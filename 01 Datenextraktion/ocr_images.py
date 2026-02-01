#!/usr/bin/env python3
"""OCR all images in the img/ subfolder.

Outputs JSON containing each detected word's text, bounding box, rotation,
center position, and estimated font size (box height in pixels).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

import pytesseract
from PIL import Image


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


def configure_tesseract(tesseract_cmd: str | None) -> None:
    resolved_cmd = tesseract_cmd or os.environ.get("TESSERACT_CMD")
    if resolved_cmd:
        pytesseract.pytesseract.tesseract_cmd = resolved_cmd
    if shutil.which(pytesseract.pytesseract.tesseract_cmd) is None:
        raise SystemExit(
            "Tesseract executable not found. Install tesseract or provide the path via "
            "--tesseract-cmd or the TESSERACT_CMD environment variable."
        )
    try:
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError as exc:
        raise SystemExit(
            "Tesseract is not available. Install it or provide the path via "
            "--tesseract-cmd or the TESSERACT_CMD environment variable."
        ) from exc


def detect_orientation(image: Image.Image) -> int:
    osd = pytesseract.image_to_osd(image)
    for line in osd.splitlines():
        if "Rotate" in line:
            _, value = line.split(":")
            return int(value.strip())
    return 0


def extract_words(image: Image.Image, rotation: int) -> list[dict[str, object]]:
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    words: list[dict[str, object]] = []
    for i in range(len(data["text"])):
        text = data["text"][i].strip()
        if not text:
            continue
        left = int(data["left"][i])
        top = int(data["top"][i])
        width = int(data["width"][i])
        height = int(data["height"][i])
        words.append(
            {
                "text": text,
                "rotation": rotation,
                "position": {
                    "left": left,
                    "top": top,
                    "right": left + width,
                    "bottom": top + height,
                    "center_x": left + width / 2,
                    "center_y": top + height / 2,
                },
                "font_size": height,
                "confidence": float(data["conf"][i]),
            }
        )
    return words


def iter_images(folder: Path) -> list[Path]:
    return sorted(
        [path for path in folder.iterdir() if path.suffix.lower() in SUPPORTED_EXTENSIONS]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run OCR on images in img/. ")
    parser.add_argument(
        "--img-dir",
        default="img",
        help="Directory containing images (default: img)",
    )
    parser.add_argument(
        "--output",
        default="ocr_output.json",
        help="Output JSON path (default: ocr_output.json)",
    )
    parser.add_argument(
        "--tesseract-cmd",
        help="Path to the tesseract executable (or set TESSERACT_CMD).",
    )
    args = parser.parse_args()

    configure_tesseract(args.tesseract_cmd)

    img_dir = Path(args.img_dir)
    if not img_dir.is_dir():
        raise SystemExit(f"Image directory not found: {img_dir}")

    result: dict[str, object] = {"images": []}
    for image_path in iter_images(img_dir):
        image = Image.open(image_path)
        rotation = detect_orientation(image)
        words = extract_words(image, rotation)
        result["images"].append(
            {
                "file": str(image_path),
                "rotation": rotation,
                "words": words,
            }
        )

    output_path = Path(args.output)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Wrote OCR results to {output_path}")


if __name__ == "__main__":
    main()

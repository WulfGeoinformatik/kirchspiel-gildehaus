# Krichspiel Gildehaus

## OCR setup

The OCR workflow in `01 Datenextraktion/ocr_images.py` depends on the Tesseract
binary. Install it for your platform and ensure it is discoverable in `PATH`, or
pass the executable path explicitly:

```bash
python "01 Datenextraktion/ocr_images.py" \
  --img-dir "01 Datenextraktion/img" \
  --output ocr_output.json \
  --tesseract-cmd /usr/bin/tesseract
```

You can also set the `TESSERACT_CMD` environment variable instead of passing the
flag.

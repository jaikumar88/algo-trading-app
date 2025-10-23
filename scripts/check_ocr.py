import shutil
import traceback
from pathlib import Path
print('CWD:', Path('.').resolve())
print('tesseract on PATH:', shutil.which('tesseract'))
try:
    import pytesseract
    from PIL import Image
    print('pytesseract imported OK')
    try:
        ver = getattr(pytesseract, 'get_tesseract_version', None)
        print('pytesseract.get_tesseract_version ->', ver() if ver else 'N/A')
    except Exception as e:
        print('could not get tesseract version:', e)
    imgs = list(Path('received_images').glob('*'))
    print('found images:', imgs)
    if imgs:
        f = imgs[0]
        print('trying OCR on:', f)
        try:
            txt = pytesseract.image_to_string(Image.open(f))
            print('\n----- OCR OUTPUT START -----\n')
            print(txt)
            print('\n----- OCR OUTPUT END -----\n')
        except Exception:
            print('OCR failed with exception:')
            traceback.print_exc()
    else:
        print('No images found in received_images/. Place an image there to test OCR.')
except Exception:
    print('pytesseract or PIL not available or import failed')
    traceback.print_exc()

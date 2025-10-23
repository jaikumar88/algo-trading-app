from pathlib import Path
import pytest
from PIL import Image
import easyocr

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.gif'}


def _collect_image_paths():
    p = Path('received_images')
    imgs = [x for x in p.glob('*') if x.suffix.lower() in IMAGE_EXTS]
    return imgs


@pytest.mark.skipif(not Path('received_images').exists(), reason='no received_images folder')
def test_easyocr_on_received_images():
    imgs = _collect_image_paths()
    print('cwd', Path('.').resolve())
    print('found images', imgs)
    if not imgs:
        pytest.skip('no image files to test')

    reader = easyocr.Reader(['en'], gpu=False)
    for p in imgs:
        print('testing', p)
        res = reader.readtext(str(p), detail=0)
        print('easyocr found lines:', len(res))
        # ensure it returns a list
        assert isinstance(res, list)
        # at least zero-length allowed; don't be strict about OCR quality in CI

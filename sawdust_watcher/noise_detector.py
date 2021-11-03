# stdlib
from pathlib import Path

# external
import cv2 as cv

data_path = Path("sawdust_watcher/data")
output_path = Path("sawdust_watcher/output")
image_a_path = data_path / "test_coins_a.jpg"
image_b_path = data_path / "test_coins_b.jpg"


def detect_sawdust(img_path):
    output_path.mkdir(parents=True, exist_ok=True)
    img = cv.imread(filename=str(img_path), flags=cv.IMREAD_COLOR)
    if img is None:
        raise ValueError("Image failed to load.")

    scale = 0.15
    dim = (int(img.shape[1] * scale), int(img.shape[0] * scale))
    # resize image
    img = cv.resize(img, dim, interpolation=cv.INTER_AREA)
    cv.imwrite(filename=str(output_path / "original.png"), img=img)

    # denoising
    img_denoised = cv.fastNlMeansDenoisingColored(
        img, dst=None, h=10, hColor=10, templateWindowSize=7, searchWindowSize=21
    )
    cv.imwrite(filename=str(output_path / "denoised.png"), img=img_denoised)

    img_diff = cv.subtract(img_denoised, img)
    cv.imwrite(filename=str(output_path / "difference.png"), img=img_diff)

    img_gray = cv.cvtColor(img_diff, cv.COLOR_BGR2GRAY)
    cv.imwrite(filename=str(output_path / "grayscale.png"), img=img_gray)
    print(img_gray.shape)
    print(img_gray.dtype)

    ret, img_thresh = cv.threshold(
        img_gray, 120, 255, cv.THRESH_BINARY + cv.THRESH_OTSU
    )

    cv.imwrite(filename=str(output_path / "threshold.png"), img=img_thresh)


def calculate_coverage():
    pass


if __name__ == "__main__":
    detect_sawdust(image_b_path)

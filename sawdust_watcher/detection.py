# external
import cv2 as cv
import numpy as np


def load_image(img_path):
    """Read a color image from specified path into numpy array.

    Args:
        img_path (str, pathlib.Path): The path to image file.

    Raises:
        ValueError: Image failed to load.

    Returns:
        numpy.ndarray: Image array.
    """
    img = cv.imread(filename=str(img_path), flags=cv.IMREAD_COLOR)
    if img is None:
        raise ValueError("Image failed to load.")

    return img


def white_pixel_ratio(img):
    """Calculates the ratio of white pixels to the total number of pixels in an image.

    Args:
        img (numpy.ndarray): Image array.
    """
    return np.sum(img == 255) / img.size


def rescale_image(img, scale):
    """Resize an image to a specified scale.

    Args:
        img (numpy.ndarray): Image to resize.
        scale (float): Scaling factor.

    Returns:
        numpy.ndarray: Rescaled image.
    """
    dim = (int(img.shape[1] * scale), int(img.shape[0] * scale))
    img = cv.resize(img, dim, interpolation=cv.INTER_AREA)

    return img


def write_image(img, output_path):
    """Save an image to disk.

    Args:
        img (numpy.ndarray): The image array to save.
        output_path (str, pathlib.Path): The path to save image to.

    Returns:
        bool: True if the image was successfully saved, False otherwise.
    """
    return cv.imwrite(filename=str(output_path), img=img)


def detect(img):
    """Detect sawdust coverage in an image.

    The approach taken involves the use of a denoising filter to act as a swadust
    particle segmentator. The image processing pipeline is as follows:
    1) Denoise the image.
    2) Find the differnce between the original image and the denoised image.
        (ie. the noise, aka sawdust)
    3) Convert image to grayscale.
    4) Threshold the image to binary.
    5) Calculate ratio of white pixels to total pixels (aka sawdust coverage).

    Args:
        img (np.ndarray): The image to be analysed.

    Returns:
        (float): Sawdust coverage ratio.
    """
    # denoising
    img_denoised = cv.fastNlMeansDenoisingColored(
        img, dst=None, h=10, hColor=10, templateWindowSize=7, searchWindowSize=21
    )

    # differencing
    img_diff = cv.subtract(img_denoised, img)

    # grayscale conversion
    img_gray = cv.cvtColor(img_diff, cv.COLOR_BGR2GRAY)

    # thresholding
    _, img_thresh = cv.threshold(img_gray, 120, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

    # ratio
    ratio = white_pixel_ratio(img_thresh)

    return ratio

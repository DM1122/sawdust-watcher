"""Detection methods for sawdust watcher."""
# stdlib
import logging

# external
import cv2 as cv
import numpy as np

LOG = logging.getLogger(__name__)


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


def write_image(img, output_path):
    """Save an image to disk.

    Args:
        img (numpy.ndarray): The image array to save.
        output_path (str, pathlib.Path): The path to save image to.

    Returns:
        bool: True if the image was successfully saved, False otherwise.
    """
    result = cv.imwrite(filename=str(output_path), img=img)

    if not result:
        raise ValueError("Image failed to save.")


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


def white_pixel_ratio(img):
    """Calculates the ratio of white pixels to the total number of pixels in an image.

    Args:
        img (numpy.ndarray): Image array.
    """
    return np.sum(img == 255) / img.size


def detect(img, noise_size=11, threshold=32, morph_size=5, interactive=False):
    """Detect sawdust coverage in an image.

    The technique used involves the use of a denoising filter to act as a sawdust
    particle segmentator. The image processing pipeline is as follows:
    1. Denoise the image.
    2. Find the difference between the original image and the denoised image. This
        effectivly isolates the noise (dust).
    3. Convert image to grayscale.
    4. Threshold the image.
    5. Apply a morphological closing operation to collect disparate particles.
    6. Calculate ratio of white pixels to total pixels (dust coverage).

    Args:
        img (numpy.ndarray): The image to be analysed.
        noise_size (int): The size of the denoising filter kernal. Must be odd.
            Defaults to 11.
        threshold (int): The threshold value for the image. Must be between 0 and 255.
            Defaults to 32.
        morph_size (int): The size of the morphological closing kernal. Must be odd.
            Defaults to 5.
        interactive (bool): If True, images will be previewed at each step in the
            pipeline. Defaults to False.

    Returns:
        ratio (float): Sawdust coverage ratio.
        img_pipe (dict): Dictionary containing images at each step in the pipeline.
    """

    assert noise_size % 2 != 0, "Noise kernal size must be an odd number."
    assert 0 <= threshold <= 255, "Threshold must be between 0 and 255."
    assert morph_size % 2 != 0, "Morphological kernel size must be an odd number."

    img_pipe = {}
    img_pipe["original"] = img

    # denoise
    img_denoise = cv.medianBlur(img, noise_size)
    img_pipe["denoise"] = img_denoise
    if interactive:
        cv.imshow("Denoise", img_denoise)
        cv.waitKey(0)

    # difference
    img_diff = cv.subtract(img, img_denoise)
    img_pipe["difference"] = img_diff
    if interactive:
        cv.imshow("Difference", img_diff)
        cv.waitKey(0)

    # grayscale
    img_gray = cv.cvtColor(img_diff, cv.COLOR_BGR2GRAY)
    img_pipe["grayscale"] = img_gray
    if interactive:
        cv.imshow("Grayscale", img_gray)
        cv.waitKey(0)

    # threshold
    _, img_thresh = cv.threshold(img_gray, threshold, 255, cv.THRESH_BINARY)
    img_pipe["threshold"] = img_thresh
    if interactive:
        cv.imshow("Threshold", img_thresh)
        cv.waitKey(0)

    # morphological transformation
    kernal = np.ones((morph_size, morph_size), np.uint8)
    img_morph = cv.morphologyEx(img_thresh, cv.MORPH_CLOSE, kernal, iterations=3)
    img_pipe["morph"] = img_morph
    if interactive:
        cv.imshow("Morph", img_morph)
        cv.waitKey(0)

    # ratio
    ratio = white_pixel_ratio(img_morph)

    return ratio, img_pipe

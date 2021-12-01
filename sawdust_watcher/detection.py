"""Detection methods for sawdust watcher."""
# stdlib
import logging
import time

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

    if result == False:
        raise ValueError("Image failed to save.")


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


def detect_contours(img):

    # convert to gray to be compatible with cv.findContours()
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    cv.imshow("grayscale", img_gray)
    cv.waitKey(0)

    # threshold
    thresh, img_thresh = cv.threshold(img_gray, 127, 255, cv.THRESH_BINARY)
    # img_thresh = cv.adaptiveThreshold(img_gray, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 255, 0)
    cv.imshow(f"threshold ({thresh})", img_thresh)
    cv.waitKey(0)

    # contours
    contours, hierarchy = cv.findContours(
        img_thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE
    )
    img_contours = cv.drawContours(
        img, contours, -1, (0, 255, 0), 3
    )  # draw all contours by passing -1 as the contour index
    cv.imshow("contours", img_contours)
    cv.waitKey(0)


def detect_blobs(img):

    # convert to gray
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    cv.imshow("Grayscale", img_gray)
    cv.waitKey(0)

    img_neg = cv.bitwise_not(img_gray)
    cv.imshow("Negative", img_neg)
    cv.waitKey(0)

    # Setup SimpleBlobDetector parameters.
    params = cv.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 100
    params.maxThreshold = 255

    # Filter by Area.
    params.filterByArea = False
    params.minArea = 1500

    # Filter by Circularity
    params.filterByCircularity = False
    params.minCircularity = 0.1

    # Filter by Convexity
    params.filterByConvexity = False
    params.minConvexity = 0.87

    # Filter by Inertia
    params.filterByInertia = False
    params.minInertiaRatio = 0.01

    # Create a detector with the parameters
    detector = cv.SimpleBlobDetector_create(params)

    # Detect blobs
    keypoints = detector.detect(img_neg)

    # Draw detected blobs as red circles.
    # cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures
    # the size of the circle corresponds to the size of blob
    img_blobs = cv.drawKeypoints(
        img,
        keypoints,
        np.array([]),
        (0, 0, 255),
        cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
    )

    # Show blobs
    write_image(img=img_blobs, output_path="output/blobs.png")
    cv.imshow("Keypoints", img_blobs)
    cv.waitKey(0)


def detect_dust(img):
    img_median = cv.medianBlur(img, 11)  # tune this value
    cv.imshow("Median", img_median)
    cv.waitKey(0)

    img_diff = cv.subtract(img, img_median)
    cv.imshow("Difference", img_diff)
    cv.waitKey(0)

    img_gray = cv.cvtColor(img_diff, cv.COLOR_BGR2GRAY)
    cv.imshow("Grayscale", img_gray)
    cv.waitKey(0)

    _, img_thresh = cv.threshold(img_gray, 32, 255, cv.THRESH_BINARY)  # tune this value
    cv.imshow("Threshold", img_thresh)
    cv.waitKey(0)

    kernal = np.ones((5, 5), np.uint8)
    img_closing = cv.morphologyEx(img_thresh, cv.MORPH_CLOSE, kernal, iterations=3)
    cv.imshow("Closing", img_closing)
    cv.waitKey(0)


def detect(img, output_path, thresh_lower=128, thresh_upper=255):
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
        img (numpy.ndarray): The image to be analysed.
        output_path (str, pathlib.Path): The path to save the image to.
        thresh (float): The threshold value for the segmented image.

    Returns:
        (float): Sawdust coverage ratio.
    """
    # denoising
    img_denoised = cv.fastNlMeansDenoisingColored(
        img, dst=None, h=1, hColor=10, templateWindowSize=7, searchWindowSize=21
    )

    # differencing
    img_diff = cv.subtract(img_denoised, img)

    # grayscale conversion
    img_gray = cv.cvtColor(img_diff, cv.COLOR_BGR2GRAY)

    # thresholding
    _, img_thresh = cv.threshold(
        img_gray, thresh_lower, thresh_upper, cv.THRESH_BINARY + cv.THRESH_OTSU
    )

    # contour removal
    img_median = cv.medianBlur(img_thresh, 25)
    img_median_diff = cv.subtract(img_thresh, img_median)

    # write segmented image
    time_stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    img_path = output_path / f"{time_stamp}_segmentation.png"
    write_image(img=img_median_diff, output_path=img_path)

    # ratio
    ratio = white_pixel_ratio(img_thresh)

    return ratio

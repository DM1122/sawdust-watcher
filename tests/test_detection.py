"""Tests for detection functionality."""
# stdlib
import logging
from pathlib import Path

# external
import numpy as np

# project
from sawdust_watcher import detection

data_path = Path("data")
output_path = Path("output")

LOG = logging.getLogger(__name__)


def test_white_pixel_ratio():
    """Test the white pixel ratio function."""
    LOG.info("Computing white pixel ratio")

    img = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]])
    LOG.info(f"Test image array:\n{img}")

    ratio = detection.white_pixel_ratio(img)
    LOG.info(f"Ratio: {ratio}")

    assert ratio == 1 / 3


def test_load_img():
    """Test the image loading function."""
    img_path = "data/test_coins_a.jpg"

    LOG.info(f"Loading image '{img_path}'")
    img = detection.load_image(img_path)

    LOG.info(f"Type:\t{type(img)}")
    LOG.info(f"Shape:\t{img.shape}")
    LOG.info(f"Size:\t{img.size}")
    LOG.info(f"Dtype:\t{img.dtype}")


def test_write_image():
    """Test the image writing function."""
    output_img_path = output_path / "test_img.png"
    img = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]])

    LOG.info(f"Writing image to '{output_img_path}'")
    assert detection.write_image(img=img, output_path=output_img_path) is True


def test_detect():
    """Test the detection function."""
    img_path = data_path / "test_coins_a.jpg"

    img = detection.load_image(img_path)
    img = detection.rescale_image(img=img, scale=0.1)

    LOG.info(f"Detecting sawdust in '{img_path}'")
    ratio = detection.detect(img)

    LOG.info(f"Sawdust coverage: {round(ratio*100,2)}%")

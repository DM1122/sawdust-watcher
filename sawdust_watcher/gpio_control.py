"""Methods for controlling GPIO on raspberry pi."""
# stdlib
import time

# external
import numpy as np
import picamera


def flash_led(led):
    """Flash the given LED once.

    Args:
        led (gpiozero.LED): The led to flash.
    """
    led.on()
    time.sleep(0.5)
    led.off()
    time.sleep(0.5)


def grab_frame(resolution=(720, 480)):
    """Capture a frame from the camera and save to disk.

    Args:
        camera (gpiozero.PiCamera): The camera object.
        output_path (pathlib.Path): Output path in which to save the image.
        resolution (tuple): The resolution of the image to capture.
            Defaults to (720,480).

    Returns:
        (numpy.ndarray): The numpy array containing the image data.
    """

    with picamera.PiCamera() as camera:
        camera.resolution = resolution
        camera.start_preview()

        time.sleep(3)  # warmup camera

        img = np.empty((resolution[1], resolution[0], 3), dtype=np.uint8)
        camera.capture(img, "bgr")

    return img

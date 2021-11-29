"""Methods for controlling GPIO on raspberry pi."""
# stdlib
import time

# external
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


def grab_frame(output_path):
    """Capture a frame from the camera and save to disk.

    Args:
        camera (gpiozero.PiCamera): The camera object.
        output_path (pathlib.Path): Output path in which to save the image.

    Returns:
        str: The path to the saved image.
    """
    output_path.mkdir(parents=True, exist_ok=True)

    with picamera.PiCamera() as camera:
        camera.start_preview()
        time.sleep(3)  # camera warmup
        time_stamp = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        img_path = output_path / f"{time_stamp}.png"
        camera.capture(str(img_path))

    return img_path

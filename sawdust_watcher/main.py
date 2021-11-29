"""Main runtime code for sawdust watcher prototype."""
# stdlib
import logging
import time
from pathlib import Path

# external
from gpiozero import LED, Button, Buzzer
from picamera import PiCamera

try:  # import as package
    # project
    from sawdust_watcher import detection, gpio_control
except ImportError:  # import as standalone
    # external
    import detection
    import gpio_control


# region config
scan_interval = 5  # sec
coverage_threshold_percent = 5  # %
# endregion

# region GPIO
led = LED(5)
button = Button(4)
buzzer = Buzzer(27)

camera = PiCamera()
camera.resolution = (3280, 2464)
# endregion


def run(output_path):
    """Run the main loop.

    Args:
        output_path (str): The output path for logging and images.
    """
    output_path = Path(output_path)

    # region logging config
    time_stamp = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    log_path = output_path / f"{time_stamp}"
    log_path.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        handlers=[
            logging.FileHandler(
                (log_path / Path(__file__).stem).with_suffix(".log"),
                "w",
                encoding="utf-8",
            )
        ],
        format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )
    LOG = logging.getLogger(__name__)
    # endregion

    LOG.info("Starting sawdust watcher script")

    time_start = time.time()
    alarm_active = False

    while True:

        if not alarm_active:
            if (time.time() - time_start) % scan_interval == 0:
                LOG.info("Scanning area for sawdust")

                img_path = gpio_control.grab_frame(
                    camera=camera, output_path=output_path / "captures"
                )
                detection.load_image(img_path)
                coverage_ratio = detection.detect(img_path)
                LOG.info(f"Sawdust detected at {round(coverage_ratio*100,2)}% coverage")

                if coverage_ratio >= coverage_threshold_percent / 100:
                    LOG.info("Sawdust coverage exceeds threshold. Activating alarm")
                    alarm_active = True
                    led.on()
                    buzzer.on()

        if button.is_pressed:
            LOG.info("Button pressed. Resetting alarm")
            alarm_active = False
            time_start = time.time()
            buzzer.off()
            led.off()


if __name__ == "__main__":
    run(output_path="output")

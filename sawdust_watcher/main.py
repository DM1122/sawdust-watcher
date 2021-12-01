"""Main runtime code for sawdust watcher prototype.

Usage:
    main.py --log=<path> [--config=<path>]

Options:
    --log=<path>  The output path for logs and images.
    --config=<path>  The config file path. [default: config.ini]
"""

# stdlib
import configparser
import logging
import time
from pathlib import Path

# external
from docopt import docopt
from gpiozero import LED, Button, Buzzer

try:  # import as package
    # project
    from sawdust_watcher import detection, gpio_control
except ModuleNotFoundError:  # import as standalone
    # external
    import detection
    import gpio_control


def run(output_path, config):
    """Run the main loop.

    Args:
        output_path (str): The output path for logging and images.
        config (dict): The program configuration.
    """
    output_path = Path(output_path).expanduser()  # expands ~ to home directory (unix)

    # region logging config
    log_time_stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_path = output_path / "logs"
    log_path.mkdir(parents=True, exist_ok=True)
    log_file_path = (log_path / log_time_stamp).with_suffix(".log")
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(filename=log_file_path, mode="w", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    LOG = logging.getLogger(__name__)
    # endregion

    # region gpio instantiation
    led = LED(config.getint("gpio", "led"))
    buzzer = Buzzer(config.getint("gpio", "buzzer"))
    button = Button(config.getint("gpio", "button"))
    # endregion

    LOG.info("Starting sawdust watcher script")

    time_start = time.time()
    alarm_active = False

    while True:

        if not alarm_active:
            if time.time() >= time_start + config.getint("op", "scan_interval"):
                LOG.info("Scanning area for sawdust")

                img = gpio_control.grab_frame(
                    eval(config.get("op", "resolution")),
                )
                coverage_ratio, img_pipe = detection.detect(
                    img=img,
                    noise_size=config.getint("detect", "noise_size"),
                    threshold=config.getint("detect", "threshold"),
                    morph_size=config.getint("detect", "morph_size"),
                )

                time_stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                for key, value in img_pipe.items():
                    detection.write_image(
                        img=value,
                        output_path=(
                            output_path / "images" / time_stamp / key
                        ).with_suffix(".png"),
                    )

                LOG.info(f"Sawdust detected at {round(coverage_ratio*100,2)}% coverage")

                if (
                    coverage_ratio
                    >= config.getfloat("op", "coverage_threshold_percent") / 100
                ):
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
    args = docopt(__doc__)

    config = configparser.ConfigParser()
    config.read(args["--config"])

    run(output_path=args["--log"], config=config)

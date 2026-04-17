
from pathlib import Path

from robot.robots.basic_car import BasicCar
from robot.utils.config import load_config

# config file to load from /config
config_file = "test_config.yaml"

# Create path and load config
CONFIG_PATH = Path(__file__).parent.parent / "config" / config_file
cfg = load_config(CONFIG_PATH)

robot = BasicCar(cfg)
robot.run()

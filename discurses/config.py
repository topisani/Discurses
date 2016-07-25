import yaml
import os

CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~"), ".config", "discurses.yaml")

with open(CONFIG_FILE_PATH, 'r') as file:
    table = yaml.load(file)

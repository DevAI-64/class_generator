"""This is an exemple for using librairie."""

import configparser as cfp
import os

from pydash import get  # type: ignore
from src.gen_class import GenClass # type: ignore
from src.utils import Utils  # type: ignore


if __name__ == "__main__":

    Utils.gen_pickle_files()

    try:
        for file_config in os.listdir("./config"):
            config = cfp.ConfigParser()
            config.read(f"./config/{file_config}")
            GenClass(
              get(config, "class_config.name_file"),
              get(config, "attributes"),
              get(config, "methods")
            )
    except Exception as err:
        print(f"ERROR: {err}")
    input("Press Enter for quit...")

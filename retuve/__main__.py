"""
Retuve

Please see the README.md for more information on how to use this package.
"""

import os
from typing import Literal

import fire
import uvicorn

from retuve.app import app
from retuve.app.helpers import app_init, load_keyphrase_config
from retuve.batch import run_batch, run_single
from retuve.keyphrases.config import Config
from retuve.logs import ulogger
from retuve.trak.main import run_all_state_machines

LOCAL_DIR = os.getcwd()


def process_file_path(file_path: str, local_dir: str, name: str):
    """
    Process the file path.

    :param file_path: The file path.
    :param local_dir: The local directory.
    :param name: The name of the file path.
    """
    if not file_path:
        raise ValueError(f"{name} is required")
    if not os.path.exists(file_path):
        raise ValueError(f"{name} does not exist.")
    if file_path.startswith("./"):
        file_path = local_dir + file_path[1:]
    return file_path


def main(
    task: Literal["trak", "batch", "single"] = "trak",
    keyphrase_file: str = None,
    keyphrase: str = None,
    file_name: str = None,
    savedir: str = None,
):
    """
    Run the retuve package.

    :param task: The task to run.
    :param keyphrase_file: The keyphrase file.
    :param keyphrase: The keyphrase.
    :param file_name: The file name.
    :param savedir: The save directory
    """

    load_keyphrase_config(keyphrase_file)

    if not keyphrase and task == "trak":
        app_init(app)
        run_all_state_machines()
        uvicorn.run(app, host="0.0.0.0", port=8000)
        return

    config = Config.get_config(keyphrase)

    ulogger.info(f"Running on device: {config.device}")

    keyphrase_file = process_file_path(
        keyphrase_file, LOCAL_DIR, "keyphrase_file"
    )

    ulogger.info(f"Using mode_func: {config.batch.mode_func.__name__}")
    ulogger.info(f"Using keyphrase_file: {keyphrase_file}")

    if task == "single":
        run_single(config, file_name, local_savedir=savedir)

    elif task == "batch":
        run_batch(config)


if __name__ == "__main__":
    fire.Fire(main)

"""
Helper Functions for launching the Retuve Web App
"""

import importlib
import logging
import os
import sys

import fastapi
from fastapi import File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from retuve.keyphrases.config import Config
from retuve.logs import ulogger
from retuve.trak.data import database_init
from retuve.typehints import GeneralModeFuncType
from retuve.utils import RETUVE_DIR

# create a temp dir
TMP_RESULTS_DIR = f"/tmp/retuve_api_results/"

API_RESULTS_URL_ACCESS = "api_results"
TMP_RESULTS_URL_ACCESS = "/results"

web_templates = Jinja2Templates(directory=f"{RETUVE_DIR}/app/static")


class AppConfigInfo:
    """
    Helper config for injecting config information into the app object directly.
    """

    def __init__(
        self, mode_func: GeneralModeFuncType, hippa_logger: logging.Logger
    ):
        self.mode_func = mode_func
        self.hippa_logger = hippa_logger


def app_init(app: fastapi.FastAPI):
    """
    Initialize the FastAPI app with the necessary configurations.

    :param app: The FastAPI app object.
    """

    app.config = {}
    app.instance_id_cache = None
    app.model_response_cache = None
    origins = []

    for _, config in Config.get_configs():
        # create batch and results dirs if they don't exist
        dirs = [TMP_RESULTS_DIR, config.api.savedir]
        for dir in dirs:
            if not os.path.exists(dir):
                ulogger.info(f"Creating directory: {dir}")
                os.makedirs(dir)

        database_init(config.api.db_path)

        # mount the video file
        app.mount(
            TMP_RESULTS_URL_ACCESS,
            StaticFiles(directory=TMP_RESULTS_DIR),
            name="results",
        )
        app.mount(
            f"/{API_RESULTS_URL_ACCESS}/{config.name}",
            StaticFiles(directory=config.api.savedir),
            name=API_RESULTS_URL_ACCESS,
        )

        app.mount(
            "/static",
            StaticFiles(directory=f"{RETUVE_DIR}/app/static"),
            name="static",
        )

        origins = [config.api.url, config.api.url.replace("http://", "")]

        mode_func = config.batch.mode_func

        origins.extend(config.api.origins)

        hippa_logger = logging.getLogger("hippa")
        hippa_logger.setLevel(logging.INFO)
        handler = logging.FileHandler(config.api.hippa_logging_file)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        hippa_logger.addHandler(handler)

        app.config[config.name] = AppConfigInfo(
            mode_func=mode_func,
            hippa_logger=hippa_logger,
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def analyze_validation(file: File, keyphrase: str, api_token: str):
    """
    Validate the file and keyphrase before analyzing it.

    :param file: The file to be analyzed.
    :param keyphrase: The keyphrase to be used for analysis.
    :param api_token: The API token for the keyphrase.

    :raises HTTPException: If the file or keyphrase is invalid.
    """
    if not Config.keyphrase_exists(keyphrase.lower()):
        raise HTTPException(
            status_code=400,
            detail=f"Keyphrase {keyphrase} is not a valid keyphrase.",
        )

    # Validate file type for .dcm
    if file.content_type is None or not (
        file.filename.endswith(".dcm") or file.filename.endswith(".jpg")
    ):
        raise HTTPException(
            status_code=400,
            detail=f"File {file.filename} is not a valid DICOM file.",
        )

    config = Config.get_config(keyphrase)

    if config.api.api_token:
        if api_token != config.api.api_token:
            raise HTTPException(
                status_code=400,
                detail="Invalid API token provided.",
            )


def load_keyphrase_config(keyphrase_file: str):
    """
    Load the keyphrase configuration from the given file.

    :param keyphrase_file: The file containing the keyphrase configuration.

    :raises ValueError: If the file does not exist.
    """

    # Check if the file exists
    if not os.path.exists(keyphrase_file):
        raise ValueError(f"{keyphrase_file} does not exist.")

    # Remove the file extension if it's a Python file
    if keyphrase_file.endswith(".py"):
        keyphrase_file = keyphrase_file[:-3]

    # Convert the file path to a module path by extracting the directory path and module name
    dir_path, module_name = keyphrase_file.rsplit("/", 1)

    # Add the directory path to sys.path if not already included
    if dir_path not in sys.path:
        sys.path.append(dir_path)

    # Import the module using its name
    module = importlib.import_module(module_name)
    setup_function = getattr(module, "setup")

    setup_function()

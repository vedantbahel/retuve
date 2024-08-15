"""
The UI routes for the Retuve Web Interface.
"""

import os
import re
import shutil
from tempfile import mkdtemp

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from retuve.app.helpers import API_RESULTS_URL_ACCESS, web_templates
from retuve.keyphrases.config import Config
from retuve.trak.data import extract_files

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def web(request: Request):
    """
    Open the main page of the Retuve Web Interface.
    """
    keyphrases = [keyphrase for keyphrase in Config.configs.keys()]

    return web_templates.TemplateResponse(
        f"index.html",
        {
            "request": request,
            "keyphrases": keyphrases,
        },
    )


@router.get("/ui/{keyphrase}", response_class=HTMLResponse)
async def web_keyphrase(request: Request, keyphrase: str):
    """
    Open the page for a specific keyphrase.
    """

    config = Config.get_config(keyphrase)
    files_data = extract_files(config.api.db_path)

    return web_templates.TemplateResponse(
        f"main.html",
        {
            "request": request,
            "files": files_data,
            "hip_mode": config.batch.hip_mode,
            "keyphrase": keyphrase,
            "url": config.api.url,
        },
    )


@router.get("/ui/upload/", response_class=HTMLResponse)
async def upload_form(request: Request):
    """
    Open the upload form for the Retuve Web Interface.
    """

    keyphrases = [keyphrase for keyphrase in Config.configs.keys()]

    return web_templates.TemplateResponse(
        f"upload.html",
        {
            "request": request,
            "keyphrases": keyphrases,
        },
    )


@router.get("/ui/download/{keyphrase}")
async def download_files(
    request: Request, keyphrase: str, pattern: str = None
):
    """
    Download files from the Retuve Web Interface.
    """

    if not pattern:
        raise HTTPException(status_code=400, detail="Pattern is required")

    config = Config.get_config(keyphrase)
    savedir = config.api.savedir

    # Create a temporary directory to hold the folders
    temp_dir = mkdtemp()

    # Find all folders in savedir that match the pattern
    # Copy each matching folder to the temporary directory
    for folder in os.listdir(savedir):
        if re.search(pattern, folder) and os.path.isdir(
            os.path.join(savedir, folder)
        ):
            source_folder = os.path.join(savedir, folder)
            destination_folder = os.path.join(temp_dir, folder)
            shutil.copytree(source_folder, destination_folder)

    # Create a zip file of the temporary directory
    zip_file = os.path.join(savedir, f"{pattern}.zip")
    shutil.make_archive(zip_file[:-4], "zip", temp_dir)

    zip_file_url = (
        f"{config.api.url}/{API_RESULTS_URL_ACCESS}/{keyphrase}/{pattern}.zip"
    )

    # Optionally, remove the temporary directory after creating the zip file
    shutil.rmtree(temp_dir)

    return web_templates.TemplateResponse(
        "download.html",
        {
            "request": request,
            "zip_file_url": zip_file_url,
            "keyphrase": keyphrase,
        },
    )


@router.get("/ui/live/", response_class=HTMLResponse)
async def live_ui(request: Request):
    """
    Open the live page of the Retuve Web Interface.
    """

    keyphrases = [keyphrase for keyphrase in Config.configs.keys()]

    return web_templates.TemplateResponse(
        f"live.html",
        {
            "request": request,
            "keyphrases": keyphrases,
        },
    )

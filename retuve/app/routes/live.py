# Copyright 2024 Adam McArthur
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The API for Retuve Live
"""

import asyncio
import logging
import os
import shutil
import traceback
from contextlib import asynccontextmanager

from fastapi import APIRouter, Form, HTTPException, Request

from retuve.app.classes import LiveResponse
from retuve.app.helpers import RESULTS_DIR, RESULTS_URL_ACCESS
from retuve.app.utils import (
    get_sorted_dicom_images,
    save_dicom_and_get_results,
    save_results,
    validate_api_token,
)
from retuve.keyphrases.config import Config

logging.getLogger("httpx").setLevel(logging.CRITICAL)


class NoDicomFoundError(Exception):
    pass


# Create a global queue for DICOM processing
dicom_processing_queue = asyncio.Queue()

processed_instance_ids = set()


async def process_dicom_queue():
    """
    Background task to process queued DICOM files and save results in `live_savedir`.
    """
    while True:
        dicom_data = await dicom_processing_queue.get()
        instance_id, dicom_content, config, live_savedir = dicom_data

        if instance_id in processed_instance_ids:
            logging.info(f"Skipping already processed DICOM: {instance_id}")
            dicom_processing_queue.task_done()
            continue

        try:

            live_batchdir = config.batch.datasets[0]

            # Define the directory for saving results
            result_dir = f"{live_savedir}/{instance_id}"

            # check if metrics already exists
            if os.path.exists(f"{result_dir}/metrics.json"):
                logging.info(f"Skipping already processed DICOM: {instance_id}")
                dicom_processing_queue.task_done()
                continue

            # Process the DICOM
            result = await save_dicom_and_get_results(
                live_batchdir, instance_id, dicom_content, config
            )
            if not result:
                dicom_processing_queue.task_done()
                continue
            await save_results(instance_id, live_savedir, result=result)

            logging.info(
                f"Processed and saved results for DICOM: {instance_id} in {result_dir}"
            )

            processed_instance_ids.add(instance_id)

        except Exception as e:
            logging.error(
                f"Error processing DICOM {instance_id}: {traceback.format_exc()}"
            )
        finally:
            dicom_processing_queue.task_done()


async def constantly_delete_temp_dirs(config):
    """
    Background task to constantly delete temporary directories.
    """
    if not config.zero_trust:
        return

    while True:
        # Delete the temporary directory
        if os.path.exists(RESULTS_DIR):
            shutil.rmtree(RESULTS_DIR)
            os.makedirs(RESULTS_DIR, exist_ok=True)

        await asyncio.sleep(config.zero_trust_interval)


@asynccontextmanager
async def lifespan(app):
    # Create the task once the event loop is running
    task = asyncio.create_task(process_dicom_queue())
    if Config.live_config:
        task2 = asyncio.create_task(
            constantly_delete_temp_dirs(Config.live_config.name)
        )

    yield

    task.cancel()
    if Config.live_config:
        task2.cancel()


router = APIRouter(lifespan=lifespan)


@router.post(
    "/api/live/",
    response_model=LiveResponse,
    responses={
        204: {"description": "No Content - Retuve Run likely to be in progress."},
        400: {"description": "Invalid file type. Expected a DICOM file."},
        422: {"description": "No DICOM images found on the Orthanc server."},
        500: {"description": "Internal Server Error"},
    },
)
async def analyse_image(
    request: Request,
    keyphrase: str = Form(...),
):
    """
    Analyze a file with a Retuve Model based on the keyphrase provided.

    :param request: The request object.
    :param keyphrase: The keyphrase to be used for analysis.
    :raises HTTPException: If the file or keyphrase is invalid.
    """

    api_token = request.cookies.get("api_token")
    validate_api_token(api_token)
    instance_id = "Unknown"

    try:
        config = Config.get_config(keyphrase)

        if config.api.zero_trust:
            live_savedir = RESULTS_DIR
            live_batchdir = RESULTS_DIR
        else:
            live_savedir = config.api.savedir
            live_batchdir = config.batch.datasets[0]

        hippa_logger = request.app.config[config.name].hippa_logger

        # Usage example: Fetch all DICOMs and find the latest one
        dicoms, request.app.latest_time = await get_sorted_dicom_images(
            config.api.orthanc_url,
            config.api.orthanc_username,
            config.api.orthanc_password,
            latest_time=request.app.latest_time,
        )

        if dicoms:
            # Get the latest DICOM (the last one in the sorted list)
            latest_dicom, instance_id = dicoms[-1]
        else:
            raise NoDicomFoundError("No DICOM images found on the Orthanc server.")

        if request.app.instance_id_cache == instance_id and not config.api.zero_trust:
            hippa_logger.debug(
                f"Retuve Run for {instance_id} with keyphrase {keyphrase} "
                f"from host: {request.client.host} has been soft-cached."
            )
            if not request.app.model_response_cache:
                raise HTTPException(
                    status_code=204,
                )

            return request.app.model_response_cache

        request.app.instance_id_cache = instance_id

        if os.path.exists(f"{live_savedir}/{instance_id}"):

            video_path, img_path, _ = await save_results(
                instance_id, live_savedir, just_paths=True
            )

            video_path = video_path.replace(
                live_savedir, f"{RESULTS_URL_ACCESS}/{config.name}"
            )
            img_path = img_path.replace(
                live_savedir, f"{RESULTS_URL_ACCESS}/{config.name}"
            )

            request.app.model_response_cache = LiveResponse(
                file_id=instance_id,
                video_url=video_path,
                img_url=img_path,
            )

            hippa_logger.debug(
                f"Retuve Run for {instance_id} with keyphrase {keyphrase} "
                f"from host: {request.client.host} has been hard-cached."
            )

            return request.app.model_response_cache

        result = await save_dicom_and_get_results(
            live_batchdir, instance_id, latest_dicom, config
        )

        video_path, img_path, _ = await save_results(
            instance_id, live_savedir, result=result
        )

        video_path = video_path.replace(
            live_savedir, f"{RESULTS_URL_ACCESS}/{config.name}"
        )
        img_path = img_path.replace(live_savedir, f"{RESULTS_URL_ACCESS}/{config.name}")

        # Mark success in hippa logs
        hippa_logger.info(
            f"Successfully processed {instance_id} with keyphrase {keyphrase} "
            f"from host: {request.client.host}."
        )

        request.app.model_response_cache = LiveResponse(
            file_id=instance_id,
            video_url=video_path if video_path else "",
            img_url=img_path if img_path else "",
        )

        # check if there is a valid response, otherwise raise a 500 error
        if not request.app.model_response_cache:
            raise HTTPException(
                status_code=500, detail="Internal Server Error, check logs."
            )

        if config.api.zero_trust:
            return request.app.model_response_cache

        # Queue the remaining DICOMs for background processing
        for dicom, dicom_id in dicoms[:-1]:
            await dicom_processing_queue.put((dicom_id, dicom, config, live_savedir))

        return request.app.model_response_cache

    except NoDicomFoundError as e:
        # raise a 422 error
        raise HTTPException(status_code=422, detail=str(e))

    except HTTPException as http_exc:
        # Allow expected HTTP exceptions to pass through without wrapping in a 500
        raise http_exc

    except Exception as e:
        hippa_logger.error(
            f"Error in processing {instance_id} with keyphrase {keyphrase} "
            f"from host: {request.client.host}."
        )
        hippa_logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail="Internal Server Error, check logs."
        )

"""
The API for Retuve Live
"""

import logging
import traceback
from datetime import datetime

import httpx
from fastapi import APIRouter, Form, HTTPException, Request

from retuve import __version__ as retuve_version
from retuve.app.classes import Metric2D, Metric3D, ModelResponse
from retuve.app.helpers import TMP_RESULTS_DIR, TMP_RESULTS_URL_ACCESS
from retuve.funcs import retuve_run
from retuve.keyphrases.config import Config
from retuve.testdata import Cases, download_case

router = APIRouter()

logging.getLogger("httpx").setLevel(logging.CRITICAL)


class NoDicomFoundError(Exception):
    pass


@router.post(
    "/api/live/",
    response_model=ModelResponse,
    responses={
        400: {"description": "Invalid file type. Expected a DICOM file."},
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

    try:
        config = Config.get_config(keyphrase)

        hippa_logger = request.app.config[config.name].hippa_logger

        try:
            # Usage example:
            latest_dicom, instance_id = await get_latest_dicom_image(
                "http://localhost:8042", "orthanc", "orthanc"
            )

        except Exception as e:
            # Log error
            hippa_logger.error(
                f"{keyphrase} failed to process due to: {str(e)}"
            )
            raise NoDicomFoundError(
                "No DICOM images found on the Orthanc server."
            )

        # write latest_dicom to a temporary file
        with open(f"{TMP_RESULTS_DIR}/{instance_id}.dcm", "wb") as f:
            f.write(latest_dicom)

        if request.app.instance_id_cache == instance_id:
            return request.app.model_response_cache

        request.app.instance_id_cache = instance_id

        # if config does not have mode_func_kwargs_dict, set it to empty dict
        if not hasattr(config.batch, "mode_func_kwargs_dict"):
            config.batch.mode_func_kwargs_dict = {}

        result = retuve_run(
            hip_mode=config.batch.hip_mode,
            config=config,
            modes_func=config.batch.mode_func,
            modes_func_kwargs_dict=config.batch.mode_func_kwargs_dict,
            file=f"{TMP_RESULTS_DIR}/{instance_id}.dcm",
        )

        notes = ""
        metrics3d = []
        metrics2d = []
        video_path = None
        figure_path = None
        img_path = None

        if result.video_clip:
            video_path = f"{TMP_RESULTS_DIR}/{instance_id}.mp4"
            result.video_clip.write_videofile(video_path)
            video_path = video_path.replace(
                TMP_RESULTS_DIR, TMP_RESULTS_URL_ACCESS
            )

        if result.visual_3d:
            figure_path = f"{TMP_RESULTS_DIR}/{instance_id}.html"
            result.visual_3d.write_html(figure_path)
            figure_path = figure_path.replace(
                TMP_RESULTS_DIR, TMP_RESULTS_URL_ACCESS
            )

        if result.image:
            img_path = f"{TMP_RESULTS_DIR}/{instance_id}.jpg"
            result.image.save(img_path)
            img_path = img_path.replace(
                TMP_RESULTS_DIR, TMP_RESULTS_URL_ACCESS
            )

        if result.hip_datas:
            for metric in result.hip_datas.metrics:
                metrics3d.append(
                    Metric3D(
                        name=metric.name,
                        post=0 if metric.post == "N/A" else metric.post,
                        graf=0 if metric.graf == "N/A" else metric.graf,
                        ant=0 if metric.ant == "N/A" else metric.ant,
                        full=0 if metric.full == "N/A" else metric.full,
                    )
                )

            notes = str(result.hip_datas.recorded_error)

        if result.image:
            for metric in result.hip.metrics:
                metrics2d.append(
                    Metric2D(name=metric.name, value=metric.value)
                )

        # Mark success in hippa logs
        hippa_logger.info(
            f"Successfully processed {instance_id} with keyphrase {keyphrase} "
            f"from host: {request.client.host}."
        )

        request.app.model_response_cache = ModelResponse(
            notes=notes,
            metrics_3d=metrics3d,
            video_url=f"{config.api.url}{video_path}" if video_path else "",
            figure_url=f"{config.api.url}{figure_path}" if figure_path else "",
            img_url=f"{config.api.url}{img_path}" if img_path else "",
            retuve_version=retuve_version,
            keyphrase_name=config.name,
            metrics_2d=metrics2d,
        )

        # Mock response for demonstration
        return request.app.model_response_cache

    except NoDicomFoundError as e:
        # raise a 422 error
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        # print traceback to hippa logs
        hippa_logger.error(
            f"Error in processing {instance_id} with keyphrase {keyphrase} "
            f"from host: {request.client.host}."
        )
        hippa_logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail="Internal Server Error, check logs."
        )


async def get_latest_dicom_image(orthanc_url, username=None, password=None):
    """
    Gets the latest DICOM image from an Orthanc server by both acquisition date and time.

    :param orthanc_url: The base URL of the Orthanc server (e.g., http://localhost:8042).
    :param username: (Optional) Username for basic authentication.
    :param password: (Optional) Password for basic authentication.
    :return: The latest DICOM image file.
    """
    auth = (username, password) if username and password else None

    async with httpx.AsyncClient() as client:
        # Fetch the list of patients
        patients_response = await client.get(
            f"{orthanc_url}/patients", auth=auth
        )
        patients = patients_response.json()

        latest_image = None
        latest_date_time = datetime.min

        for patient_id in patients:
            # Fetch the studies for each patient
            studies_response = await client.get(
                f"{orthanc_url}/patients/{patient_id}/studies", auth=auth
            )
            studies = studies_response.json()

            for study in studies:
                study_id = study["ID"]
                # Fetch the series for each study
                series_list_response = await client.get(
                    f"{orthanc_url}/studies/{study_id}/series", auth=auth
                )
                series_list = series_list_response.json()

                for series in series_list:
                    series_id = series["ID"]
                    # Fetch the instances for each series
                    instances_response = await client.get(
                        f"{orthanc_url}/series/{series_id}/instances",
                        auth=auth,
                    )
                    instances = instances_response.json()

                    for instance in instances:
                        instance_id = instance["ID"]
                        # Fetch the metadata for each instance
                        instance_metadata_response = await client.get(
                            f"{orthanc_url}/instances/{instance_id}/simplified-tags",
                            auth=auth,
                        )
                        instance_metadata = instance_metadata_response.json()

                        # Check the acquisition date and time
                        acquisition_date_str = instance_metadata.get(
                            "AcquisitionDate"
                        )
                        acquisition_time_str = instance_metadata.get(
                            "AcquisitionTime"
                        )

                        if acquisition_date_str and acquisition_time_str:
                            acquisition_date_time_str = (
                                acquisition_date_str
                                + acquisition_time_str.split(".")[0]
                            )  # to avoid microseconds
                            acquisition_date_time = datetime.strptime(
                                acquisition_date_time_str, "%Y%m%d%H%M%S"
                            )

                            if acquisition_date_time > latest_date_time:
                                latest_date_time = acquisition_date_time
                                latest_image = instance_id

        if latest_image:
            # Download the latest DICOM image
            latest_image_response = await client.get(
                f"{orthanc_url}/instances/{latest_image}/file", auth=auth
            )
            return latest_image_response.content, latest_image
        else:
            raise ValueError("No DICOM images found on the Orthanc server.")

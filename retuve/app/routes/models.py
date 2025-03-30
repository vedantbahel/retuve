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
The Models API for Retuve.
"""

import shutil
import tempfile
import traceback
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from retuve import __version__ as retuve_version
from retuve.app.classes import Metric2D, Metric3D, ModelResponse
from retuve.app.helpers import (
    RESULTS_DIR,
    RESULTS_URL_ACCESS,
    analyze_validation,
)
from retuve.funcs import retuve_run
from retuve.keyphrases.config import Config

router = APIRouter()


@router.post(
    "/api/model/",
    response_model=ModelResponse,
    responses={
        400: {"description": "Invalid file type. Expected a DICOM file."},
        500: {"description": "Internal Server Error"},
    },
)
def analyse_image(
    request: Request,
    file: UploadFile = File(...),
    keyphrase: str = Form(...),
    api_token: Optional[str] = Form(None),
):
    """
    Analyze a file with a Retuve Model based on the keyphrase provided.

    :param request: The request object.
    :param file: The file to be analyzed.
    :param keyphrase: The keyphrase to be used for analysis.
    :param api_token: The API token for the keyphrase.

    :raises HTTPException: If the file or keyphrase is invalid.
    """

    try:
        config = Config.get_config(keyphrase)

        hippa_logger = request.app.config[config.name].hippa_logger

        analyze_validation(file, keyphrase, api_token)

        hippa_logger.info(
            f"Validated and Uploaded {file.filename} "
            f"with keyphrase {keyphrase} from host: {request.client.host}."
        )

        file_name = file.filename.split("/")[-1]

        # save file in tempfile with same name
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=file_name, prefix=""
        ) as temp_file:
            # save the file
            shutil.copyfileobj(file.file, temp_file)
            temp_file.flush()

            # get the file location
            temp_file = temp_file.name

            result = retuve_run(
                hip_mode=config.batch.hip_mode,
                config=config,
                modes_func=config.batch.mode_func,
                modes_func_kwargs_dict=config.batch.mode_func_args,
                file=temp_file,
            )

        notes = ""
        metrics3d = []
        metrics2d = []
        video_path = None
        figure_path = None
        img_path = None

        filename = file.filename.split("/")[-1].split(".")[0]

        if result.video_clip:
            video_path = f"{RESULTS_DIR}/{filename}.mp4"
            result.video_clip.write_videofile(video_path)
            video_path = video_path.replace(
                RESULTS_DIR, f"{RESULTS_URL_ACCESS}/{config.name}"
            )

        if result.visual_3d:
            figure_path = f"{RESULTS_DIR}/{filename}.html"
            result.visual_3d.write_html(figure_path)
            figure_path = figure_path.replace(
                RESULTS_DIR, f"{RESULTS_URL_ACCESS}/{config.name}"
            )

        if result.image:
            img_path = f"{RESULTS_DIR}/{filename}.jpg"
            result.image.save(img_path)
            img_path = img_path.replace(
                RESULTS_DIR, f"{RESULTS_URL_ACCESS}/{config.name}"
            )

        if result.hip_datas:
            for i, metric in enumerate(result.hip_datas.metrics):
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
            for i, metric in enumerate(result.hip.metrics):
                metrics2d.append(Metric2D(name=metric.name, value=metric.value))

        # Mark success in hippa logs
        hippa_logger.info(
            f"Successfully processed {file.filename} with keyphrase {keyphrase} "
            f"from host: {request.client.host}."
        )

        # Mock response for demonstration
        return ModelResponse(
            notes=notes,
            metrics_3d=metrics3d,
            video_url=f"{config.api.url}{video_path}" if video_path else "",
            figure_url=f"{config.api.url}{figure_path}" if figure_path else "",
            img_url=f"{config.api.url}{img_path}" if img_path else "",
            retuve_version=retuve_version,
            keyphrase_name=config.name,
            metrics_2d=metrics2d,
        )
    except Exception as e:
        # print traceback to hippa logs
        hippa_logger.error(
            f"Error in processing {file.filename} with keyphrase {keyphrase} "
            f"from host: {request.client.host}."
        )
        hippa_logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail="Internal Server Error, check logs."
        )

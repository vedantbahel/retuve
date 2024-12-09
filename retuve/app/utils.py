import asyncio
import json
import os
from datetime import datetime

from httpx import AsyncClient

from retuve.funcs import retuve_run


async def save_dicom_and_get_results(
    live_batchdir, instance_id, dicom_content, config
):
    # Save the DICOM file in the appropriate directory
    dicom_path = f"{live_batchdir}/{instance_id}.dcm"
    with open(dicom_path, "wb") as f:
        f.write(dicom_content)

    # Process the DICOM
    result = await asyncio.to_thread(
        retuve_run,
        hip_mode=config.batch.hip_mode,
        config=config,
        modes_func=config.batch.mode_func,
        modes_func_kwargs_dict={},
        file=dicom_path,
    )

    return result


async def save_results(instance_id, savedir, result=None, just_paths=False):
    """
    Saves DICOM content, video, image, and metrics results for a given instance ID.

    :param instance_id: The unique ID of the DICOM instance.
    :param result: The result object returned by `retuve_run`.
    :param savedir: The base directory for saving the results.
    :param just_paths: Whether to return just the paths of the saved results.
    """
    result_dir = f"{savedir}/{instance_id}"
    os.makedirs(result_dir, exist_ok=True)

    video_path = f"{result_dir}/video.mp4"
    img_path = f"{result_dir}/img.jpg"
    metrics_path = f"{result_dir}/metrics.json"

    if just_paths:
        return video_path, img_path, metrics_path

    # Save video result if available
    if result.video_clip:
        await asyncio.to_thread(result.video_clip.write_videofile, video_path)

    # Save image result if available
    if result.image:
        await asyncio.to_thread(result.image.save, img_path)

    # Save metrics if available
    if result.metrics:
        with open(metrics_path, "w") as f:
            json.dump(result.metrics, f)

    return video_path, img_path, metrics_path


async def get_sorted_dicom_images(
    orthanc_url, username=None, password=None, latest_time=None
):
    """
    Fetch and sort DICOM images from an Orthanc server based on acquisition time.

    :param orthanc_url: The Orthanc server URL.
    :param username: Username for authentication (optional).
    :param password: Password for authentication (optional).
    :param latest_time: Filter for acquisition times after this datetime.
    :return: A tuple of (sorted list of (DICOM content, instance ID), latest acquisition datetime).
    """

    auth = (username, password) if username and password else None
    images_with_dates = []
    latest_acq_time = latest_time or datetime.min

    async with AsyncClient() as client:
        patients_response = await client.get(
            f"{orthanc_url}/patients", auth=auth
        )
        for patient_id in patients_response.json():
            studies_response = await client.get(
                f"{orthanc_url}/patients/{patient_id}/studies", auth=auth
            )
            for study in studies_response.json():
                study_id = study["ID"]
                series_response = await client.get(
                    f"{orthanc_url}/studies/{study_id}/series", auth=auth
                )
                for series in series_response.json():
                    series_id = series["ID"]
                    instances_response = await client.get(
                        f"{orthanc_url}/series/{series_id}/instances",
                        auth=auth,
                    )
                    for instance in instances_response.json():
                        instance_id = instance["ID"]
                        metadata_response = await client.get(
                            f"{orthanc_url}/instances/{instance_id}/simplified-tags",
                            auth=auth,
                        )
                        metadata = metadata_response.json()
                        acq_date, acq_time = metadata.get(
                            "AcquisitionDate"
                        ), metadata.get("AcquisitionTime")
                        if acq_date and acq_time:
                            acq_datetime = datetime.strptime(
                                f"{acq_date}{acq_time.split('.')[0]}",
                                "%Y%m%d%H%M%S",
                            )

                            images_with_dates.append(
                                (
                                    acq_datetime,
                                    instance_id,
                                )
                            )

        final_images_with_dates = []

        for acq_datetime, instance_id in images_with_dates:
            if acq_datetime > latest_acq_time:
                file_response = await client.get(
                    f"{orthanc_url}/instances/{instance_id}/file",
                    auth=auth,
                )

                latest_acq_time = max(latest_acq_time, acq_datetime)

                final_images_with_dates.append(
                    (acq_datetime, file_response.content, instance_id)
                )

        images_with_dates.sort(key=lambda x: x[0])
        latest_image = images_with_dates[-1]

        # inject file_response.content into latest_image
        file_response = await client.get(
            f"{orthanc_url}/instances/{latest_image[1]}/file",
            auth=auth,
        )

        latest_image = (
            latest_image[0],
            file_response.content,
            latest_image[1],
        )

        if not final_images_with_dates:
            final_images_with_dates = [latest_image]

    return [
        (image, instance_id)
        for _, image, instance_id in final_images_with_dates
    ], latest_acq_time

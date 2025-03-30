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

import multiprocessing
import os
import shutil
import time

from retuve.app.classes import File, FileEnum
from retuve.app.helpers import API_RESULTS_URL_ACCESS
from retuve.keyphrases.config import Config
from retuve.keyphrases.enums import HipMode, Outputs
from retuve.logs import ulogger
from retuve.trak.data import extract_files, insert_files


def get_state(config: Config) -> bool:
    """
    Get the state of the files and update the database.

    :param config: The configuration.
    """

    # turn the above into a list comprehension
    files = [
        os.path.join(dataset, file)
        for dataset in config.trak.datasets
        for file in os.listdir(dataset)
        if any(file.endswith(ext) for ext in config.batch.input_types)
    ]
    save_dir = config.api.savedir

    new_states = {}

    for file in files:
        file_id = file.split("/")[-1].split(".")[0]

        updated = File(
            file_id=file_id,
            state=FileEnum.PENDING,
            metrics_url="N/A",
            video_url="N/A",
            img_url="N/A",
            figure_url="N/A",
            attempts=0,
        )

        # Check if any case files exist
        output_paths = [os.path.join(save_dir, file_id)]
        any_case_files_exist = any(
            os.path.isfile(os.path.join(path, "metrics.json")) for path in output_paths
        )

        url = config.api.url
        base_url = os.path.join(url, API_RESULTS_URL_ACCESS, config.name, file_id)
        updated.img_url = os.path.join(base_url, Outputs.IMAGE)

        # If files exist, update URLs and set state to COMPLETED
        if any_case_files_exist:
            updated.video_url = os.path.join(base_url, Outputs.VIDEO_CLIP)
            updated.figure_url = os.path.join(base_url, Outputs.VISUAL3D)
            updated.metrics_url = os.path.join(base_url, Outputs.METRICS)
            updated.state = FileEnum.COMPLETED

        else:
            os.makedirs(os.path.join(save_dir, file_id), exist_ok=True)

            # Insert Empty Images automatically, if mode is not 3D
            if config.batch.hip_mode not in [HipMode.US3D, HipMode.US2DSW]:
                shutil.copyfile(file, os.path.join(save_dir, file_id, "img.jpg"))

            any_case_videos_exist = any(
                os.path.isfile(os.path.join(path, "video.mp4")) for path in output_paths
            )

            if any_case_videos_exist:
                # Add the video URL
                updated.video_url = os.path.join(base_url, Outputs.VIDEO_CLIP)
                updated.state = FileEnum.FAILED

        new_states[file_id] = updated

    # get file_ids in cache, find the difference and insert the new states
    cached_files = extract_files(config.api.db_path)
    for cached_file in cached_files:
        if cached_file.file_id not in new_states:
            # and there is no video + metrics file

            # Check if any case files exist
            output_paths = [
                os.path.join(save_dir, cached_file.file_id, output)
                for output in config.batch.outputs
            ]
            any_case_files_exist = any(os.path.exists(path) for path in output_paths)

            if any_case_files_exist:
                # mark as dead
                cached_file.state = FileEnum.DEAD_WITH_RESULTS
                new_states[cached_file.file_id] = cached_file

            else:
                # mark as pending
                cached_file.state = FileEnum.DEAD
                new_states[cached_file.file_id] = cached_file

    insert_files(new_states.values(), config.api.db_path)


def run_state_machine(config: Config):
    """
    Continuously run the state machine.
    """
    ulogger.info(f"\nRunning state machine {config.name}!\n")

    while True:
        get_state(config)
        time.sleep(5)


def run_all_state_machines():
    """
    Run all state machines from registered configs.
    """

    configs = [config for _, config in Config.get_configs()]

    # set type to spawn
    multiprocessing.set_start_method("spawn")

    # run each state machine in a separate process
    processes = [
        multiprocessing.Process(target=run_state_machine, args=(config,))
        for config in configs
    ]

    for process in processes:
        process.start()

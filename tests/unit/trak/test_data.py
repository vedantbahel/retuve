import os
import sqlite3
from typing import List

import pytest

from retuve.app.classes import File, FileEnum
from retuve.trak.data import (
    database_init,
    extract_files,
    get_file_data,
    insert_files,
)

# Get this files DIR
DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def db_path(tmp_path):
    return os.path.join(tmp_path, "test_files.db")


@pytest.fixture
def sample_files() -> List[File]:
    return [
        File(
            file_id="1",
            state=FileEnum.COMPLETED,
            metrics_url="http://metrics1",
            video_url="http://video1",
            img_url="http://img1",
            figure_url="http://figure1",
            attempts=1,
        ),
        File(
            file_id="2",
            state=FileEnum.PENDING,
            metrics_url="http://metrics2",
            video_url="http://video2",
            img_url="http://img2",
            figure_url="http://figure2",
            attempts=2,
        ),
    ]


def test_database_init(db_path):
    database_init(db_path)
    assert os.path.exists(db_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='files'"
        )
        assert cursor.fetchone() is not None


def test_insert_files(db_path, sample_files):
    database_init(db_path)
    insert_files(sample_files, db_path)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM files")
        count = cursor.fetchone()[0]
        assert count == len(sample_files)


def test_extract_files(db_path, sample_files):
    database_init(db_path)
    insert_files(sample_files, db_path)
    files = extract_files(db_path)
    assert len(files) == len(sample_files)
    assert files[0].file_id == "1"
    assert files[1].file_id == "2"


def test_get_file_data(db_path, sample_files):
    database_init(db_path)
    insert_files(sample_files, db_path)

    file = get_file_data("1", db_path)
    assert file.file_id == "1"
    assert file.state == FileEnum.COMPLETED
    assert file.metrics_url == "http://metrics1"
    assert file.video_url == "http://video1"
    assert file.img_url == "http://img1"
    assert file.figure_url == "http://figure1"
    assert file.attempts == 1

    new_file = get_file_data("nonexistent", db_path)
    assert new_file.file_id == "nonexistent"
    assert new_file.state == FileEnum.PENDING
    assert new_file.metrics_url == "N/A"
    assert new_file.video_url == "N/A"
    assert new_file.img_url == "N/A"
    assert new_file.figure_url == "N/A"
    assert new_file.attempts == 0

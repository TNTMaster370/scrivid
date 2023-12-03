from functions import get_current_directory, TemporaryDirectory
from samples import empty, figure_eight, image_drawing

import scrivid

import cv2 as opencv
import imagehash
from PIL import Image
import pytest


# Alternative name for module to reduce typing
parametrize = pytest.mark.parametrize


def loop_over_video_objects(container_actual, container_expected):
    while True:
        ret_a, frame_actual = container_actual.vid.read()
        ret_e, frame_expected = container_expected.vid.read()

        if not ret_a or not ret_e:
            break

        image_actual = Image.fromarray(opencv.cvtColor(frame_actual, opencv.COLOR_BGR2RGB))
        image_expected = Image.fromarray(opencv.cvtColor(frame_expected, opencv.COLOR_BGR2RGB))

        phash_actual = imagehash.phash(image_actual)
        phash_expected = imagehash.phash(image_expected)
        assert phash_actual == phash_expected


@pytest.fixture(scope="module")
def temp_dir():
    with TemporaryDirectory(get_current_directory()) as tempdir:
        yield tempdir.dir


class VideoFilePointer:
    def __init__(self, video_path):
        self.vid = opencv.VideoCapture(video_path)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.vid.release()


# @pytest.mark.skip("Unstable result; cannot debug at the moment.")
@pytest.mark.flag_video
@parametrize("sample_function,sample_module_name", [
    (empty, "empty"),
    (figure_eight, "figure_eight"),
    (image_drawing, "image_drawing")
])
def test_compile_video_output(temp_dir, sample_function, sample_module_name):
    instructions, metadata = sample_function.data()
    metadata.save_location = temp_dir
    scrivid.compile_video(instructions, metadata)

    actual_video_path = str(temp_dir / f"{metadata.video_name}.mp4")
    expected_video_path = str(get_current_directory() / f"videos/__scrivid_\'{sample_module_name}\'__.mp4")

    with VideoFilePointer(actual_video_path) as container_actual, \
            VideoFilePointer(expected_video_path) as container_expected:
        loop_over_video_objects(container_actual, container_expected)

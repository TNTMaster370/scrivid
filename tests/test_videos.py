from functions import get_current_directory, TemporaryDirectory
from samples import empty, figure_eight, image_drawing

import scrivid

import av
import imagehash
import pytest


# Alternative name for module to reduce typing
parametrize = pytest.mark.parametrize


@pytest.fixture(scope="module")
def temp_dir():
    with TemporaryDirectory(get_current_directory()) as tempdir:
        yield tempdir.dir


def loop_over_video_objects(*containers):
    container_actual, container_expected = containers

    for frame_actual, frame_expected in zip(
            container_actual.decode(video=0), 
            container_expected.decode(video=0)
    ):
        image_actual = frame_actual.to_image()
        image_expected = frame_expected.to_image()

        phash_actual = imagehash.phash(image_actual)
        phash_expected = imagehash.phash(image_expected)
        assert phash_actual == phash_expected


@pytest.mark.flag_video
@parametrize("sample_function,sample_module_name", [
    (empty, "empty"),
    (figure_eight, "figure_eight"),
    (image_drawing, "image_drawing")
])
def test_compile_video_output__(temp_dir, sample_function, sample_module_name):
    video_settings = {"format": "mp4", "options": {"crf": "23", "pix_fmt": "rgb24"}}

    instructions, metadata = sample_function.data()
    metadata.save_location = temp_dir
    scrivid.compile_video(instructions, metadata)

    actual_video_path = str(temp_dir / f"{metadata.video_name}.mp4")
    expected_video_path = str(get_current_directory() / f"videos/__scrivid_\'{sample_module_name}\'__.mp4")

    with av.open(actual_video_path, **video_settings) as container_actual, \
            av.open(expected_video_path, **video_settings) as container_expected:
        loop_over_video_objects(container_actual, container_expected)

from functions import get_current_directory, hacky_import, TemporaryDirectory

import sys

import av
import imagehash
import pytest


# Alternative name for module to reduce typing
parametrize = pytest.mark.parametrize


# I have to use a hacky-kind of import to dynamically import from another 
# directory. I'm using the sample script from the 'sample' directory at the 
# moment, but I may add local sample snippets for small concept tests.
sample_directory = get_current_directory().parent / "sample"

sample_1 = hacky_import(sample_directory / "01_FIRST/main.py", "main")
sys.modules["sample_1"] = sample_1


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
@parametrize("generative_function,gen_args,actual_video_name,expected_result_path", [
    (sample_1.generate, (sample_directory / "01_FIRST/images",), "scrivid_sampleVideo_final.mp4", 
     get_current_directory() / "videos/__sample_1__.mp4")
])
def test_compile_video_output(temp_dir, generative_function, gen_args, actual_video_name, expected_result_path):
    video_settings = {"format": "mp4", "options": {"crf": "23", "pix_fmt": "rgb24"}}

    generative_function(temp_dir, *gen_args)

    with av.open(str(temp_dir / actual_video_name), **video_settings) as container_actual, \
            av.open(str(expected_result_path), **video_settings) as container_expected:
        loop_over_video_objects(container_actual, container_expected)

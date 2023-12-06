import pytest


def pytest_addoption(parser):
    # The flag '--skip-video-tests' was added to facilitate the video tests, so
    # I can only run those tests when I mean to, since running those tests is
    # quite expensive.
    parser.addoption(
        "--skip-video-tests",
        action="store_true",
        help="Skips tests related to video-making."
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--skip-video-tests"):
        skip_flag = pytest.mark.skip(
            reason="Skip flag for video tests enabled."
        )

        for item in items:
            if "flag_video" in item.keywords:
                item.add_marker(skip_flag)

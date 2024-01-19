import scrivid

from pathlib import Path


def get_current_directory():
    return Path(__file__).absolute().parent


def ALL():
    return INSTRUCTIONS(), METADATA()


def INSTRUCTIONS():
    directory = get_current_directory().parent / "images"
    return (
        scrivid.create_image_reference(
            "LEFT",
            directory / "img2.png",
            layer=1,
            scale=1,
            x=50,
            y=50
        ),
        scrivid.create_image_reference(
            "RIGHT",
            directory / "img3.png",
            layer=1,
            scale=1,
            x=205,
            y=100
        ),
        scrivid.MoveAdjustment("RIGHT", 12, scrivid.Properties(x=0), 1)
    )


def METADATA():
    return scrivid.Metadata(
        frame_rate=12,
        video_name="testSampleResult_\'overlap\'", 
        window_size=(410, 410)
    )

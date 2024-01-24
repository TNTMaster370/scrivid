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
            "stone",
            directory / "img2.png",
            layer=1,
            scale=1,
            x=50,
            y=20
        ),
        scrivid.adjustments.move.create("stone", 1, scrivid.Properties(x=500), 36)
    )


def METADATA():
    return scrivid.Metadata(
        frame_rate=12,
        video_name="testSampleResult_\'slide\'", 
        window_size=(600, 306)
    )

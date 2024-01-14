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
            "BLOCK",
            directory / "img3.png",
            layer=1,
            scale=1,
            x=300, 
            y=50
        ),
        scrivid.MoveAdjustment("BLOCK", 6, scrivid.Properties(x=500, y=500), 10),
        scrivid.MoveAdjustment("BLOCK", 16, scrivid.Properties(x=250, y=-250), 5),
        scrivid.MoveAdjustment("BLOCK", 21, scrivid.Properties(x=-250, y=-250), 5),
        scrivid.MoveAdjustment("BLOCK", 26, scrivid.Properties(x=-500, y=500), 10),
        scrivid.MoveAdjustment("BLOCK", 36, scrivid.Properties(x=-250, y=-250), 5),
        scrivid.MoveAdjustment("BLOCK", 41, scrivid.Properties(x=250, y=-250), 5)
    )


def METADATA():
    return scrivid.Metadata(
        fps=12,
        video_name="testSampleResult_\'figure_eight\'", 
        window_size=(1356, 856)
    )

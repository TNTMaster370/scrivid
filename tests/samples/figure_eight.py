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
        scrivid.adjustments.move.create("BLOCK", 6, scrivid.properties.Properties(x=500, y=500), 10),
        scrivid.adjustments.move.create("BLOCK", 16, scrivid.properties.Properties(x=250, y=-250), 5),
        scrivid.adjustments.move.create("BLOCK", 21, scrivid.properties.Properties(x=-250, y=-250), 5),
        scrivid.adjustments.move.create("BLOCK", 26, scrivid.properties.Properties(x=-500, y=500), 10),
        scrivid.adjustments.move.create("BLOCK", 36, scrivid.properties.Properties(x=-250, y=-250), 5),
        scrivid.adjustments.move.create("BLOCK", 41, scrivid.properties.Properties(x=250, y=-250), 5)
    )


def METADATA():
    return scrivid.Metadata(
        frame_rate=12,
        video_name=f"testSampleResult_\'{NAME()}\'", 
        window_size=(1356, 856)
    )


def NAME():
    return "figure_eight"

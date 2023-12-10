import scrivid

from pathlib import Path


def get_current_directory():
    return Path(__file__).absolute().parent


def data():
    metadata = scrivid.Metadata(
        fps=12,
        video_name="testSampleResult_\'slide\'", 
        window_size=(600, 306)
    )

    directory = get_current_directory().parent / "images"
    instructions = [
        scrivid.create_image_reference(
            "stone",
            directory / "img2.png",
            layer=1,
            scale=1,
            x=50,
            y=20
        ),
        scrivid.MoveAdjustment("stone", 1, scrivid.Properties(x=500), 36)
    ]

    return instructions, metadata

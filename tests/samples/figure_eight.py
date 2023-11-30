import scrivid

from pathlib import Path


def get_current_directory():
    return Path(__file__).absolute().parent


def data():
    metadata = scrivid.Metadata(
        fps=12,
        video_name="testSampleResult_\'figure_eight\'", 
        window_size=(1356, 856)
    )

    directory = get_current_directory().parent / "images"
    instructions = [
        scrivid.create_image_reference(
            "BLOCK",
            directory / "img3.png",
            layer=1,
            scale=1,
            x=300, 
            y=50
        ),
        '''
        + 500, + 500
        + 250, - 250
        - 250, - 250
        - 500, + 500
        - 250, - 250
        + 250, - 250
        ''',
        scrivid.MoveAdjustment(
            "BLOCK", 
            6, 
            scrivid.Properties(x=500, y=500), 
            10
        ),
        scrivid.MoveAdjustment(
            "BLOCK",
            16,
            scrivid.Properties(x=250, y=-250),
            5
        ),
        scrivid.MoveAdjustment(
            "BLOCK",
            21,
            scrivid.Properties(x=-250, y=-250),
            5
        ),
        scrivid.MoveAdjustment(
            "BLOCK",
            26,
            scrivid.Properties(x=-500, y=500),
            10
        ),
        scrivid.MoveAdjustment(
            "BLOCK",
            36,
            scrivid.Properties(x=-250, y=-250),
            5
        ),
        scrivid.MoveAdjustment(
            "BLOCK",
            41,
            scrivid.Properties(x=250, y=-250),                   
            5
        )
    ]

    return instructions, metadata

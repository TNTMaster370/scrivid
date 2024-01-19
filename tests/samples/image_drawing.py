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
            "TL",
            directory / "img1.png",
            layer=1,
            scale=1,
            x=50, 
            y=50
        ),
        scrivid.create_image_reference(
            "TR", 
            directory / "img2.png", 
            layer=2,
            scale=1,
            x=355,
            y=50
        ),
        scrivid.create_image_reference(
            "BL",
            directory / "img2.png",
            layer=3,
            scale=1,
            x=50,
            y=355
        ),
        scrivid.create_image_reference(
            "BR",
            directory / "img1.png",
            layer=4,
            scale=1,
            x=355,
            y=355
        ),
        # This last ImageReference is a temporary cheat to make sure that the
        # video *actually* has a duration other than one frame, since the 
        # script will think that there's one need for one frame to draw. In the
        # future, this should not be necessary, and it should be allowed a more
        # explicit duration. But for now, the duration is explicit.
        scrivid.create_image_reference(
            "HIDDEN",
            directory / "img1.png",
            layer=5,
            scale=0,
            x=-500,
            y=-500
        ),
        scrivid.HideAdjustment("HIDDEN", 0),
        scrivid.ShowAdjustment("HIDDEN", 20)
    )


def METADATA():
    return scrivid.Metadata(
        frame_rate=12,
        video_name="testSampleResult_\'image_drawing\'", 
        window_size=(660, 660)
    )

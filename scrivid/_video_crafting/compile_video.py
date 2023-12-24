from __future__ import annotations

from ._frame_drawing import create_frame, generate_frames
from ._video_stitching import stitch_video

from .._separating_instructions import separate_instructions
from .._motion_tree import parse
from .._utils import TemporaryDirectory

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._file_objects.adjustments import ImageReference, RootAdjustment
    from ..metadata import Metadata

    from collections.abc import Sequence
    from typing import Union

    INSTRUCTIONS = Union[ImageReference, RootAdjustment]


def compile_video(instructions: Sequence[INSTRUCTIONS], metadata: Metadata):
    """
    Converts the objects, taken as instructions, into a compiled video.

    :param instructions: A list of instances of ImageReference's, and/or a 
        class of the Adjustment hierarchy.
    :param metadata: An instance of Metadata that stores the attributes
        of the video.
    """
    metadata._validate()

    separated_instructions = separate_instructions(instructions)
    motion_tree = parse(separated_instructions)

    with TemporaryDirectory(
        metadata.save_location / ".scrivid-cache"
    ) as temp_dir:
        # ...
        frames = generate_frames(motion_tree)

        for frame_information in frames:
            create_frame(
                *frame_information,
                separated_instructions,
                metadata.window_size,
                temp_dir.dir
            )

        stitch_video(temp_dir.dir, metadata)

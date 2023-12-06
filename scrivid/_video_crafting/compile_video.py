from __future__ import annotations

from ._frame_drawing import create_frame, generate_frames
from ._video_stitching import stitch_video

from .._separating_instructions import separate_instructions
from .._motion_tree import parse

import os
import shutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._file_objects.adjustments import ImageReference, RootAdjustment
    from ..metadata import Metadata

    from collections.abc import Sequence
    from pathlib import Path
    from typing import Union

    INSTRUCTIONS = Union[ImageReference, RootAdjustment]


class _TemporaryDirectory:
    def __init__(self, folder_location: Path):
        self.dir = folder_location / ".scrivid-cache"

    def __enter__(self):
        os.mkdir(self.dir)
        return self

    def __exit__(self, *_):
        shutil.rmtree(self.dir)


def compile_video(instructions: Sequence[INSTRUCTIONS], metadata: Metadata):
    """
    Converts the objects, taken as instructions, into a compiled video.

    :param instructions: A list of instances of ImageReference's, and/or a 
        class of the Adjustment hierarchy.
    :param metadata: An instance of Metadata that stores the attributes
        of the video.
    """
    separated_instructions = separate_instructions(instructions)
    motion_tree = parse(separated_instructions)

    with _TemporaryDirectory(metadata.save_location) as temp_dir:
        frames = generate_frames(motion_tree)

        for frame_information in frames:
            create_frame(
                *frame_information,
                separated_instructions,
                metadata.window_size,
                temp_dir.dir
            )

        stitch_video(temp_dir.dir, metadata)

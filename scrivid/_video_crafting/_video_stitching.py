from .. import errors

import os

import ffmpeg


def _concatenate(*, input_file, input_settings, output_file, output_settings):
    try:
        (
            ffmpeg
            .input(input_file, **input_settings)
            .output(output_file, **output_settings)
            .run(quiet=True)
        )
    except ffmpeg._run.Error as exc:
        raise errors.InternalErrorFromFFMPEG(exc, exc.stdout, exc.stderr)


def stitch_video(temporary_directory, metadata):
    input_file = os.path.join(temporary_directory, "%06d.png")
    output_file = str(metadata.save_location / f"{metadata.video_name}.mp4")
    dimensions = f"{metadata.window_width}x{metadata.window_height}"

    # I honest to god could not tell you how I figured this out. I just
    # couldn't figure out how to make a stable result for the life of me.
    _concatenate(
        input_file=input_file, 
        input_settings={
            "f": "image2",
            "pattern_type": "sequence",
            "r": metadata.frame_rate,
        },
        output_file=output_file,
        output_settings={
            "b:v": "4M",
            "vcodec": "libx264",
            "pix_fmt": "yuv420p",
            "s": dimensions
        }
    )

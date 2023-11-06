from pathlib import Path
import scrivid


class VisibilityIndex:
    _index_dict = {
        0: (0, 75),
        1: (75, 105),
        2: (105, 225),
        3: (225, 240),
        4: (240, 330),
        5: (330, 600)
    }

    @classmethod
    def access(cls, index):
        return cls._index_dict[index]


def create_instructions(image_directory):
    instructions = []

    for index in range(6):
        instructions.append(
            scrivid.image_reference(
                index,
                image_directory / f"img{index+1}.png",
                layer=index+1,
                scale=1,
                visibility=scrivid.VisibilityStatus.HIDE,
                x=0,
                y=0
            )
        )

        show_time, hide_time = VisibilityIndex.access(index)
        instructions.append(scrivid.ShowAdjustment(index, show_time))
        instructions.append(scrivid.HideAdjustment(index, hide_time))

    return instructions


def generate(save_location):
    metadata = scrivid.Metadata(
        frame_rate=30,
        save_location=save_location,
        video_name="scrivid_sampleVideo_final",
        window_size=(852, 480)
    )

    instructions = create_instructions(metadata.save_location / "images")
    scrivid.compile_video(instructions, metadata)


def main():
    save_location = Path(__file__).absolute().parent
    generate(save_location)


if __name__ == "__main__":
    main()

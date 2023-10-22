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


def create_image_references(image_directory):
    objects = []
    for index in range(6):
        objects.append(
            scrivid.image_reference(
                image_directory / f"img{index+1}.png",
                layer=index+1,
                scale=1,
                x=0,
                y=0
            )
        )

        show, hide = VisibilityIndex.access(index)
        scrivid.ShowAdjustment(show) >> objects[-1]
        scrivid.HideAdjustment(hide) >> objects[-1]

    return objects


def generate(save_location):
    metadata = scrivid.Metadata(
        frame_rate=30,
        save_location=save_location,
        video_name="scrivid_sampleVideo_final",
        window_size=(852, 480)
    )

    image_references = create_image_references(metadata.save_location / "images")
    scrivid.compile_video(image_references, metadata)


def main():
    generate(Path(".").absolute())


if __name__ == "__main__":
    main()

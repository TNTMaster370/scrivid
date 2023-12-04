import figure_eight
import scrivid


def main():
    current_directory = figure_eight.get_current_directory()
    instructions, metadata = figure_eight.data()
    metadata.save_location = current_directory
    scrivid.compile_video(instructions, metadata)


if __name__ == "__main__":
    main()

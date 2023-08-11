from scrivid import ImageReference


class FileSubstitute:
    def __init__(self, file):
        self.state = []
        self.__file = file

    def open(self):
        self.state.append("open")

    def close(self):
        self.state.append("close")


def test_image_file_management():
    file_handler = FileSubstitute("some/file")
    image_reference = ImageReference(file_handler)

    image_reference.open()
    image_reference.close()

    assert file_handler.state == ["open", "close"]


def test_image_file_management_weakref():
    file_handler = FileSubstitute("some/file")
    image_reference = ImageReference(file_handler)

    image_reference.open()
    del image_reference  # The method to close should be called when `i`s
    # reference count hits zero.

    assert file_handler.state == ["open", "close"]

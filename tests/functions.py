from pathlib import Path


def get_current_directory():
    return Path(__file__).absolute().parent


def hacky_import(file, module_name):
    # Borrowed and adapted from the documentation: 
    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    import importlib.util

    spec = importlib.util.spec_from_file_location(module_name, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


# Copied from `scrivid.compile_video` to avoid dependency.
class TemporaryDirectory:
    def __init__(self, folder_location: Path):
        self.dir = folder_location / ".scrivid-test-cache"

    def __enter__(self):
        import os
        os.mkdir(self.dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import shutil
        shutil.rmtree(self.dir)

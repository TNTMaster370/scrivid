from __future__ import annotations

import os
import shutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class TemporaryDirectory:
    def __init__(self, dir: Path):
        self.dir = dir

    def __enter__(self):
        os.mkdir(self.dir)
        return self

    def __exit__(self, *_):
        shutil.rmtree(self.dir)

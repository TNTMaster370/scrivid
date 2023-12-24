class Index:
    __slots__ = ("end", "start")

    start: int
    end: int

    def __init__(self, index):
        self.end = index
        self.start = index

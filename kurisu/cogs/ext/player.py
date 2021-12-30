from random import shuffle

import pomice


class Player(pomice.Player):
    """Subclass of Pomice Player, adding Queue."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._queue: list[pomice.Track] = []

    @property
    def queue(self) -> list[pomice.Track]:
        return self._queue

    def shuffle_queue(self) -> None:
        shuffle(self.queue)

#!/usr/bin/env python
input_path = "input.txt"


def process_input(input_path: str) -> int:
    s = 0
    for line in open(input_path):
        line = line.strip()
        if len(line) == 0:
            yield s
            s = 0
        else:
            s += int(line)
    yield s
    return StopIteration


elves = process_input(input_path)


class Store(object):
    def __init__(self, topk: int):
        self._topk = topk
        self._store = []

    def maybe_store(self, value) -> None:
        self._store.append(value)
        self._store.sort()
        self._store = self._store[-self._topk :]

    def sum(self) -> int:
        return sum(self._store)


topk = 3
store = Store(topk)
for elf in elves:
    store.maybe_store(elf)

print(store.sum())

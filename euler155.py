import itertools
from fractions import Fraction

from functools import cache
from typing import Set, List

one = Fraction(1, 1)

circuits = {1: {one}}

for i in range(2, 18 + 1):
    print(f'starting {i}')
    s = set()
    for first_circuit_size in range(1, i):
        other_size = i - first_circuit_size
        if other_size <= 0:
            continue
        if other_size > first_circuit_size:
            continue

        for first in circuits[first_circuit_size]:
            for other in circuits[other_size]:
                s.add(first + other)
                s.add((first * other) / (first + other))

    circuits[i] = s

unique = set()
for index in sorted(circuits.keys()):
    size = len(circuits[index])

    unique = unique.union(circuits[index])

    print(f'{index}: {len(circuits[index])}, unique: {len(unique)}')

import sys

sys.exit()


def precompute_places(to_place: int, current_memory_size: int, current_depth: int, max_size: int, current_placed: List,
                      solutions: List):
    for i in range(current_depth, max_size):
        if i != current_depth:
            current_memory_size += 1

        if current_memory_size >= 2:

            current_placed.append(i)

            if to_place == 1:
                solutions.append(tuple(current_placed))

            else:
                precompute_places(to_place - 1, current_memory_size - 1, i, max_size, current_placed, solutions)

            current_placed.pop()


def parallel_coupling(r1, r2):
    return r1 + r2


def serial_coupling(r1, r2):
    return r1 * r2 / (r1 + r2)


def calculate(places: List, memory: List, current_index: int, solutions: set):
    next_to_place = places.pop()

    if not next_to_place >= current_index:
        raise AssertionError

    while current_index != next_to_place:
        current_index += 1
        memory.append(one)

    r1, r2 = memory.pop(), memory.pop()
    for i in (True, False):
        if i:
            r = parallel_coupling(r1, r2)
        else:
            r = serial_coupling(r1, r2)
        memory.append(r)
        if not places:
            if not len(memory) == 1:
                raise AssertionError
            solutions.add(memory[0])

        else:
            calculate(places, memory, current_index, solutions)

    places.append(next_to_place)


def main(size):
    solution_set = set()

    sol = []

    precompute_places(size - 1, 1, 0, size, [], sol)

    for comb in itertools.product((True, False), repeat=size - 1):

        for places in sol:
            memory = []
            current = -1

            for index, next_to_place in enumerate(places):
                if not next_to_place >= current:
                    raise AssertionError

                while current != next_to_place:
                    current += 1
                    memory.append(one)

                if comb[index]:
                    r = parallel_coupling(memory.pop(), memory.pop())
                    memory.append(r)
                else:
                    r1, r2 = memory.pop(), memory.pop()
                    r = serial_coupling(r1, r2)
                    memory.append(r)

            if not len(memory) == 1:
                raise AssertionError

            solution_set.add(memory[0])

    print(len(solution_set))
    return len(solution_set)


if __name__ == '__main__':

    comm = 0
    from datetime import datetime

    for i in range(1, 10):
        before = datetime.now()
        r = main(i)

        delta = datetime.now() - before

        comm += r
        print(f'{i}: {r}, time: {delta.seconds} total: {comm}')

    main(4)

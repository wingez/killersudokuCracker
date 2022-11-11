from __future__ import annotations

from dataclasses import dataclass
from typing import Union, Tuple, List, Iterator, Generator


@dataclass
class Pair:
    l: Union[int, Pair]
    r: Union[int, Pair]

    def __str__(self):
        return f'[{self.l}, {self.r}]'

    def __repr__(self):
        return str(self)


def parse_recursive(s: str) -> Tuple[Union[Pair, int], int]:
    if s[0] != '[':

        m = []
        if ',' in s:
            m.append(s.index(','))
        if ']' in s:
            m.append(s.index(']'))
        if not m:
            raise ValueError()
        until = min(m)

        number = s[:until]
        return int(number), len(number)

    index = 1
    left, pos = parse_recursive(s[index:])
    index += pos
    if not s[index] == ',':
        raise ValueError()
    index += 1

    right, pos = parse_recursive(s[index:])
    index += pos
    if not s[index] == ']':
        raise ValueError
    index += 1

    return Pair(left, right), index


def parse(s: str) -> Pair:
    return parse_recursive(s)[0]


print(str(parse('[1,2]')))
print(str(parse('[[1,2],3]')))
print(str(parse('[9,[8,7]]')))
print(str(parse('[[[9,[3,8]],[[0,9],6]],[[[3,7],[4,9]],3]]')))


def traverse(node: Pair) -> Generator[Tuple[Union[int, Pair], List[str]]]:
    def traverse_recursive(n: Union[int, Pair], how_to_get_here: List[str]):
        yield n, how_to_get_here
        if isinstance(n, Pair):
            yield from traverse_recursive(n.l, how_to_get_here + ['l'])
            yield from traverse_recursive(n.r, how_to_get_here + ['r'])

    yield from traverse_recursive(node, [])


for i in traverse(parse('[[[9,[3,8]],[[0,9],6]],[[[3,7],[4,9]],3]]')):
    print(i)


def replace(node: Pair, value: Union[int, Pair], path: List[str]):
    for p in path[:-1]:
        node = getattr(node, p)

    setattr(node, path[-1], value)


def explode(p: Pair):
    i = traverse(p)

    leftmost: int
    how_to_get_to_leftmost: List[str] = None

    while True:
        try:
            node, path = next(i)
        except StopIteration:
            return False
        if isinstance(node, int):
            leftmost = node
            how_to_get_to_leftmost = path
        else:
            if len(path) > 4:
                raise ValueError()
            if len(path) == 4:
                to_explode = node
                to_explode_path = path
                break

    how_to_get_to_rightmost = None
    while True:
        try:
            node, path = next(i)
        except StopIteration:
            break
        if isinstance(node, int):
            if len(path) < len(to_explode_path) or path[:len(to_explode_path)] != to_explode_path:
                rightmost = node
                how_to_get_to_rightmost = path
                break

    if not isinstance(to_explode, Pair):
        raise ValueError()

    if how_to_get_to_leftmost is not None:
        replace(p, leftmost + to_explode.l, how_to_get_to_leftmost)
    replace(p, 0, to_explode_path)

    if how_to_get_to_rightmost is not None:
        replace(p, rightmost + to_explode.r, how_to_get_to_rightmost)

    return True


print("SINGLE EXPLODE START")

g = parse('[[[[[9,8],1],2],3],4]')
explode(g)
print(g, parse('[[[[0,9],2],3],4]'), sep='\n')

g = parse('[7,[6,[5,[4,[3,2]]]]]')
explode(g)
print(g, parse('[7,[6,[5,[7,0]]]]'), sep='\n')

g = parse('[[6,[5,[4,[3,2]]]],1]')
explode(g)
print(g, parse('[[6,[5,[7,0]]],3]'), sep='\n')

g = parse('[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]')
explode(g)
print(g, parse('[[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]]'), sep='\n')

g = parse('[[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]]')
explode(g)
print(g, parse('[[3,[2,[8,0]]],[9,[5,[7,0]]]]'), sep='\n')

print("SINGLE EXPLODE END")

import math


def split(node: Pair):
    for n, path in traverse(node):
        if isinstance(n, int) and n >= 10:
            new = Pair(math.floor(n / 2), math.ceil(n / 2))

            replace(node, new, path)
            return True

    return False


def reduce(node):
    while True:
        if explode(node):
            continue
        if split(node):
            continue
        break


g = Pair(parse('[[[[4,3],4],4],[7,[[8,4],9]]]'), parse('[1,1]'))
reduce(g)
print(g)


def magnitude(node: Union[int, Pair]) -> int:
    if isinstance(node, int):
        return node
    return 3 * magnitude(node.l) + 2 * magnitude(node.r)


print("PART 1 start")
with open("data.txt") as f:
    node = None
    for line in f:
        n = parse(line.strip())

        if node is None:
            node = n
        else:
            node = Pair(node, n)
        reduce(node)

    print(node)
    print(magnitude(node))
print("PART 2 ")

with open("data.txt") as f:
    nodes = [line.strip() for line in f]

    import itertools

    maximum = 0
    for g in itertools.permutations(nodes, 2):
        node = Pair(parse(g[0]),parse(g[1]))
        reduce(node)
        maximum = max(maximum, magnitude(node))

print(maximum)

print("TEST")

for g in itertools.permutations([

    parse("[[2,[[7,7],7]],[[5,8],[[9,3],[0,2]]]]"),
    parse("[[[0,[5,8]],[[1,7],[9,6]]],[[4,[1,2]],[[1,4],2]]]")]):
    print(g)
    node = Pair(g[0], g[1])
    reduce(node)
    print(g)
    print(magnitude(node))

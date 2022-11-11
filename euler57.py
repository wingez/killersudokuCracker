import math
from fractions import Fraction
import functools


@functools.cache
def func(iteration: int):
    if iteration == 0:
        return Fraction(2, 1)

    return Fraction(2, 1) + Fraction(1, 1) / func(iteration - 1)


size = 2
result = 0

for i in range(1000):
    frac = Fraction(1, 1) + Fraction(1, 1) / func(i)

    numerator, denominator = frac.as_integer_ratio()

    numerator_digits = math.floor(math.log10(numerator))
    denominator_digits = math.floor(math.log10(denominator))

    if numerator_digits > denominator_digits:
        result += 1

    if i % 10 == 0:
        print(i)

print(result)

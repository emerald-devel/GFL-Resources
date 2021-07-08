import numpy as np
import math

def custom_sum(vals):
    # We sort them in ascending order to minimize floating point and rounding errors
    vals.sort()
    # We don't know what algorithm sum() uses, so we'll do this the old fashioned way
    total = 0
    for i in range(len(vals)):
        total += vals[i]
    return total

values_l = []
values_u = []

for x in range(10):
    partials = []
    for n in range(x+2):
        for m in range(84-x+1):
            partials.append(math.comb(x + 1, n) * ((9 / 15400) ** n) * ((39 / 3850) ** (x + 1 - n))
                            * math.comb(84 - x, m) * ((3 / 392) ** m) * ((13 / 98) ** (84 - x - m)))
    partial_sum = custom_sum(partials)
    values_l.append(partial_sum * ((26 / 98) ** x))
    values_u.append(partial_sum * ((26 / 98) ** x) * math.comb(84, x))

print(custom_sum(values_l))
print(custom_sum(values_u))
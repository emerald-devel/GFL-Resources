import sys

# Starting out, sum up the probability branches of having only 2* as well as only 2* and ringleader
def start(charge, extra):
    return 28 * 27 * 26 / 100 / 99 / 98 * no3(charge, extra, 0, 6) + 28 * 27 * 1 / 100 / 99 / 98 * have3(charge, extra, 0, 6)

# You have a ringleader
def have3(charge, extra, time, reset):
    # End of banner, 56 means 12 full days = maint, you won't ever reach 56
    if time == 55:
        # Last attempt, so this is the terminal for the recursion
        if charge + extra == 1:
            return 3 / 4
        # Use a charge if you can
        if charge > 0:
            return 3 / 4 * 1 / 98 * have3(charge - 1, extra, time, reset) + 3 / 4 * 26 / 98 * no3(charge - 1, extra, time, reset)
        # Otherwise use an extra charge
        elif extra > 0:
            return 3 / 4 * 1 / 98 * have3(charge, extra - 1, time, reset) + 3 / 4 * 26 / 98 * no3(charge, extra - 1, time, reset)
        else:
            print("Error, why am I here")
            sys.exit(1)
    # No charge, wait to fail to capture ringleader
    if charge == 0:
        return have3(charge + 1, extra, time + 1, max(reset - 1, 0))
    # Failed to capture ringleader, then draw either a 2* or 3*, and try again
    return 3 / 4 * 1 / 98 * have3(charge - 1, extra, time, reset) + 3 / 4 * 26 / 98 * no3(charge - 1, extra, time, reset)

# All 2*
def no3(charge, extra, time, reset):
    # Reset if we can
    # We will always do this reset with at least 1 charge remaining, so no worries
    if reset == 0:
        return 28 * 27 * 26 / 100 / 99 / 98 * no3(charge, extra, time, 6) + 28 * 27 * 1 / 100 / 99 / 98 * have3(charge, extra, time, 6)
    # End of banner, 56 means 12 full days = maint, you won't ever reach 56
    if time == 55:
        # Last attempt, so this is the terminal for the recursion
        if charge + extra == 1:
            return 1 / 2
        # Use a charge if you can
        if charge > 0:
            return 1 / 2 * 1 / 98 * have3(charge - 1, extra, time, reset) + 1 / 2 * 26 / 98 * no3(charge - 1, extra, time, reset)
        # Otherwise use an extra charge
        elif extra > 0:
            return 1 / 2 * 1 / 98 * have3(charge, extra - 1, time, reset) + 1 / 2 * 26 / 98 * no3(charge, extra - 1, time, reset)
        else:
            print("Error, why am I here")
            sys.exit(1)
    # Not full charge, try not to use
    if charge < 14:
        return no3(charge + 1, extra, time + 1, max(reset - 1, 0))
    # Failed to capture, then draw either a 2* or 3*, and try again
    return 1 / 2 * 1 / 98 * have3(charge - 1, extra, time, reset) + 1 / 2 * 26 / 98 * no3(charge - 1, extra, time, reset)

print(start(14, 16))
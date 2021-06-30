import random

# Let 0 denote 1* units, 1 denote 2* units and 2 denote 3* units
# These are the probabilities of capturing the unit
prob = [1, 0.5, 0.25]
# Populate the pool with units
units = [2]
for i in range(71):
    units.append(0)
for i in range(28):
    units.append(1)
# These are the amount of charges you have
charge = 14
# This tracks the number of 12 hr time frames that have passed
time = 0
# Set the number of times you want to run this simulator
runs = 100000
# Track the number of successful runs
success = 0
max_charge = 14
max_time = 60
# Reset downtime
reset = 6

# Function to pick 3 units from the pool and display them
def pick_units(pool):
    display = []
    for i in range(min(3, len(pool))):
        display.append(pool.pop(random.randint(0, len(pool) - 1)))
    display.sort()
    return display

# Function to simulate a capture. Returns 1 for a successful capture, 0 otherwise
def capture(id):
    attempt = random.random()
    if attempt <= prob[id]:
        return 1
    return 0

for i in range(runs):
    print("Sim #" + str(i))
    # Make a copy of the units since we want to modify the list directly
    pool = units.copy()
    # The first displayed units when the banner starts
    display = pick_units(pool)
    # We will assume a 30 day period for this
    while(time < max_time):
        # Check if we can reset
        if reset == 0:
            # Check if we want to reset, which is if we have no boss
            if display[2] != 2:
                # Put the units back into the pool
                pool += display
                # Pick another 3 units
                display = pick_units(pool)
                # Reset the reset timer
                reset = 6

        # If we have charges, maybe do a capture
        if charge > 0:
            # If the boss appeared, try capturing it
            if display[2] == 2:
                pick = 2
                result = capture(2)
            # Otherwise, if there is a 1* unit, go for it
            elif display[0] == 0:
                pick = 0
                result = capture(0)
            # If there are only 2* units, check if we are at max charges.
            # Only attempt capturing a 2* when at max charge
            elif charge == max_charge:
                pick = 0
                result = capture(1)
            # Otherwise, don't do a capture
            else:
                pick = -1
            
            # Check if we did a capture
            if pick != -1:
                # Reduce charges
                charge -= 1
                # Success
                if result == 1:
                    # If we captured the boss, end the simulation
                    if pick == 2:
                        success += 1
                        print("Success\n")
                        break
                    # Otherwise, put a new unit to display
                    else:
                        display.append(pool.pop(random.randint(0, len(pool) - 1)))
                        display.sort()
                # Failure
                else:
                    # Return the unit to the pool
                    pool.append(display.pop(pick))
                    # Grab another unit to display
                    display.append(pool.pop(random.randint(0, len(pool) - 1)))
                    display.sort()
            # We did not do a capture, wait 12 hrs
            else:
                time += 1
                charge += 1
                if reset > 0:
                    reset -= 1
        # No charges, wait 12 hours
        else:
            time += 1
            charge += 1
            if reset > 0:
                reset -= 1
    # If we reached this part, it means the simulation failed to capture a boss
    print("Failure\n")

print(str(success) + " out of " + str(runs) + " runs are successful.")
print("Probability: " + str(success / runs * 100) + "%")

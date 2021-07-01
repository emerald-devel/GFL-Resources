import random

# The class that contains the state of a PA Banner Simulation Run
class PARun(object):
    # Start up the simulator
    def __init__(self, max_time = 56, detail = False, charge = 14, reset = 6, reset_prio = True):
        # Stores the information on whether to print the simulation in detail or not
        self.detail = detail
        # Let 0 denote 1* units, 1 denote 2* units and 2 denote 3* units
        # These are the probabilities of capturing the unit
        self.prob = [1, 0.5, 0.25]
        # Keeps the count of the units remaining, for easy access
        self.count = [71, 28, 1]
        # Populate the pool with units from a banner
        # There are 71 1* units, 28 2* units and 1 3* ringleader
        self.pool = [0] * 71 + [1] * 28 + [2]
        # The number of max charges you can store up at any point in time
        self.max_charge = 14
        # In this simulation, a unit of time = 12 hours
        # The maximum number of 12 hour intervals for the banner period
        # By default, it assumes 28 days, or 56 units of time
        self.max_time = max_time
        # The initial amount of charge to start the simulation with
        self.charge = 14
        # The number of charges used
        self.used = 0
        # The starting time period, which is time 0
        self.time = 0
        # The starting display refresh intervals
        # We assume that the refresh starts with the 72 hour countdown
        # Which is 6 time units
        self.reset = 6
        # Initialize the displayed units from the current pool
        self.display = []
        self.fill_display()
        # This determines if we should prioritize resetting whenever there is no boss
        # If False, the simulation will prioritize clearing 1* units before resetting
        self.reset_prio = reset_prio
        # Denotes if the ringleader is captured
        self.complete = False
        # Denotes if we encountered the ringleader at all
        self.encounter = False

    # Function to fill in an empty display
    def fill_display(self):
        # Since we terminate as soon as the boss is captured
        # We will never go below 3 units to display
        for i in range(3):
            self.pick_unit()
        # Sort the display. This is very important to simplify the code
        self.display.sort()

    # Function to pick a unit from the pool and add to display
    def pick_unit(self):
        self.display.append(self.pool.pop(random.randint(0, len(self.pool) - 1)))

    # Prints the state of the simulation in the current step
    def print_step_header(self):
        print("Day:", self.time / 2)
        print("1* units remaining:", self.count[0])
        print("2* units remaining:", self.count[1])
        print("Total units remaining:", sum(self.count))
        print("Charges remaining:", self.charge)
        print("Reset cooldown:", self.reset / 2)
        print("Currently displayed units:", self.display)

    # Increments the time period (i.e. wait 12 hours)
    def inc(self):
        if self.detail:
            print("Action: Do nothing for 12 hours")
        # Increase the time by 1 unit
        self.time += 1
        # Gain 1 charge ONLY IF we did not reach the end of the banner
        if self.time < self.max_time:
            self.charge += 1
        # If reset cooldown has not ended, shorten it
        if self.reset > 0:
            self.reset -= 1

    # Attempts a capture
    def capture(self, unit):
        if self.detail:
            print("Action: Try to catch a " + str(unit + 1) + "* unit")
        # Use a charge
        self.charge -= 1
        self.used += 1
        # Try catching it
        attempt = random.random()
        if self.detail:
            print("Dice roll:", attempt)
        # Check if the attempt was successful
        success = False
        if attempt <= self.prob[unit]:
            success = True
        if success:
            if self.detail:
                print("Capture success")
            # Successfully captured the ringleader
            if unit == 2:
                self.complete = True
            # Successfully captured a non-ringleader
            else:
                # 3* unit is in position 2, 1* unit is in position 0, 2* unit is in position 1 (because you only capture 2* when it's all 2*)
                # So we can use the unit type as the index too
                # Remove the unit from the display
                del self.display[unit]
                # Pick another unit and add it to the display
                self.pick_unit()
                self.display.sort()
                # Reduce the count of the units
                self.count[unit] -= 1
        # Failed to capture
        else:
            if self.detail:
                print("Capture failure")
            # Return the unit back to the pool
            self.pool.append(self.display.pop(unit))
            # Pick another unit and add it to the display
            self.pick_unit()
            self.display.sort()
            
    # Resets the display pool
    def reset_display(self):
        if self.detail:
            print("Action: Perform a display reset")
        # Add the units back into the pool
        self.pool += self.display
        # Empty the display
        self.display = []
        # Refill the display
        self.fill_display()
        # Reset the display reset cooldown timer
        self.reset = 6
        
    # Performs a step of action
    def step(self):
        if self.detail:
            self.print_step_header()
        # If you have no charges, the only thing you can do is to wait 12 hours
        if self.charge == 0:
            self.inc()
        # If a boss is on display, try to capture it
        elif self.display[2] == 2:
            self.encounter = True
            self.capture(2)
        # If 1* units are prioritized, try capturing them
        elif not self.reset_prio and self.display[0] == 0:
            self.capture(0)
        # If reset is available, perform a reset
        elif self.reset == 0:
            self.reset_display()
        # If resets are prioritized and there are no resets, try capturing a 1* unit
        elif self.display[0] == 0:
            self.capture(0)
        # If you are here, it means that there are only 2* units on display
        # We only catch them if
        # - we have max charges
        # - we are at the end of the banner
        elif self.charge == self.max_charge or self.time == self.max_time:
            self.capture(1)
        # We cannot do anything else, so we wait for 12 hours
        else:
            self.inc()
        if self.detail:
            print("")

    # Perform a full simulation
    def run(self): 
        if self.detail:
            print("Simulation start")
        # Just perform steps while there is still time and we have not captured the ringleader
        while(self.time <= self.max_time and not self.complete):
            self.step()
        # If we succeed, return the total number of charges used
        # TODO: Expand this section if we want to return more metadata and metrics
        # TODO: Collect the number of encounters needed to capture the ringleader
        if self.complete:
            return self.used
        # We will use -1 to denote encountering but failing to capture
        elif self.encounter:
            return -1
        # We will use -2 to denote never encountering the ringleader
        else:
            return -2

# Modify the parameters if you need to do so
max_time = 56
charge = 14
reset = 6
# A test run with detailed prints
myrun = PARun(max_time, True, charge, reset, True)
myrun.run()

# Experimenting
runs = 100000
success = 0
encounter = 0
# Scenario 1: reset whenever there is no boss
print("Prioritize resetting")
for i in range(runs):
    myrun = PARun(max_time, False, charge, reset, True)
    result = myrun.run()
    if result > 0:
        success += 1
    if result != -2:
        encounter += 1
print(str(encounter) + " out of " + str(runs) + " had boss encounters.")
print("Probability: " + str(encounter / runs * 100) + "%")
print(str(success) + " out of " + str(runs) + " runs are successful.")
print("Probability: " + str(success / runs * 100) + "%")
print("")

success = 0
encounter = 0
# Scenario 2: reset only when it's all 2*
print("Prioritize capturing 1*")
for i in range(runs):
    myrun = PARun(max_time, False, charge, reset, False)
    result = myrun.run()
    if result > 0:
        success += 1
    if result != -2:
        encounter += 1
print(str(encounter) + " out of " + str(runs) + " had boss encounters.")
print("Probability: " + str(encounter / runs * 100) + "%")
print(str(success) + " out of " + str(runs) + " runs are successful.")
print("Probability: " + str(success / runs * 100) + "%")

import random

# The class that contains the state of a PA Banner Simulation Run
class PARun(object):
    # Initialize the banner
    def __init__(self, banner, max_time = 56, detail = False, charge = 14, reset = 6, prio_cutoff = 1, reset_prio = 1, store_prio = 2):
        # Stores the information on whether to print the simulation in detail or not
        self.detail = detail
        # Let 0 denote 1* units, 1 denote 2* units and 2 denote 3* units
        # These are the probabilities of capturing the unit
        self.prob = [-1, 1, 0.5, 0.25]
        # Keeps the count of the units of each rarity remaining, for easy access
        self.count = [0, 0, 0, 0]
        # The pool contains all the remaining units
        self.pool = []
        # Keeps the count of the units of each priority level remaining, used to determine simulation success
        self.prio_count = [0]

        # Populate the pool
        for i in banner:
            self.pool += [i] * i['count']
            self.count[i['rarity']] += i['count']
            if len(self.prio_count) < i['prio'] + 1:
                self.prio_count += [0] * (i['prio'] + 1 - len(self.prio_count))
            self.prio_count[i['prio']] += i['count']

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

        # Determines which units need to be captured completely before success
        # For example, prio_cutoff = 1 means all priority 1 units need to be captured
        # Before the banner run is considered a success
        self.prio_cutoff = prio_cutoff
        # Determines which units are prioritized before using a reset
        # For example, reset_prio = 2 means the algorithm does not do a reset
        # as long as priority 1 and 2 units are on display
        self.reset_prio = reset_prio
        # This determines which units to capture instead of doing a timeskip
        # For example, store_prio = 2 means the algorithm does not do a timeskip
        # as long as priority 1 and 2 units are on display
        self.store_prio = store_prio

        # Denotes if the ringleader is captured
        self.complete = False
        # Denotes if we encountered the ringleader at all
        self.encounter = False

    def sort_key(self, e):
        return e['prio']

    # Function to fill in an empty display
    def fill_display(self):
        # Since we terminate as soon as the boss is captured
        # We will never go below 3 units to display
        for i in range(3):
            self.pick_unit()
        # Sort the display. This is very important to simplify the code
        self.display.sort(key = self.sort_key)

    # Function to pick a unit from the pool and add to display
    def pick_unit(self):
        self.display.append(self.pool.pop(random.randint(0, len(self.pool) - 1)))

    # Pretty prints the display
    def print_display(self):
        string = "["
        for i in self.display:
            string += i['name'] + " (" + str(i['rarity']) + "*), "
        return string[:-2] + "]"

    # Prints the state of the simulation in the current step
    def print_step_header(self):
        print("Day:", self.time / 2)
        print("Units remaining (rarity):", self.count[1:])
        print("Units remaining (priority):", self.prio_count[1:])
        print("Total units remaining:", sum(self.count))
        print("Charges remaining:", self.charge)
        print("Reset cooldown:", self.reset / 2)
        print("Currently displayed units:", self.print_display())

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
    def capture(self):
        unit = self.display[0]
        if self.detail:
            print("Action: Try to catch a " + str(unit['rarity']) + "* " +  unit['name'])
        # Use a charge
        self.charge -= 1
        self.used += 1
        # Note down if we encountered the ringleader
        if unit['rarity'] == 3:
            self.encounter = True
        # Try catching it
        attempt = random.random()
        if self.detail:
            print("Dice roll:", attempt)
        # Check if the attempt was successful
        success = False
        if attempt <= self.prob[unit['rarity']]:
            success = True
        if success:
            if self.detail:
                print("Capture success")
            self.count[unit['rarity']] -= 1
            self.prio_count[unit['prio']] -= 1
            # We will always be capturing the leftmost unit, so we can delete it 
            del self.display[0]
            # Pick another unit and add it to the display
            self.pick_unit()
            self.display.sort(key = self.sort_key)
            # Reduce the count of the units
        # Failed to capture
        else:
            if self.detail:
                print("Capture failure")
            # Return the unit back to the pool
            self.pool.append(self.display.pop(0))
            # Pick another unit and add it to the display
            self.pick_unit()
            self.display.sort(key = self.sort_key)
            
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

    # Checks if we have completed the simulation
    def check_complete(self):
        if sum(self.prio_count[0 : self.prio_cutoff + 1]) == 0:
            self.complete = True
        
    # Performs a step of action
    def step(self):
        if self.detail:
            self.print_step_header()
        # If you have no charges, the only thing you can do is to wait 12 hours
        if self.charge == 0:
            self.inc()
        # If a priority unit is on display, try to capture it
        elif self.display[0]['prio'] <= self.reset_prio:
            self.capture()
        # If reset is available, perform a reset
        elif self.reset == 0:
            self.reset_display()
        # If a lower priority unit is on display, try to capture it
        elif self.display[0]['prio'] <= self.store_prio:
            self.capture()
        # If you are here, it means that you've reached store_prio
        # At this point, captures are only made if one of the following holds:
        # - we have max charges
        # - we are at the end of the banner
        elif self.charge == self.max_charge or self.time == self.max_time:
            self.capture()
        # We cannot do anything else, so we wait for 12 hours
        else:
            self.inc()
        if self.detail:
            print("")
        self.check_complete()

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
prio_cutoff = 1
reset_prio = 1
store_prio = 2

# Define the Scarecrow banner
scarecrow = [{'name': 'Scarecrow', 'rarity': 3, 'prio': 1, 'count': 1},
             {'name': 'Brute', 'rarity': 2, 'prio': 3, 'count': 9},
             {'name': 'Dragoon', 'rarity': 2, 'prio': 3, 'count': 9},
             {'name': 'Aegis', 'rarity': 2, 'prio': 3, 'count': 10},
             {'name': 'Ripper', 'rarity': 1, 'prio': 2, 'count': 10},
             {'name': 'Vespid', 'rarity': 1, 'prio': 2, 'count': 10},
             {'name': 'Guard', 'rarity': 1, 'prio': 2, 'count': 10},
             {'name': 'Jaeger', 'rarity': 1, 'prio': 2, 'count': 10},
             {'name': 'Striker', 'rarity': 1, 'prio': 2, 'count': 10},
             {'name': 'Scout', 'rarity': 1, 'prio': 2, 'count': 10},
             {'name': 'Prowler', 'rarity': 1, 'prio': 2, 'count': 11}]

# A test run with detailed prints
myrun = PARun(scarecrow, max_time, True, charge, reset, prio_cutoff, reset_prio, store_prio)
myrun.run()

# Experimenting
runs = 100000
success = 0
encounter = 0
# Scenario 1: reset whenever there is no boss
print("Prioritize resetting")
for i in range(runs):
    myrun = PARun(scarecrow, max_time, False, charge, reset, prio_cutoff, reset_prio, store_prio)
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
    myrun = PARun(scarecrow, max_time, False, charge, reset, prio_cutoff, 2, store_prio)
    result = myrun.run()
    if result > 0:
        success += 1
    if result != -2:
        encounter += 1
print(str(encounter) + " out of " + str(runs) + " had boss encounters.")
print("Probability: " + str(encounter / runs * 100) + "%")
print(str(success) + " out of " + str(runs) + " runs are successful.")
print("Probability: " + str(success / runs * 100) + "%")
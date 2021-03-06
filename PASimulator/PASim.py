import random

# The class that contains the state of a PA Banner Simulation Run
class PASim(object):
    # Initialize the banner
    def __init__(self, banner, max_time = 56, detail = False, charge = 14, prio_cutoff = 1, reset_prio = 1, store_prio = 2,
                 extra = 16, svarog = 11, early_term = True, whale = False):
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
        # Keeps a summary of the successes and failures of every capture
        self.summary = {}

        # Store the starting amount of charges and Svarogs for reporting
        self.start_charge = charge
        self.start_extra = extra
        self.start_svarog = svarog

        # Store the name of the ringleader
        self.ringleader = banner[0]['name']
        self.banner = banner

        # Populate the pool
        for i in banner:
            self.pool += [i] * i['count']
            self.count[i['rarity']] += i['count']
            if len(self.prio_count) < i['prio'] + 1:
                self.prio_count += [0] * (i['prio'] + 1 - len(self.prio_count))
            self.prio_count[i['prio']] += i['count']
            self.summary[i['name']] = { 'success': 0, 'failure': 0 }

        # The number of max charges you can store up at any point in time
        self.max_charge = 14
        # In this simulation, a unit of time = 12 hours
        # The maximum number of 12 hour intervals for the banner period
        # By default, it assumes 28 days, or 56 units of time
        self.max_time = max_time

        # The initial amount of charge to start the simulation with
        self.charge = charge
        # The amount of extra charges a player has at the end of the banner.
        # Per data provided by Cleista, this is 16 a month
        self.extra = extra
        # The amount of svarogs a player has at the end of the banner.
        # Per data provided by Cleista, this is 11 a month
        self.svarog = svarog
        # The number of charges used before completing the target
        self.used = 0
        # The number of charges used throughout the simulation
        self.used_charge = 0
        # The number of extra charges used throughout the simulation
        self.used_extra = 0
        # The number of Svarogs used before completing the target
        self.used_svarog = 0
        # The starting time period, which is time 0
        self.time = 0
        # The starting display refresh intervals
        # The refresh starts with the 72 hour countdown for every banner
        # Which is 6 time units
        self.reset = 6
        # Determines if you plan to whale or not
        # A whaling simulation means that you will ensure success no matter what
        self.whale = whale
        # Notes down the amount of Svarogs whaled
        self.whale_svarog = 0

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

        # Determines if the simulation should terminate as soon as the goals are achieved
        self.early_term = early_term

        # Denotes if the ringleader is captured
        self.complete = False

    def sort_key(self, e):
        return e['prio']

    # Function to fill in an empty display
    def fill_display(self):
        # We will never reset when we have 3 or less units remaining
        for i in range(3):
            self.pick_unit()
        # Sort the display. This is very important to simplify the code
        self.display.sort(key = self.sort_key)

    # Function to pick a unit from the pool and add to display
    def pick_unit(self):
        # Only add to display if there are units in the pool remaining
        if(len(self.pool) > 0):
            self.display.append(self.pool.pop(random.randint(0, len(self.pool) - 1)))

    # Pretty prints the display
    def print_display(self):
        if len(self.display) == 0:
            return "[]"
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
        print("Regular impulses remaining:", self.charge)
        print("Extra impulses remaining:", self.extra)
        print("Svarogs remaining:", self.svarog)
        print("Svarogs whaled:", self.whale_svarog)
        print("Reset cooldown:", self.reset / 2)
        print("Currently displayed units:", self.print_display())

    # Increments the time period (i.e. wait 12 hours)
    def inc(self):
        if self.detail:
            print("Action: Do nothing for 12 hours")
        # Increase the time by 1 unit
        self.time += 1
        # Gain 1 charge ONLY IF we did not reach the end of the banner
        # The 1 charge earned at the end of banner will happen right after this banner ends
        # Therefore it cannot be used on this banner
        if self.time < self.max_time:
            self.charge += 1
        # If reset cooldown has not ended, shorten it
        if self.reset > 0:
            self.reset -= 1

    # Simulate using a Svarog
    def use_svarog(self):
        if self.svarog > 0:
            self.svarog -= 1
        else:
            self.whale_svarog += 1
        self.used_svarog += 1
        # Svarogs allow you to capture any unit in the pool at random, regardless if it is on display or not
        index = random.randint(0, sum(self.count) - 1)
        # If the unit captured is not displayed
        if index < len(self.pool):
            captured = self.pool.pop(index)
        # If the unit is displayed
        else:
            captured = self.display.pop(index - len(self.pool))
            # Replace a unit in display
            self.pick_unit()
            self.display.sort(key = self.sort_key)
        # Reduce the count of the units
        self.count[captured['rarity']] -= 1
        self.prio_count[captured['prio']] -= 1
        # Record the capture
        self.summary[captured['name']]['success'] += 1
        # Print the output
        if self.detail:
            print("Action: Captured a " + str(captured['rarity']) + "* " +  captured['name'] + " with a Svarog")

    # Attempts a capture
    def capture(self):
        unit = self.display[0]
        action = "Action: Try to catch a " + str(unit['rarity']) + "* " +  unit['name']
        # Use a regular charge if you have one
        if self.charge > 0:
            self.charge -= 1
            self.used_charge += 1
            action += " with a regular impulse"
        # Otherwise, use an extra charge if you have one
        elif self.extra > 0:
            self.extra -= 1
            self.used_extra += 1
            action += " with an extra impulse"
        # Otherwise, use a Svarog
        else:
            self.use_svarog()
            # Skip the rest of the logic as it does not apply to Svarog captures
            return
        # Record the charges used before completing the banner target
        if not self.complete:
            self.used += 1
        if self.detail:
            print(action)
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
            # Reduce the count of the units
            self.count[unit['rarity']] -= 1
            self.prio_count[unit['prio']] -= 1
            # Record the capture
            self.summary[unit['name']]['success'] += 1
            # We will always be capturing the leftmost unit, so we can delete it 
            del self.display[0]
            # Pick another unit and add it to the display
            self.pick_unit()
            self.display.sort(key = self.sort_key)
        # Failed to capture
        else:
            if self.detail:
                print("Capture failure")
            # Record the failure
            self.summary[unit['name']]['failure'] += 1
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

    # Check if we need to do a timeskip
    def should_inc(self):
        # If we are at the end of the banner, we plan to whale and the target is not complete
        # Do not timeskip
        if self.time == self.max_time and self.whale and not self.complete:
            return False
        # If we have completed our targets, we will try to save up to 14 charges
        # This will also prevent unnecessary usage of extra impulses and Svarogs
        if self.complete and self.charge < 14:
            return True
        # If we are out of charges, and we have not reached the end of the banner
        # We should do a timeskip
        if self.charge == 0 and self.time < self.max_time:
            return True
        # If we are at the end of a banner, and we literally cannot do anything else
        # We do a timeskip
        if self.charge == 0 and self.extra == 0 and self.svarog == 0 and self.time == self.max_time:
            return True
        return False
        
    # Performs a step of action
    def step(self):
        if self.detail:
            self.print_step_header()
        # Check if you should increase the time, and if so, do it
        if self.should_inc():
            self.inc()
        # If a priority unit is on display, try to capture it
        elif self.display[0]['prio'] <= self.reset_prio:
            self.capture()
        # If reset is available, perform a reset if there are more than 3 units remaining in the pool
        elif self.reset == 0 and sum(self.count) > 3:
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
        # Check if we have achieved our target
        self.check_complete()

    # Print summary of simulation
    def print_summary(self):
        # Summary header
        print("Simulation summary")
        print("Ringleader:", self.ringleader)
        # Print out the targets
        targets = "Targets: ["
        have_target = False
        for i in self.banner:
            if i['prio'] <= self.prio_cutoff:
                have_target = True
                targets += i['name'] + ', '
        if have_target:
            targets = targets[:-2] + ']'
        else:
            targets = targets[:-1] + 'None'
        print(targets)
        print('Initial regular impulses:', self.start_charge)
        print('Initial extra impulses:', self.start_extra)
        print('Initial Svarogs:', self.start_svarog)
        print('Banner period:', self.max_time / 2, 'days')
        print('Reset priority:', self.reset_prio)
        print('Store priority:', self.store_prio)
        if self.early_term:
            print('Simulation terminates as soon as targets are captured')
        else:
            print('Full simulation will be ran')
        if self.whale:
            print('Whaling mode on: will whale until targets are captured')
        else:
            print('F2P mode on')

        # Print completion status
        if self.complete:
            print('Targets captured')
        else:
            print('Targets not captured')
        print('Regular impulses used:', self.used_charge)
        print('Extra impulses used:', self.used_extra)
        print('Svarogs used:', self.used_svarog)
        if self.whale:
            print('Svarogs whaled:', self.whale_svarog)
        if self.complete:
            print('Total charges used before target completion:', self.used)
        print('Regular impulses remaining:', self.charge)
        print('Extra impulses remaining:', self.extra)
        print('Svarogs remaining:', self.svarog)
        
        # Print out summary of captured units
        print('Units captured:')
        for i in self.banner:
            print(i['name'] + ' (' + str(i['rarity']) + '*): '
                  + str(self.summary[i['name']]['success']) + '/' + str(i['count']) + ', '
                  + str(self.summary[i['name']]['failure']) + ' failures')

        print('')

    # Perform a full simulation
    def run(self): 
        if self.detail:
            print("Simulation start")
        # Just perform steps while there is still time and we have not completed the simulation
        # or opt to not terminate early
        while(self.time <= self.max_time and (not self.early_term or not self.complete)):
            self.step()
        
        # Proper simulation summary reporting
        if self.detail:
            self.print_summary()

        # Return a summary report of the simulation
        return { 'ringleader': self.ringleader,
                 'complete': self.complete,
                 'start_charge': self.start_charge,
                 'start_extra': self.start_extra,
                 'start_svarog': self.start_svarog,
                 'summary': self.summary,
                 'charge': self.charge,
                 'extra': self.extra,
                 'svarog': self.svarog,
                 'used': self.used,
                 'used_charge': self.used_charge,
                 'used_extra': self.used_extra,
                 'used_svarog': self.used_svarog,
                 'whale_svarog': self.whale_svarog,
                 'time': self.time }                 

# Testing (and sample) code on PARun usage
def run_test():
    # Modify the parameters if you need to do so
    max_time = 56
    charge = 14
    prio_cutoff = 1
    reset_prio = 1
    store_prio = 2
    extra = 16
    svarog = 11

    import banners
    scarecrow = banners.get_banner('Scarecrow', [1, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2])

    # A test run with detailed prints
    myrun = PASim(scarecrow, max_time, True, charge, prio_cutoff, reset_prio, store_prio, extra, svarog, True, False)
    report = myrun.run()
    # Testing without early termination
    myrun = PASim(scarecrow, max_time, True, charge, prio_cutoff, reset_prio, store_prio, extra, svarog, False, False)
    report = myrun.run()
    # Testing with whale
    myrun = PASim(scarecrow, max_time, True, charge, prio_cutoff, reset_prio, store_prio, extra, svarog, True, True)
    report = myrun.run()

    # Fun exercise: see how many runs capture Scarecrow as the 100th capture
    runs = 0
    for i in range(100000):
        myrun = PASim(scarecrow, max_time, False, charge, prio_cutoff, reset_prio, store_prio, extra, svarog, True, True)
        report = myrun.run()
        cleared = 0
        for i in report['summary']:
            cleared += report['summary'][i]['success']
        if cleared == 100:
            runs += 1
    print("Runs that captured Scarecrow as the 100th capture: " + str(runs) + "/100000 (" + str(runs / 10000) + "%)")
    print("")

    # Experimenting
    runs = 100000
    success = 0
    encounter = 0
    # Scenario 1: reset whenever there is no boss
    print("Prioritize resetting")
    for i in range(runs):
        myrun = PASim(scarecrow, max_time, False, charge, prio_cutoff, reset_prio, store_prio, extra, svarog, True, False)
        result = myrun.run()
        if result['complete']:
            success += 1
            encounter += 1
        elif result['summary']['Scarecrow']['failure'] > 0:
            encounter += 1
    print(str(encounter) + " out of " + str(runs) + " had boss encounters (" + str(encounter / runs * 100) + "%)")
    print(str(success) + " out of " + str(runs) + " runs are successful (" + str(success / runs * 100) + "%)")
    print("")

    success = 0
    encounter = 0
    # Scenario 2: reset only when it's all 2*
    print("Prioritize capturing 1*")
    for i in range(runs):
        myrun = PASim(scarecrow, max_time, False, charge, prio_cutoff, 2, store_prio, extra, svarog, True, False)
        result = myrun.run()
        if result['complete']:
            success += 1
            encounter += 1
        elif result['summary']['Scarecrow']['failure'] > 0:
            encounter += 1
    print(str(encounter) + " out of " + str(runs) + " had boss encounters (" + str(encounter / runs * 100) + "%)")
    print(str(success) + " out of " + str(runs) + " runs are successful (" + str(success / runs * 100) + "%)")
    print("")

if __name__ == "__main__":
    run_test()
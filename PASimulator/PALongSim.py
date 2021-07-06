import banners
import PASim

class PALongSim(object):
    # Initialize the long sim
    def __init__(self, banners_list, prios, sim_prios, time, detail, charge, extra, svarog, whale):
        # Provide the list of banners to be simulated
        self.banners_list = banners_list
        # Provide the priorities for each unit in each banner
        self.prios = prios
        # Provide the prio_cutoff, reset_prio and store_prio for each banner
        self.sim_prios = sim_prios

        # Determine the duration of each banner
        self.time = time
        # Determine if we should print run details
        self.detail = detail
        # Determine the amount of regular charges to start the simulation with
        self.charge = charge
        # Provide the amount of extra charges and svarogs to bank in every banner
        self.extra_ = extra
        self.svarog_ = svarog
        # Initialize extra charges and svarogs
        self.extra = extra
        self.svarog = svarog
        # Set the flag to determine if you want to whale or not
        self.whale = whale

        # The summary of the entire run
        self.summary = {}

    def run(self):
        for i in range(len(self.banners_list)):
            # Grab the banner with the given priority values
            banner = banners.get_banner(self.banners_list[i], self.prios[i])
            # Initialize the banner simulation
            myrun = PASim.PASim(banner, self.time, self.detail, self.charge, self.sim_prios[i][0], self.sim_prios[i][1],
                          self.sim_prios[i][2], self.extra, self.svarog, False, self.whale)
            # Run the simulation and print the report
            report = myrun.run()
            if self.detail:
                print(report)
                print("")
            self.summary[self.banners_list[i]] = report
            # You earn one charge during banner transition assuming optimal charges
            self.charge = report['charge'] + 1
            # Update the extra charges and svarogs you have
            self.extra = report['extra'] + self.extra_
            self.svarog = report['svarog'] + self.svarog_
        return self.summary

# Example test runs
def run_tests():
    mysim = PALongSim(['Executioner'] * 12, [[1, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2]] * 12, [[1, 1, 2]] * 12,
                      56, True, 9, 16, 11, False)
    mysim.run()
    banners_list = ['Executioner', 'Hunter', 'Intruder', 'Destroyer', 'Architect', 'Ouroboros',
                    'Alchemist', 'Dreamer', 'Gager', 'Judge', 'Agent', 'Adeline', 'Alina']
    prios = [[1, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2]] + [[1, 2, 4, 3]] * 12
    sim_prios = [[1, 1, 2]] + [[1, 2, 3]] * 12
    mysim = PALongSim(banners_list, prios, sim_prios, 56, True, 9, 16, 11, False)
    mysim.run()
    mysim = PALongSim(banners_list, prios, sim_prios, 56, False, 9, 16, 11, True)
    summary = mysim.run()
    for i in summary:
        print(summary[i])

if __name__ == '__main__':
    run_tests()
import matplotlib.pyplot as pt
import PALongSim

banners_list = ['Executioner', 'Hunter', 'Intruder', 'Destroyer', 'Architect', 'Ouroboros',
                'Alchemist', 'Dreamer', 'Gager', 'Judge', 'Agent', 'Adeline', 'Alina']
prios = [[1, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2]] + [[1, 2, 4, 3]] * 12
sim_prios = [[1, 1, 2]] + [[1, 2, 3]] * 12
runs = 1000000
charge = 9
extra = 10
svarog = 6
complete = [0] * (len(banners_list) + 1)

print('F2P success analysis')
for i in range(runs):
    mysim = PALongSim.PALongSim(banners_list, prios, sim_prios, 56, False, charge, extra, svarog, False)
    summary = mysim.run()
    target = 0
    for j in summary:
        if summary[j]['complete']:
            target += 1
    complete[target] += 1
    if runs // 100 > 0 and i % (runs // 100) == ((runs // 100) - 1):
        print(str((i + 1) // 10000) + '% complete')

pt.bar(range(len(complete)), complete)
pt.xlabel('Number of ringleaders caught')
pt.ylabel('Number of shikikans')
pt.title('F2P PA 13 Month Banner Simulation')
pt.savefig('f2p.png', bbox_inches='tight')
print(complete)

count = [0]

print('Whale amount analysis')
for i in range(runs):
    mysim = PALongSim.PALongSim(banners_list, prios, sim_prios, 56, False, charge, extra, svarog, True)
    summary = mysim.run()
    whaled = 0
    for j in summary:
        whaled += summary[j]['whale_svarog']
    if len(count) < whaled + 1:
        count += [0] * (whaled + 1 - len(count))
    count[whaled] += 1
    if runs // 100 > 0 and i % (runs // 100) == (runs // 100 - 1):
        print(str((i + 1) // 10000) + '% complete')

bins = ['0']
values = [count[0]]
input = count[1:]

index = 0
while len(input) > 0:
    bins += [str(index + 1) + '-' + str(index + 10)]
    if len(input) > 10:
        values += [sum(input[0:10])]
        input = input[10:]
    else:
        values += [sum(input)]
        input = []
    index += 10

pt.figure()
pt.bar(bins, values)
pt.xticks(bins, bins, rotation='vertical')
pt.xlabel('Number of Svarogs whaled')
pt.ylabel('Number of shikikans')
pt.title('Whale PA 13 Month Banner Simulation')
pt.savefig('whale.png', bbox_inches='tight')
print(count)
print(bins)
print(values)
print(sum(values))
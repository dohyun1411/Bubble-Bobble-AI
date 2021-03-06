import argparse, random, pickle, sys, time
from copy import deepcopy

import numpy as np
import matplotlib.pyplot as plt

from gamelauncher import GameLauncher
from config import *
from ga import *


parser = argparse.ArgumentParser()
parser.add_argument("--ga", type=int, default=1)
parser.add_argument("-c", "--checkpoint", action="store_true")
parser.add_argument("-t", "--test", action="store_true")
parser.add_argument("-n", "--noplot", action="store_true")
parser.add_argument('-m', '--mute', action="store_true")
parser.add_argument("-s", "--sub", type=int, default=17)
parser.add_argument('-p', '--pop', type=int, default=50)
parser.add_argument('--save', type=int, default=0)
args = parser.parse_args()

N_POP = args.pop
N_BEST = 5
N_CHILDREN = 5
PROB_MUT = 0.4

v = 100

if args.mute:
    ScreenConfig.volume = 0

if not args.test:
    genome_name = {}
    genomes = []
    # for i in range(300):
    #     for j in range(10):
    #         name = f"v53-{i}-{j}.pkl"
    #         try:
    #             with open(name, "rb") as f:
    #                 # genomes = pickle.load(f)
    #                 genome = pickle.load(f)
    #                 if genome.fitness > 70000:
    #                     genomes.append(genome)
    #                     genome_name[genome] = name
    #         except:
    #             continue
        # print(name)
        # print(f"Past Fitness: {genome.fitness:.2f}")
    # print([g.fitness for g in genomes], len(genomes))
    # names = ['v53-158-0.pkl', 'v53-203-0.pkl', 'v53-256-0.pkl', 'v53-204-0.pkl', 'v53-264-0.pkl']
    names = ['v53-158-0.pkl', 'v53-161-0.pkl', 'v53-167-0.pkl', 'v53-257-0.pkl', 'v53-203-0.pkl']
    for name in names:
        with open(name, 'rb') as f:
            genomes.append(pickle.load(f))

    genomes.sort(key=lambda x: x.fitness, reverse=True)
    # print(len(genomes))
    # for g in genomes[:10]:
    #     print(genome_name[g], g.fitness)
    if not args.ga:
        genomes = [Network()]
    gl = GameLauncher(ga=args.ga, genomes=genomes, best=args.ga)
    gl.run()
    print(f"Current Fitness: {Fitness.value}")
    # print([g for g in genomes])
    # for genome in genomes:
    #     print(f"Past Fitness: {genome.fitness:.2f}")
    #     gl = GameLauncher(ga=args.ga, genomes=[genome])
    #     # gl = GameLauncher(ga=True, genomes=genomes)
    #     gl.run()
    #     print(f"Current Fitness: {Fitness.value[0]:.2f}")
    print("Done")
    time.sleep(1)
    gl.quit()
    sys.exit()

if args.checkpoint:
    with open(f"n_gen{v}.txt", "r") as f:
        doc = f.read()
    n_gen = int(doc)
    with open(f"genomes{v}.pkl", "rb") as f:
        genomes = pickle.load(f)
    with open(f"bests{v}.pkl", "rb") as f:
        best_genomes = pickle.load(f)
    with open(f"max{v}.pkl", "rb") as f:
        max_fitness = pickle.load(f)
    with open(f"mmax{v}.pkl", "rb") as f:
        mmax_fitness = pickle.load(f)
    with open(f"mmmax{v}.pkl", "rb") as f:
        mmmax_fitness = pickle.load(f)
    with open(f"avg{v}.pkl", "rb") as f:
        avg_fitness = pickle.load(f)
    with open(f"med{v}.pkl", 'rb') as f:
        med_fitness = pickle.load(f)
    print(f"Past Generation {n_gen} - max: {max_fitness[-1]:.2f}, avg: {avg_fitness[-1]:.2f}, median: {med_fitness[-1]:.2f}")
else:
    n_gen = 0
    best_genomes = None
    genomes = [Network() for _ in range(N_POP)]
    max_fitness = []
    mmax_fitness = []
    mmmax_fitness = []
    avg_fitness = []
    med_fitness = []

if not args.noplot:
    fig = plt.figure()
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)
    plt.xlabel("Generation", fontsize=12)
    ax1.set_ylabel("Fitness", fontsize=12)
    ax2.set_ylabel("Fitness", fontsize=12)
    plt.show(block=False)

if not args.ga:
    genomes = [Network()]
while True:
    n_gen += 1
    if best_genomes is not None:
        genomes.extend(best_genomes)
    fitness_list = []
    # s, M, med = 0, 0, 0
    for i in range(0, len(genomes), args.sub):
        sub_genomes = genomes[i:i + args.sub]
        gl = GameLauncher(ga=args.ga, genomes=sub_genomes)
        # gl = GameLauncher(ga=True, genomes=sub_genomes)
        gl.run()
        fitness_list.extend(Fitness.value)
        # for i, f in enumerate(Fitness.value):
        #     sub_genomes[i].fitness = f
        # M = max(max(Fitness.value), M)
        # s += sum(Fitness.value)
        print(f"max: {max(Fitness.value):.2f}, avg: {sum(Fitness.value)/len(Fitness.value):.2f}, median: {np.median(np.array(Fitness.value)):.2f}")
    # s /= len(genomes)
    for i, f in enumerate(fitness_list):
        genomes[i].fitness = f
    # print(len(genomes), len(fitness_list))
    fitness_list.sort(reverse=True)
    fitness_arr = np.array(fitness_list)
    M = fitness_list[0]
    s = np.mean(fitness_arr)
    med = np.median(fitness_arr)
    # print(Fitness.dist[0] * 10e10)
    print(f"Generation {n_gen} - Max: {M:.2f}, Avg: {s:.2f}, Median: {med:.2f}")
    # print(fitness_list)
    if not args.noplot:
        max_fitness.append(M)
        mmax_fitness.append(fitness_list[1])
        mmmax_fitness.append(fitness_list[2])
        # print(mmax_fitness, fitness_list[1])
        avg_fitness.append(s)
        med_fitness.append(med)
        line1, = ax1.plot(np.array(list(range(1, n_gen + 1))), np.array(max_fitness), color='orangered')
        line4, = ax1.plot(np.array(list(range(1, n_gen + 1))), np.array(mmax_fitness), color='violet')
        line5, = ax1.plot(np.array(list(range(1, n_gen + 1))), np.array(mmmax_fitness), color='gold')
        line2, = ax2.plot(np.array(list(range(1, n_gen + 1))), np.array(avg_fitness), color='limegreen')
        line3, = ax2.plot(np.array(list(range(1, n_gen + 1))), np.array(med_fitness), color='deepskyblue')
        ax1.legend([line1, line4, line5], ['top1', 'top2', 'top3'])
        ax2.legend([line2, line3], ['avg', 'median'])
        fig.canvas.draw()
        fig.canvas.flush_events()

    genomes.sort(key=lambda x: x.fitness, reverse=True)
    # print([g.fitness for g in genomes])
    # print(f"Generation {n_gen}: Best Fitness {genomes[0].fitness}")

    best_genomes = []
    for i in range(N_BEST):
        genome = genomes[i]
        best_genomes.append(deepcopy(genome))
        if genome.fitness > 20000:
        # if True:
            name = f"v{v}-{n_gen}-{i}.pkl"
            with open(name, 'wb') as f:
                pickle.dump(genome, f)
    
    if args.save:
        with open(f"cp_best{v}.pkl", 'wb') as f:
            pickle.dump(best_genomes, f)
        with open(f"cp_genome{v}.pkl", 'wb') as f:
            pickle.dump(genomes, f)
        with open(f"cp_fit{v}.pkl", 'wb') as f:
            pickle.dump(fitness_list, f)

    # best_genomes = deepcopy(genomes[:N_BEST])
    # weights = [g.fitness for g in best_genomes]
    # m = min(weights)
    # weights = [w - m for w in weights]
    # best_genomes = random.choices(best_genomes, weights=weights, k=N_CHILDREN)
    
    for _ in range(N_CHILDREN):
        
        new_genome = deepcopy(best_genomes[0])
        a_genome = deepcopy(random.choice(best_genomes))
        b_genome = deepcopy(random.choice(best_genomes))

        # j = random.randint(0, new_genome.w1.shape[0] - 1)
        # ii = [a for a in range(new_genome.w1.shape[0])]
        # random.shuffle(ii)
        # for jj in range(j):
        #     i = ii[jj]
        #     cut = random.randint(0, new_genome.w1.shape[1])
        #     new_genome.w1[i, :cut] = a_genome.w1[i, :cut]
        #     new_genome.w1[i, cut:] = b_genome.w1[i, cut:]

        # j = random.randint(0, new_genome.w2.shape[0] - 1)
        # ii = [a for a in range(new_genome.w2.shape[0])]
        # random.shuffle(ii)
        # for jj in range(j):
        #     i = ii[jj]
        #     cut = random.randint(0, new_genome.w2.shape[1])
        #     new_genome.w2[i, :cut] = a_genome.w2[i, :cut]
        #     new_genome.w2[i, cut:] = b_genome.w2[i, cut:]

        i = random.randint(0, new_genome.w1.shape[0] - 1)
        cut = random.randint(0, new_genome.w1.shape[1])
        new_genome.w1[i, :cut] = a_genome.w1[i, :cut]
        new_genome.w1[i, cut:] = b_genome.w1[i, cut:]
    
        i = random.randint(0, new_genome.w2.shape[0] - 1)
        cut = random.randint(0, new_genome.w2.shape[1])
        new_genome.w2[i, :cut] = a_genome.w2[i, :cut]
        new_genome.w2[i, cut:] = b_genome.w2[i, cut:]

        # i = random.randint(0, new_genome.w3.shape[0] - 1)
        # cut = random.randint(0, new_genome.w3.shape[1])
        # new_genome.w3[i, :cut] = a_genome.w3[i, :cut]
        # new_genome.w3[i, cut:] = b_genome.w3[i, cut:]

        best_genomes.append(new_genome)

    # if M > 7500:
    #     PROB_MUT = 0.2
    #     mut_num = 2
    # else:
    #     PROB_MUT = 0.4
    #     mut_num = 1
    PROB_MUT = 0.2
    # mut_num = 4

    genomes = []
    while len(genomes) < (N_POP - N_CHILDREN - N_BEST):
        for bg in best_genomes:
            new_genome = deepcopy(bg)

            # j = random.randint(0, new_genome.w1.shape[0] - 1)
            # ii = [a for a in range(new_genome.w1.shape[0])]
            # random.shuffle(ii)
            # for jj in range(j):
            #     i = ii[jj]
            #     if random.uniform(0, 1) < PROB_MUT:
            #         new_genome.w1[i, :] += new_genome.w1[i, :] * np.random.randn(new_genome.w1.shape[1]) # * (random.uniform(0, 1) - 0.5) * 4

            # j = random.randint(0, new_genome.w2.shape[0] - 1)
            # ii = [a for a in range(new_genome.w2.shape[0])]
            # random.shuffle(ii)
            # for jj in range(j):
            #     i = ii[jj]
            #     if random.uniform(0, 1) < PROB_MUT:
            #         new_genome.w2[i, :] += new_genome.w2[i, :] * np.random.randn(new_genome.w2.shape[1])

            # for _ in range(4):
            #     for i in range(new_genome.w1.shape[0]):
            #         if random.uniform(0, 1) < PROB_MUT:
            #             new_genome.w1[i, :] += new_genome.w1[i, :] * np.random.randn(new_genome.w1.shape[1]) # * (random.uniform(0, 1) - 0.5) * 4
            #     for i in range(new_genome.w2.shape[0]):
            #         if random.uniform(0, 1) < PROB_MUT:
            #             new_genome.w2[i, :] += new_genome.w2[i, :] * np.random.randn(new_genome.w2.shape[1]) # * (random.uniform(0, 1) - 0.5) * 4
            #     for i in range(new_genome.w3.shape[0]):
            #         if random.uniform(0, 1) < PROB_MUT:
            #             new_genome.w3[i, :] += new_genome.w3[i, :] * np.random.randn(new_genome.w3.shape[1])

            for i in range(new_genome.w1.shape[0]):
                if random.uniform(0, 1) < PROB_MUT:
                    new_genome.w1[i, :] += new_genome.w1[i, :] * np.random.randn(new_genome.w1.shape[1]) # * (random.uniform(0, 1) - 0.5) * 4
            for i in range(new_genome.w2.shape[0]):
                if random.uniform(0, 1) < PROB_MUT:
                    new_genome.w2[i, :] += new_genome.w2[i, :] * np.random.randn(new_genome.w2.shape[1]) # * (random.uniform(0, 1) - 0.5) * 4
            # for i in range(new_genome.w3.shape[0]):
            #     if random.uniform(0, 1) < PROB_MUT:
            #         new_genome.w3[i, :] += new_genome.w3[i, :] * np.random.randn(new_genome.w3.shape[1])

            # for i in range(new_genome.w3.shape[0]):
            #     if random.uniform(0, 1) < PROB_MUT:
            #         new_genome.w3[i, :] += new_genome.w3[i, :] * (random.uniform(0, 1) - 0.5) * 3 + (random.uniform(0, 1) - 0.5)
            # for i in range(new_genome.w4.shape[0]):
            #     if random.uniform(0, 1) < PROB_MUT:
            #         new_genome.w4[i, :] += new_genome.w4[i, :] * np.random.randn()
            # for i in range(new_genome.w5.shape[0]):
            #     if random.uniform(0, 1) < PROB_MUT:
            #         new_genome.w5[i, :] += new_genome.w5[i, :] * np.random.randn()

            # mean = 20
            # stddev = 10
            # if random.uniform(0, 1) < PROB_MUT:
            #     new_genome.w1 += new_genome.w1 * np.random.randn(new_genome.input_layer, new_genome.hidden_layer1)
            # if random.uniform(0, 1) < PROB_MUT:
            #     new_genome.w2 += new_genome.w2 * np.random.randn(new_genome.hidden_layer1, new_genome.hidden_layer2)
            # if random.uniform(0, 1) < PROB_MUT:
            #     new_genome.w3 += new_genome.w3 * np.random.randn(new_genome.hidden_layer2, new_genome.output_layer)
            # if random.uniform(0, 1) < PROB_MUT:
            #     new_genome.w4 += new_genome.w4 * np.random.randn(new_genome.hidden_layer3, new_genome.output_layer)

            genomes.append(new_genome)
    
    if args.save:
        with open(f"n_gen{v}.txt", "w") as f:
            f.write(str(n_gen))
        with open(f"genomes{v}.pkl", 'wb') as f:
            pickle.dump(genomes, f)
        with open(f"bests{v}.pkl", 'wb') as f:
            pickle.dump(best_genomes, f)
        with open(f"max{v}.pkl", "wb") as f:
            pickle.dump(max_fitness, f)
        with open(f"mmax{v}.pkl", "wb") as f:
            pickle.dump(mmax_fitness, f)
        with open(f"mmmax{v}.pkl", "wb") as f:
            pickle.dump(mmmax_fitness, f)
        with open(f"avg{v}.pkl", 'wb') as f:
            pickle.dump(avg_fitness, f)
        with open(f"med{v}.pkl", 'wb') as f:
            pickle.dump(med_fitness, f)

gl.quit()

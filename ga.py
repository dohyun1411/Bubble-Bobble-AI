import enum, random

import numpy as np

from config import *


class Action(enum.Enum):

    STOP = 0
    LEFT = 1
    RIGHT = 2
    JUMP = 3
    LEFT_JUMP = 4
    RIGHT_JUMP = 5


class GA:

    monster_threshold = 200

    def __init__(self, player, enemy_group, bubble_group):
        self.player = player
        self.enemy_group = enemy_group
        self.bubble_group = bubble_group
    
    def menhattan_dist(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] + pos2[1])

    def fitness_func(self, solution, solution_idx):
        if (len(self.enemy_group) + len(self.bubble_group)) == 0:
            return 0
        
        fitness = 0
        player_pos = self.solution_player_pos(solution)
        target = None
        if self.bubble_group:
            target = list(self.bubble_group)[0]
            target_pos = target.pos
            fitness = 100. / self.menhattan_dist(player_pos, target_pos)
        
        for i, enemy in enumerate(self.enemy_group):
            if i == 0 and target is None:
                target = enemy
                target_pos = target.pos
                fitness = 1. / self.menhattan_dist(player_pos, target_pos)
            else:
                if abs(player_pos[0] - enemy.pos[0]) < GA.monster_threshold \
                    and abs(player_pos[1] - enemy.pos[1]) < GA.monster_threshold:
                    fitness -= 3.
                else:
                    fitness += 1.
        
        return fitness
    
    def solution_player_pos(self, action):
        if action is Action.STOP:
            return self.player.pos
        elif action is Action.LEFT:
            pass


class Network:
    def __init__(self):
        self.fitness = 0
        # self.input_layer = 10
        self.input_layer = 6
        self.hidden_layer1 = 4
        self.hidden_layer2 = 4
        # self.hidden_layer3 = 8
        # self.hidden_layer4 = 6
        self.output_layer = 3
        self.w1 = np.random.randn(self.input_layer, self.hidden_layer1)
        self.w2 = np.random.randn(self.hidden_layer1, self.hidden_layer2)
        self.w3 = np.random.randn(self.hidden_layer2, self.output_layer)
        # self.w4 = np.random.randn(self.hidden_layer3, self.output_layer)
        # self.w5 = np.random.randn(self.hidden_layer4, self.output_layer)
    
    def menhattan_dist(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] + pos2[1])

    def forward(self, player, enemy_group, bubble_group):
        px, py = player.pos
        ppx = px / ScreenConfig.width
        ppy = py / ScreenConfig.height
        pdx = player.dx / PlayerConfig.x_speed
        pdy = player.dy / 40
        
        i = player.i

        # out = []
        out = [ppx, ppy]
        tmp = []
        for bubble in bubble_group:
            if bubble.i != i: continue
            if not bubble.enemy: continue
            x, y = bubble.pos
            # print("BUBBLE", self.menhattan_dist((px, py), (x, y)), 10e10 / self.menhattan_dist((px, py), (x, y))**4)
            Fitness.dist[i] += 1 / (self.menhattan_dist((px, py), (x, y)) ** 4)
            x /= ScreenConfig.width
            y /= ScreenConfig.height
            dx = 0 if bubble.s == 'jumping' else bubble.dx
            dy = bubble.dy if bubble.s == 'jumping' else 0
            dx /= 8
            dy /= 2

            if pdx != 0 and (x - ppx > 0) == (pdx > 0):
                # print("CORRECT X")
                Fitness.x_dir[i] += 1
            elif pdx != 0 and (x - ppx > 0) != (pdx > 0):
                Fitness.x_dir[i] -= 1
            if pdy != 0 and (y - ppy > 0) == (pdy > 0):
                # print("CORRECT Y")
                Fitness.y_dir[i] += 1
            elif pdy != 0 and (y - ppy > 0) != (pdy > 0):
                # print("WRONG")
                Fitness.y_dir[i] -= 1

            if bubble.enemy.eid == 0:
                # print("bubble eid:", bubble.enemy.eid, x, y)
                out.extend([x, y])
                out.extend([dx, dy])
            else:
                tmp.extend([x, y])
                tmp.extend([dx, dy])

        for enemy in enemy_group:
            if enemy.i != i: continue
            if enemy.is_dead: continue
            x, y = enemy.pos
            # print("ENEMY", self.menhattan_dist((px, py), (x, y)), 10e10 / self.menhattan_dist((px, py), (x, y))**4)
            Fitness.dist[i] += 1 / (self.menhattan_dist((px, py), (x, y)) ** 4)
            Fitness.mid_gap[i] += 1 / (abs(px) ** 4 + abs(ScreenConfig.width - px) ** 4)
            # print("men:", self.menhattan_dist((px, py), (x, y)))
            x /= ScreenConfig.width
            y /= ScreenConfig.height
            dx = enemy.dx if enemy.status == 'walking' else 0
            dy = 0 if enemy.status in {'walking', 'standing'} else enemy.dy
            # print('enemy:', dx, dy)
            dx /= 8
            dy /= 2

            # print(x, ppx, pdx)
            if pdx != 0 and (x - ppx > 0) == (pdx > 0):
                # print("CORRECT X")
                Fitness.x_dir[i] += 1
            elif pdx != 0 and (x - ppx > 0) != (pdx > 0):
                Fitness.x_dir[i] -= 1
            # print(y, ppy, pdy)
            if pdy != 0 and (y - ppy > 0.02) == (pdy > 0):
                # print("CORRECT Y")
                Fitness.y_dir[i] += 1
            elif pdy != 0 and (y - ppy > 0.02) != (pdy > 0):
                # print("WRONG")
                Fitness.y_dir[i] -= 1

            if enemy.eid == 0:
                # print("eid:", enemy.eid, x, y)
                out.extend([x, y])
                out.extend([dx, dy])
            else:
                tmp.extend([x, y])
                tmp.extend([dx, dy])
        
        out.extend(tmp)
        # print(out)

        out = np.array(out)
        out = np.dot(out, self.w1)
        out = self.leaky_relu(out)
        # out = self.leaky_relu(out)
        # out = np.tanh(out)
        # print(out)
        # out = np.sinh(out)
        # print(out)
        out = np.dot(out, self.w2)
        out = self.leaky_relu(out)
        # out = self.leaky_relu(out)
        # out = np.tanh(out)
        out = np.dot(out, self.w3)
        # out = self.relu(out)
        # out = np.dot(out, self.w4)
        # out = self.relu(out)
        # out = np.dot(out, self.w5)
        out = self.softmax(out)
        # out = np.array(out)
        # out = np.dot(out, self.w1)
        # out = np.tanh(out)
        # out = np.dot(out, self.w2)
        # out = np.tanh(out)
        # out = np.dot(out, self.w3)
        # out = np.tanh(out)
        # out = np.dot(out, self.w4)
        # out = np.tanh(out)
        # out = np.dot(out, self.w5)
        # out = self.softmax(out)
        return out

    def relu(self, x):
        return x * (x >= 0)
    
    def leaky_relu(self, x, slope=0.02):
        return np.where(x > 0, x, x * slope)

    def softmax(self, x):
        z = x - max(x)
        numerator = np.exp(z)
        denominator = np.sum(numerator)
        return numerator / denominator


class Fitness:

    value = None
    dist = None
    mid_gap = None
    x_dir = None
    y_dir = None
    t_tmp = None
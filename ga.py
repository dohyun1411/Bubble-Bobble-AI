import numpy as np

from config import *


class Network:
    def __init__(self):
        self.fitness = 0
        # self.input_layer = 10
        self.input_layer = 6 # px, py, pdx, pdy, ex, ey
        self.hidden_layer1 = 4
        # self.hidden_layer2 = 6
        # self.hidden_layer3 = 8
        # self.hidden_layer4 = 6
        self.output_layer = 3
        self.w1 = np.random.randn(self.input_layer, self.hidden_layer1)
        self.w2 = np.random.randn(self.hidden_layer1, self.output_layer)
        # self.w3 = np.random.randn(self.hidden_layer2, self.output_layer)
        # self.w4 = np.random.randn(self.hidden_layer3, self.output_layer)
        # self.w5 = np.random.randn(self.hidden_layer4, self.output_layer)
    
    def menhattan_dist(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] + pos2[1])

    def forward(self, player, enemy_group, bubble_group):
        px, py = player.pos
        ppx = px / ScreenConfig.width
        ppy = py / ScreenConfig.height
        pdx = (player.dx + PlayerConfig.x_speed) / (2 * PlayerConfig.x_speed)
        pdy = (player.dy + 40) / 80
        
        i = player.i

        # out = []
        # out = [ppx, ppy, pdx, pdy]
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
            dx = (dx + 8) / 16
            dy = (dy + 2) / 4

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
            dx = (dx + 8) / 16
            dy = (dy + 2) / 4

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
        # out = self.leaky_relu(out)
        # out = self.leaky_relu(out)
        # out = np.tanh(out)
        # out = np.dot(out, self.w3)
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
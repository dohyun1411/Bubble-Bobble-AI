import os, sys
import random, math

import pygame

from config import *
from loader import Loader
from map import Map
from player import Player, DeadPlayer, Heart
from enemy import Enemy
from bubble import Bubble
from boom import Boom
from ga import *


class GameLauncher:

    def __init__(self, ga, genomes=None):
        # initialize
        pygame.init()
        pygame.display.set_caption('Simple Bubble Bobble')

        self.screen = pygame.display.set_mode(ScreenConfig.width_height)
        self.clock = pygame.time.Clock()

        self.mode = ScreenConfig.EASY
        
        self.genomes = genomes
        self.n_gen = len(genomes)
        # print(f"{self.n_gen} sub genomes", end=' ')

        self.round = [1 for _ in range(self.n_gen)]
        self.new_round = [True for _ in range(self.n_gen)]
        self.new_round_delay = [0 for _ in range(self.n_gen)]
        self.shooting_delay = [0 for _ in range(self.n_gen)]
        self.time = [ScreenConfig.max_time for _ in range(self.n_gen)]
        self.time_color = [ScreenConfig.time_color for _ in range(self.n_gen)]
        self.gameover = [False for _ in range(self.n_gen)]
        self.initial_gameover_sound = [True for _ in range(self.n_gen)]
        # self.running = [True for _ in range(self.n_gen)]
        self.restart = [True for _ in range(self.n_gen)]
        self.player_score = [0 for _ in range(self.n_gen)]

        # self.round = 1
        # self.new_round = True
        # self.new_round_delay = 0
        # self.shooting_delay = 0
        # self.time = ScreenConfig.max_time
        # self.time_color = ScreenConfig.time_color
        # self.gameover = False
        # self.initial_gameover_sound = True
        self.running = True
        # self.restart = False
        self.blinking_delay = 0

        # self.player_score = 0

        # load bgm
        self.bgm = pygame.mixer.music
        self.bgm.load(os.path.join(Loader.sound_path, 'main_theme.mp3'))
        self.bgm.set_volume(ScreenConfig.volume)

        # load sound effect
        self.sounds = Loader.load_sounds()
        for sound in self.sounds.values():
            sound.set_volume(ScreenConfig.volume)

        # load background image
        self.background_images = Loader.load_background_images()
        self.background_image = self.background_images[ScreenConfig.background_image]
        self.background_pos = ScreenConfig.background_pos

        # load map image
        self.map_image = Loader.load_brick_images()['brick']

        # load player images and sounds
        Player.group.empty()
        DeadPlayer.group.empty()
        self.player_images = Loader.load_player_images()
        # self.player = Player(self.player_images, self.sounds)
        
        # load enemy images
        Enemy.group.empty()
        # Enemy.count = 0
        # Enemy.score = 0
        self.enemy_images = Loader.load_enemy_images()

        # load bubble images
        Bubble.group.empty()
        self.bubble_images = Loader.load_bubble_images()

        Boom.group.empty()

        self.ga = ga
        # if ga: # ga setup
        # self.restart = True
        # self.shooting_delay = 0
        self.player = []
        for i, genome in enumerate(genomes):
            self.player.append(Player(self.player_images, self.sounds, i, genome))
            
        self.init = True
        Fitness.value = [0 for _ in range(self.n_gen)]
        Fitness.dist = [0. for _ in range(self.n_gen)]
        Fitness.mid_gap = [0. for _ in range(self.n_gen)]
        Fitness.x_dir = [0. for _ in range(self.n_gen)]
        Fitness.y_dir = [0. for _ in range(self.n_gen)]
        Fitness.t_tmp = [[False, False] for _ in range(self.n_gen)]
        self.t = [0 for _ in range(self.n_gen)]
        BubbleConfig.gameover = [0 for _ in range(self.n_gen)]
        Enemy.bonus_time = [0 for _ in range(self.n_gen)]
        # self.text_time = 0
        Enemy.count = [0 for _ in range(self.n_gen)]
        Enemy.score = [0 for _ in range(self.n_gen)]
        self.num_left = self.n_gen
        self.elapsed = [0 for _ in range(self.n_gen)]
        self.corner = 0
        
    def run(self):
        # if self.ga:
        if True:
            self._ga_run()
        else:
            self._run()
    
    def _ga_run(self):
        # play BGM
        self.bgm.play(-1)

        # event loop
        while self.running:
            self.clock.tick(ScreenConfig.fps)
            if not self.ga:
                self.handle_event()
            
            # update time
            # if not self.gameover and self.new_round_delay >= ScreenConfig.new_round_delay \
            #     and not Enemy.is_all_flying():

            # if not self.gameover:
            #     self.time = self.time - 1 + Enemy.bonus_time * ScreenConfig.fps
            #     Enemy.bonus_time = 0
            
            for i in range(self.n_gen):
                # print("player", self.player[i].dx, self.player[i].dy)
                if self.gameover[i]:
                    self.time[i] = 0
                else:
                    self.time[i] = self.time[i] - 1 + Enemy.bonus_time[i] * ScreenConfig.fps
                    self.elapsed[i] += 1
                    Enemy.bonus_time[i] = 0
                
                if Fitness.t_tmp[i][0]:
                    s = min(6700 / (math.sqrt(self.elapsed[i] - self.t[i] + 1e-9)), 500)
                    # print("ELAPSED1", (self.elapsed[i] - self.t[i]) // 60)
                    # print("s1", s)
                    Fitness.value[i] +=s
                    self.t[i] = self.elapsed[i]
                    # print("check", self.t[i])
                    Fitness.t_tmp[i][0] = False
                if Fitness.t_tmp[i][1]:
                    # print("hey", self.time[i])
                    s = min(6700 / (math.sqrt(self.elapsed[i] - self.t[i] + 1e-9)), 350)
                    # print("s2", s)
                    # print("ELAPSED2", (self.elapsed[i] - self.t[i]) // 60)
                    Fitness.value[i] +=s
                    # print(s)
                    self.t[i] = self.elapsed[i]
                    Fitness.t_tmp[i][1] = False
            
                # update score
                # if not self.gameover:
                #     self.player_score = Enemy.score
            
                if not self.gameover[i]:
                    self.player_score[i] = Enemy.score[i]

                if self.new_round[i]:

                    if not self.gameover[i]:
                        self.time[i] = ScreenConfig.max_time

                    # create map
                    Map.group.empty()
                    Map(self.map_image)

                    # create enemy
                    for j in range(1):
                        enemy = Enemy(self.enemy_images, self.round, eid=j, i=i)
                        # enemy.new_round_delay = 0
                    self.new_round[i] = False

                    self.new_round_delay[i] = 0

                # create heart
                # Heart.group.empty()
                # for i in range(self.player.life):
                #     Heart(ScreenConfig.heart_pos[i], self.player_images['heart'])

                # player action
                if self.player[i].status == 'ghost':
                    Player.group.remove(self.player[i])
                self.player[i].move()
                # self.player.new_round_delay = self.new_round_delay
                # self.new_round_delay += 1

                # dead player action
                # for dead_player in DeadPlayer.group:
                #     if dead_player.i == i:
                #         dead_player.fall()

                # enemy action
                for enemy in Enemy.group:
                    if enemy.i == i:
                        enemy.act_randomly()
            
                # bubble action
                for bubble in Bubble.group:
                    if bubble.i == i:
                        bubble.shoot()
            
                # boom action
                for boom in Boom.group:
                    if boom.i == i:
                        boom.act()
            
                # new round
                if Enemy.count[i] == 0:
                    self.new_round[i] = True
                    self.round[i] += 1
            
                # time warning
                if self.time[i] == ScreenConfig.warning_time:
                    # self.sounds['hurry'].set_volume(1)
                    # self.sounds['hurry'].play()
                    pass

                # game over
                try:
                    self.gameover[i] = self.player[i].life <= 0 or BubbleConfig.gameover[i] or self.time[i] <= 0
                except:
                    print(i)
                    print(self.player[i].life)
                    print(BubbleConfig.gameover[i])
                    print(self.time[i])
                    
                if self.initial_gameover_sound[i] and self.gameover[i]:
                    self.player[i].life = 0
                    for enemy in Enemy.group:
                        if enemy.i == i:
                            Enemy.group.remove(enemy)
                    for bubble in Bubble.group:
                        if bubble.i == i:
                            Bubble.group.remove(bubble)
                    self.num_left -= 1
                    # print(self.time[i])
                    # print('bo', Fitness.dist[i] * 10e10 * ScreenConfig.max_time / self.elapsed[i])
                    # Fitness.value[i] += Fitness.dist[i] * 10e10 * ScreenConfig.max_time / self.elapsed[i]
                    # Fitness.value[i] += Fitness.mid_gap[i] * 10e10 * ScreenConfig.max_time / self.elapsed[i]
                    # if self.time[i] <= 0:
                    #     Fitness.value[i] -= 200
                    # print("X", Fitness.x_dir[i], "Y", Fitness.y_dir[i])
                    # print("eX", Fitness.x_dir[i] * ScreenConfig.max_time / self.elapsed[i], "eY", Fitness.y_dir[i] * ScreenConfig.max_time / self.elapsed[i])
                    fit_dir = (0.1 * Fitness.x_dir[i] + 2 * Fitness.y_dir[i]) * ScreenConfig.max_time / self.elapsed[i]
                    # print(fit_dir)
                    # if fit_dir > 500:
                    #     fit_dir = 500
                    # elif fit_dir < -500:
                    #     fit_dir = -500
                    # print("dir", fit_dir)
                    # print(fit_dir)
                    Fitness.value[i] += fit_dir
                    if self.player[i].pos[0] < 30 or self.player[i].pos[0] > 1170:
                        Fitness.value[i] -= 200
                        self.corner += 1
                        # print(self.corner)
                    if BubbleConfig.gameover[i] or self.time[i] <= 0:
                        if BubbleConfig.gameover[i]:
                            self.player[i].sounds['damaged'].play()
                        Boom(self.player[i].images['boom'], self.player[i].pos, i=i)
                        # DeadPlayer(self.player[i].images['dead'], self.player[i].dir, self.player[i].pos, i=i)
                    if all(self.gameover):
                        self.bgm.stop()
                    # self.sounds['gameover'].play()
                    self.initial_gameover_sound[i] = False
                if all(self.restart) and all(self.gameover):
                    self.running = False

                if not self.gameover[i]:
                    # outputs
                    outputs = self.genomes[i].forward(self.player[i], Enemy.group, Bubble.group)
                    outputs = sorted(enumerate(outputs), key=lambda x: x[1], reverse=True)

                    # handle events
                    if self.ga == 1:
                        self.ga_handle_event(self.player[i], outputs)
                    elif self.ga == 2:
                        self.rule_handle_event(self.player[i])

            self.draw()
    
    def rule_handle_event(self, player):


        pass

    def ga_handle_event(self, player, outputs):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # quit
                self.running = False
                sys.exit()

        i = player.i
    
        self.player[i].dx_left = 0
        self.player[i].dx_right = 0
        if self.shooting_delay[i] > 0:
            self.shooting_delay[i] += 1
        if self.shooting_delay[i] > ScreenConfig.shooting_delay:
            self.shooting_delay[i] = 0
        # print(outputs)
        # if outputs[0] > 0.4:
        #     self.left(player)
        # if outputs[1] > 0.4:
        #     self.right(player)
        # if outputs[2] > 0.4 and not player.is_jumpping:
        #     self.jump(player)
        # for output_idx, _ in outputs:
        #     if output_idx == 0:
        #         # print('s')
        #         break
        #     elif output_idx == 1: # and self.player[i].pos[0] > 30:
        #         # print('l')
        #         self.left(player)
        #         break
        #     elif output_idx == 2: # and self.player[i].pos[0] < 1170:
        #         # print('r')
        #         self.right(player)
        #         break
        #     elif output_idx == 3 and not self.player[i].is_jumpping:
        #         # print('j')
        #         self.jump(player)
        #         break
            # elif output_idx == 4 and not self.player[i].is_jumpping:
            #     self.left(player)
            #     self.jump(player)
            #     break
            # elif output_idx == 5 and not self.player[i].is_jumpping:
            #     self.right(player)
            #     self.jump(player)
            #     break
        output_idx = outputs[0][0]
        if output_idx == 0:
            pass
        elif output_idx == 1:
            self.left(player)
        elif output_idx == 2:
            self.right(player)
        elif output_idx == 3:
            if self.player[i].is_jumpping:
                pass
            else:
                self.jump(player)
        elif output_idx == 4:
            if self.player[i].is_jumpping:
                self.left(player)
            else:
                self.left(player)
                self.jump(player)
        elif output_idx == 5:
            if self.player[i].is_jumpping:
                self.right(player)
            else:
                self.right(player)
                self.jump(player)

        self.shoot_when_enemy_is_nearby(player)
        # if self.shooting_cond(player):
        #     self.shoot(player)
        #     pass

    def left(self, player):
        player.dx_left = -PlayerConfig.x_speed
    
    def right(self, player):
        player.dx_right = PlayerConfig.x_speed
    
    def jump(self, player):
        player.dy = -PlayerConfig.y_speed
        player.is_jumpping = True
        self.sounds['jumping'].play()

    def shoot(self, player):
        player.shoot(self.bubble_images)
        i = player.i
        self.shooting_delay[i] = 1
    
    # def shooting_cond(self, player):
    #     return not self.new_round_delay < ScreenConfig.new_round_delay \
    #         and not 0 < player.damaged_delay < ScreenConfig.new_round_delay \
    #             and self.shooting_delay == 0
    
    def shooting_cond(self, player):
        i = player.i
        return self.shooting_delay[i] == 0

    # TODO
    def shoot_when_enemy_is_nearby(self, player):
        i = player.i
        px, py = player.pos
        pd = player.dir
        # print(f"{pd = }")
        for enemy in Enemy.group:
            if enemy.i != i: continue
            if enemy.is_dead: continue
            ex, ey = enemy.pos
            # print(px, pd, px + pd * 200, ex)
            if pd > 0: # 200? 40?
                if px + 200 > ex > px:
                    # print("XOK", py, ey)
                    if -50 < py - ey < 100:
                        if self.shooting_cond(player):
                            self.shoot(player)
            else:
                if px - 200 < ex  < px:
                    # print("XOK", py, ey)
                    if -50 < py - ey < 100:
                        if self.shooting_cond(player):
                            self.shoot(player)

    def _run(self): # TODO
        # play BGM
        self.bgm.play(-1)

        # event loop
        while self.running:
            self.clock.tick(ScreenConfig.fps)
            
            # update time
            # print(Enemy.bonus_time)
            if not self.gameover:
                self.time = self.time - 1 + Enemy.bonus_time * ScreenConfig.fps
                Enemy.bonus_time = 0
            
            # update score
            if not self.gameover:
                self.player_score = Enemy.score

            # handle events
            self.handle_event()

            if self.new_round:

                if not self.gameover:
                    self.time = ScreenConfig.max_time

                # create map
                Map.group.empty()
                Map(self.map_image)

                # create enemy
                if self.mode == ScreenConfig.EASY or self.mode == ScreenConfig.HARD: # TODO: EASY와 HARD 분리
                    for _ in range(2):
                        enemy = Enemy(self.enemy_images, self.round)
                        # enemy.new_round_delay = 0
                self.new_round = False

                # self.new_round_delay = 0

            # create heart
            Heart.group.empty()
            for i in range(self.player.life):
                Heart(ScreenConfig.heart_pos[i], self.player_images['heart'])

            # player action
            self.player.move()
            # self.player.new_round_delay = self.new_round_delay
            # self.new_round_delay += 1

            # dead player action
            for dead_player in DeadPlayer.group:
                dead_player.fall()

            # enemy action
            for enemy in Enemy.group:
                enemy.act_randomly()
            
            # bubble action
            for bubble in Bubble.group:
                bubble.shoot()
            
            # boom action
            for boom in Boom.group:
                boom.act()
            
            # new round
            if Enemy.count == 0:
                self.new_round = True
                self.round += 1
            
            # time warning
            if self.time == ScreenConfig.warning_time:
                self.sounds['hurry'].set_volume(1)
                self.sounds['hurry'].play()

            # game over
            self.gameover = self.player.life <= 0 or BubbleConfig.gameover or self.time <= 0
            if self.initial_gameover_sound and self.gameover:
                self.player.life = 0
                if BubbleConfig.gameover or self.time <= 0:
                    self.player.sounds['damaged'].play()
                    Boom(self.player.images['boom'], self.player.pos)
                    DeadPlayer(self.player.images['dead'], self.player.dir, self.player.pos)
                self.bgm.stop()
                self.sounds['gameover'].play()
                self.initial_gameover_sound = False
            if self.restart and self.gameover:
                self.running = False

            self.draw()
        
        # self.quit()     

    def handle_event(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT: # quit
                self.running = False
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q: # quit
                    self.running = False
                
                elif event.key == pygame.K_r and self.gameover: # restart
                    self.restart = True

                elif event.key == pygame.K_LEFT: # move left
                    self.player[0].dx_left = -PlayerConfig.x_speed

                elif event.key == pygame.K_RIGHT: # move right
                    self.player[0].dx_right = PlayerConfig.x_speed
                
                elif event.key == pygame.K_UP: # jump
                    if not self.player[0].is_jumpping:
                        self.player[0].dy = -PlayerConfig.y_speed
                        self.player[0].is_jumpping = True
                        self.sounds['jumping'].play()
                
                elif event.key == pygame.K_SPACE: # shoot bubble
                    self.player[0].shoot(self.bubble_images)
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT: # stop moving
                    self.player[0].dx_left = 0

                elif event.key == pygame.K_RIGHT: # stop moving
                    self.player[0].dx_right = 0

    def draw(self):
        # draw background
        self.screen.blit(self.background_image, self.background_pos)

        # draw map
        Map.group.draw(self.screen)

        # draw enemy
        # if self.new_round_delay < ScreenConfig.new_round_delay:
        #     if self.new_round_delay % ScreenConfig.blinking_interval in range(ScreenConfig.blinking_interval // 2):
        #         Enemy.group.draw(self.screen)
        # else:
        #     Enemy.group.draw(self.screen)
        Enemy.group.draw(self.screen)

        # draw dead player
        DeadPlayer.group.draw(self.screen)

        # draw player
        # if self.new_round_delay < ScreenConfig.new_round_delay \
        #     or 0 < self.player.damaged_delay < ScreenConfig.new_round_delay:
        #     if self.new_round_delay % ScreenConfig.blinking_interval in range(ScreenConfig.blinking_interval // 2):
        #         Player.group.draw(self.screen)
        # else:
        #     Player.group.draw(self.screen)
        Player.group.draw(self.screen)
        
        # draw bubble
        Bubble.group.draw(self.screen)

        # draw boom
        Boom.group.draw(self.screen)

        # draw heart
        Heart.group.draw(self.screen)
        # print([t // 60 for t in self.time])
        time = max(self.elapsed)
        
        # if time <= ScreenConfig.warning_time:
        #     time_color = ScreenConfig.RED
        # else:
        #     time_color = ScreenConfig.WHITE
        # self.time_color = ScreenConfig.WHITE

        # text time
        time_font = pygame.font.SysFont(ScreenConfig.time_font, ScreenConfig.time_size)
        time_text = time_font.render(f"TIME: {time // ScreenConfig.fps}", True, ScreenConfig.WHITE)
        time_rect = time_text.get_rect(center=ScreenConfig.time_pos)
        self.screen.blit(time_text, time_rect)

        # text round
        # round_font = pygame.font.SysFont(ScreenConfig.round_font, ScreenConfig.round_size)
        # round_text = round_font.render(f"ROUND {self.round}", True, ScreenConfig.round_color)
        # round_rect = round_text.get_rect(center=ScreenConfig.round_pos)
        # self.screen.blit(round_text, round_rect)

        # text player score
        # score = max(self.player_score)
        # score_font = pygame.font.SysFont(ScreenConfig.score_font, ScreenConfig.score_size)
        # player_score_text = score_font.render(f"SCORE: {score}", True, ScreenConfig.score_color)
        # player_score_rect = player_score_text.get_rect(center=ScreenConfig.player_score_pos)
        # self.screen.blit(player_score_text, player_score_rect)

        # text left
        score_font = pygame.font.SysFont(ScreenConfig.score_font, ScreenConfig.score_size)
        player_score_text = score_font.render(f"LEFT: {self.num_left}", True, ScreenConfig.score_color)
        player_score_rect = player_score_text.get_rect(center=ScreenConfig.player_score_pos)
        self.screen.blit(player_score_text, player_score_rect)

        # if self.gameover:
        #     # text gameover
        #     gameover_font = pygame.font.SysFont(ScreenConfig.gameover_font, ScreenConfig.gameover_size)
        #     gameover_text = gameover_font.render("GAME OVER", True, ScreenConfig.gameover_color)
        #     gameover_rect = gameover_text.get_rect(center=ScreenConfig.gameover_pos)
        #     self.screen.blit(gameover_text, gameover_rect)

            # test info
            # info_font = pygame.font.SysFont(ScreenConfig.info_font, ScreenConfig.info_size)
            # info_text = info_font.render("PRESS R TO RESTART", True, ScreenConfig.info_color)
            # info_rect = info_text.get_rect(center=ScreenConfig.info_pos)
            # if self.blinking_delay in range(2 * ScreenConfig.max_blinking_delay // 3):
            #     self.screen.blit(info_text, info_rect)
            # self.blinking_delay += 1
            # self.blinking_delay %= ScreenConfig.max_blinking_delay

        pygame.display.update()

    def quit(self):
        pygame.quit()
    
    def start(self):
        self.sounds['init'].play()
        self.easy_color = ScreenConfig.RED
        self.hard_color = ScreenConfig.WHITE
        self.mode = ScreenConfig.EASY
        is_pressed = False
        blinking_delay = 0
        while self.running:
            self.clock.tick(ScreenConfig.fps)

            # draw background
            self.screen.fill(ScreenConfig.BLACK)

            # draw gamename
            self.screen.blit(self.background_images['gamename'], ScreenConfig.gamename_pos)

            # text level: easy
            easy_font = pygame.font.SysFont(ScreenConfig.easy_font, ScreenConfig.easy_size)
            easy_text = easy_font.render("EASY", True, self.easy_color)
            easy_rect = easy_text.get_rect(center=ScreenConfig.easy_pos)
            self.screen.blit(easy_text, easy_rect)     

            # text level: hard
            hard_font = pygame.font.SysFont(ScreenConfig.hard_font, ScreenConfig.hard_size)
            hard_text = hard_font.render("HARD", True, self.hard_color)
            hard_rect = hard_text.get_rect(center=ScreenConfig.hard_pos)
            self.screen.blit(hard_text, hard_rect)

            # text info
            info_font = pygame.font.SysFont(ScreenConfig.info_font, ScreenConfig.info_size)
            if is_pressed:
                info_text = info_font.render("PRESS SPACE TO START", True, ScreenConfig.info_color)
            else:
                info_text = info_font.render("PRESS LEFT/RIGHT TO SELECT LEVEL", True, ScreenConfig.info_color)
            info_rect = info_text.get_rect(center=ScreenConfig.info_pos)
            if blinking_delay in range(2 * ScreenConfig.max_blinking_delay // 3):
                self.screen.blit(info_text, info_rect)
            blinking_delay += 1
            blinking_delay %= ScreenConfig.max_blinking_delay          
            
            for event in pygame.event.get():

                if event.type == pygame.QUIT: # quit
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q: # quit
                        self.running = False
                    
                    elif event.key == pygame.K_LEFT:
                        self.easy_color = ScreenConfig.RED
                        self.hard_color = ScreenConfig.WHITE
                        self.mode = ScreenConfig.EASY
                        is_pressed = True
                    
                    elif event.key == pygame.K_RIGHT:
                        self.easy_color = ScreenConfig.WHITE
                        self.hard_color = ScreenConfig.RED
                        self.mode = ScreenConfig.HARD
                        is_pressed = True
                    
                    elif event.key == pygame.K_SPACE:
                        self.load()
                        
            pygame.display.update()
    
    def load(self):
        self.sounds['init'].stop()
        self.sounds['loading'].play()
        loading = 0
        max_loading = ScreenConfig.loading_sound_time * ScreenConfig.fps
        player = Player(self.player_images, self.sounds)
        player.dx = 2
        player.pos = (player.pos[0] + 160, player.pos[1])
        while self.running:
            self.clock.tick(ScreenConfig.fps)

            if loading > max_loading:
                break
            player.walk()

            # draw background
            self.screen.fill(ScreenConfig.BLACK)

            # draw gamename
            self.screen.blit(self.background_images['gamename'], ScreenConfig.gamename_pos)

            # text level: easy
            easy_font = pygame.font.SysFont(ScreenConfig.easy_font, ScreenConfig.easy_size)
            easy_text = easy_font.render("EASY", True, self.easy_color)
            easy_rect = easy_text.get_rect(center=ScreenConfig.easy_pos)
            self.screen.blit(easy_text, easy_rect)     

            # text level: hard
            hard_font = pygame.font.SysFont(ScreenConfig.hard_font, ScreenConfig.hard_size)
            hard_text = hard_font.render("HARD", True, self.hard_color)
            hard_rect = hard_text.get_rect(center=ScreenConfig.hard_pos)
            self.screen.blit(hard_text, hard_rect)

            # draw player
            self.screen.blit(player.image, player.rect)
                        
            loading += 1

            for event in pygame.event.get():

                if event.type == pygame.QUIT: # quit
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q: # quit
                        self.running = False
                    
                    elif event.key == pygame.K_SPACE:
                        loading = max_loading

            pygame.display.update()

        Player.group.remove(player)
        self.sounds['loading'].stop()
        self.run()
        
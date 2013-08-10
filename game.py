#!/usr/bin/env python

try:
    import os
    import sys
    import math
    import random
    import pygame    
    from pygame.locals import *
    from level import *
    from player import *
    from resources import *
except ImportError, err:
    print "cannot load module(s)"
    sys.exit(2)

class Game:
    
    def __init__(self):
        #set physics variables
        self.clock = pygame.time.Clock()
        self.__physics_FPS = 100.0
        self.__dt = 1.0 / self.__physics_FPS
        self.time_current = self.get_time()
        self.accumulator = 0.0
        #set program stuff
        self.screen_size = (1280, 720)
        self.screen = pygame.display.set_mode(self.screen_size)
        self.tile_size = 64
        self.name = "RPG"
        self.font = pygame.font.SysFont("monospace", 15)
        self.movement_points = [0, 0, 0, 0] #up, right, down, left
        
    def load(self):
        self.screen.fill((0, 0, 0))
        pygame.display.set_caption(self.name)
        #initialise objects
        level = Level("level.map", "key.txt", self.tile_size)
        level.load_tiles("tiles.png")
        level.load_map()
        self.background, self.background_rect = level.create()
        player = Player()
        self.entities = pygame.sprite.Group(player)
        self.set_player_center(player)
        self.set_level_offset(level, player)
        self.play(level, player)

    def get_time(self):
        #returns time passed in seconds
        return float(pygame.time.get_ticks()) / 1000.0

    def draw_to_hud(self, text, x, y):
        label = self.font.render(text, 1, (255,255,0))
        self.screen.blit(label, (x, y))

    def set_player_center(self, player):
        #set player in screen center
        (screen_width, screen_height) = self.screen_size
        player.position[1] = (screen_height / 2) - (player.rect.height / 2)
        player.position[0] = (screen_width / 2) - (player.rect.width / 2)

    def set_level_offset(self, level, player):
        top_offset = player.location[1] - player.position[1]
        left_offset = player.location[0] - player.position[0]
        self.background_rect.top = - top_offset
        self.background_rect.left = - left_offset

    def is_player_blocked(self, level, player):
        x, y = player.get_coordinates()
        player.directions_blocked["up"] = level.is_wall(x, y - 1)
        player.directions_blocked["right"] = level.is_wall(x + 1, y)
        player.directions_blocked["down"] = level.is_wall(x, y + 1)
        player.directions_blocked["left"] = level.is_wall(x - 1, y)

    def move(self, player, direction):
        if not player.directions_blocked["up"] and direction == "up":
            player.state = "moving_up"
            self.movement_points[0] = 64
            player.state = "idle"
        if not player.directions_blocked["right"] and direction == "right":
            player.state = "moving_right"
            self.movement_points[1] = 64
            player.state = "idle"
        if not player.directions_blocked["down"] and direction == "down":
            player.state = "moving_down"
            self.movement_points[2] = 64
            player.state = "idle"
        if not player.directions_blocked["left"] and direction == "left":
            player.state = "moving_left"
            self.movement_points[3] = 64
            player.state = "idle"

    def handle_events(self, player):
        dt = self.__dt
        player.movement_cooldown += dt
        self.keys_down = pygame.key.get_pressed()
        if player.movement_cooldown >= player.movement_limit:
            if self.keys_down[K_w]:       
                self.move(player, "up")
            if self.keys_down[K_d]:
                self.move(player, "right")
            if self.keys_down[K_s]:
                self.move(player, "down")
            if self.keys_down[K_a]:
                self.move(player, "left")
            player.movement_cooldown = 0.0
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

    def update(self, level, player):
        #call update method for all entities
        self.entities.update()
        for entity in self.entities:
            #update player location relative to map
            entity.location[0] = entity.position[0] - self.background_rect.left
            entity.location[1] = entity.position[1] - self.background_rect.top
        self.is_player_blocked(level, player)
        self.handle_events(player)     

    def render(self):
        if self.movement_points[0] > 0:
            self.background_rect.top += 1
            self.movement_points[0] -= 1
        if self.movement_points[1] > 0:
            self.background_rect.left -= 1
            self.movement_points[1] -= 1
        if self.movement_points[2] > 0:
            self.background_rect.top -= 1
            self.movement_points[2] -= 1
        if self.movement_points[3] > 0:
            self.background_rect.left += 1
            self.movement_points[3] -= 1
        self.screen.blit(self.background, self.background_rect)
        dirty_rects = self.entities.draw(self.screen)
        pygame.display.update()

    def play(self, level, player):
        dt = self.__dt
        while True:
            time_new = self.get_time()
            time_frame = time_new - self.time_current
            if time_frame > 0.25:
                time_frame = 0.25
            self.accumulator += time_frame
            self.time_current = time_new        
            # update
            while self.accumulator >= dt:
                self.update(level, player)
                self.accumulator -= dt           
            # render
            self.render()      
    
def main():
    pygame.init()
    game = Game()
    game.load()

if __name__ == "__main__":
    main()

import random
from controllers import *

import pygame

from random import randrange

class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GRAY = (220, 220, 220)


class Constants:
    # G constant x planet's mass
    GM = 6.674e-11 * 5.972e24

    # planet's radius
    R_PLANET = 6.371e6

    # screen size
    screen_size = (1024, 576)

    # how many meters are visible on the screen
    height_visible = 1e6

    # meters per pixel
    meters_per_pixel = height_visible / screen_size[1]

    # dt[s] for frame
    dt = 0.25

    # where mouse will be put after starting
    pos_mouse_start = (850, screen_size[1]*0.8)

    # where mouse needs to be in order to start
    rect_to_start = pygame.Rect(800, screen_size[1]*0.8 - 25, 100, 50)

    # font size
    font_size = 25

    # percent
    percent_bot = 0.2
    percent_top = 0.8


class Rocket:
    size = (0.025 * Constants.screen_size[0], 0.15 * Constants.screen_size[1])
    max_power = 12.5

    rect: pygame.Rect
    vel: float
    height: float

    def __init__(self,  height: float, vel: float):
        self.height = height
        self.vel = vel
        self.update_rect()

    def draw(self, screen: pygame.display):
        pygame.draw.rect(screen, Colors.RED, self)

    def update(self, normalized_power):
        r = Constants.R_PLANET + self.height
        acc_grav = -Constants.GM/(r**2)
        acc_power = normalized_power * Rocket.max_power
        self.vel = self.vel + (acc_grav + acc_power) * Constants.dt
        self.height = self.height + self.vel * Constants.dt
        self.update_rect()

    def update_rect(self):
        x_center = Constants.screen_size[0]/2
        y_center = Constants.screen_size[1] - (self.height / Constants.meters_per_pixel)
        self.rect = pygame.Rect((x_center-Rocket.size[0]/2, y_center-Rocket.size[1]), Rocket.size)




class Simulation:
    font: pygame.font
    fps: int
    screen: pygame.display
    clock: pygame.time.Clock
    rocket: Rocket
    controller: Controller

    @staticmethod
    def init():
        pygame.init()
        pygame.font.init()
        Simulation.font = pygame.font.SysFont('Comic Sans MS', Constants.font_size)
        Simulation.fps = 120
        Simulation.screen = pygame.display.set_mode(Constants.screen_size)
        Simulation.clock = pygame.time.Clock()
        height, vel = Simulation.get_starting_conditions()
        Simulation.rocket = Rocket(height, vel)
        Simulation.screen.fill(Colors.WHITE)
        Simulation.rocket.draw(Simulation.screen)
        pygame.draw.rect(Simulation.screen, Colors.RED, Constants.rect_to_start)
        pygame.display.update()

        # choose controller
        #Simulation.controller = ManualController()
        Simulation.controller = AnfisController("D:\\Studia4Sem\\SI\\Projekt\\Simulation\\fis.fis")


    @staticmethod
    def run():
        frames = []
        time = 0

        # start simulation
        while Simulation.rocket.height > 0:

            power = Simulation.controller.getPower(Simulation.rocket.height, Simulation.rocket.vel)
            frames.append([Simulation.rocket.height, Simulation.rocket.vel, power])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

            Simulation.screen.fill(Colors.WHITE)
            Simulation.clock.tick(Simulation.fps)
            time += Constants.dt
            Simulation.rocket.update(power)

            Simulation.adjust_fps()

            velocity = Simulation.font.render('velocity: ' + str(round(Simulation.rocket.vel)), False, (0, 0, 0))
            height = Simulation.font.render('height: ' + str(round(Simulation.rocket.height)), False, (0, 0, 0))
            pow = Simulation.font.render('power: ' + str(round(power, 2)), False, (0, 0, 0))
            fps = Simulation.font.render('fps: ' + str(Simulation.fps), False, (0, 0, 0))
            Simulation.screen.blit(velocity, (0, Constants.font_size *0))
            Simulation.screen.blit(height, (0, Constants.font_size*1))
            Simulation.screen.blit(pow, (0, Constants.font_size*2))
            Simulation.screen.blit(fps, (0, Constants.font_size*3))
            Simulation.draw_power(power)
            Simulation.rocket.draw(Simulation.screen)

            pygame.display.update()

        return Simulation.check_result(), frames

    @staticmethod
    def check_result():
        return abs(Simulation.rocket.vel) < 4

    @staticmethod
    def draw_power(normalized_power):
        bottom = Constants.screen_size[1] * (1-Constants.percent_bot)
        max_top = Constants.screen_size[1] * (1-Constants.percent_top)
        top = bottom - (bottom-max_top) * normalized_power
        pygame.draw.rect(Simulation.screen, Colors.GRAY, pygame.Rect(800, top, 100, bottom-top))

    @staticmethod
    def adjust_fps():
        if Simulation.rocket.height < 1.5e3:
            Simulation.fps = 8
        elif Simulation.rocket.height < 3e4:
            Simulation.fps = 30
        else:
            Simulation.fps = 120

    @staticmethod
    def rate():
        Simulation.screen.fill(Colors.WHITE)
        info = Simulation.font.render('g-good, b-bad', False, (0, 0, 0))
        Simulation.screen.blit(info, (Constants.screen_size[0]/2, Constants.screen_size[1]/2))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key ==pygame.K_g:
                        return True
                    elif event.key == pygame.K_b:
                        return False

    @staticmethod
    def get_starting_conditions():
        return random.uniform(0.3e6, 0.7e6), random.uniform(-200.0, 100.0)

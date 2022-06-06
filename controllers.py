import pygame
import simulation
import fuzzyReader
import simpful as sf

class Controller:
    status: bool

    def getPower(self, height, velocity):
        raise NotImplementedError()


class ManualController(Controller):

    @staticmethod
    def scale_to_power(percent_of_screen):
        t = simulation.Constants.percent_top
        b = simulation.Constants.percent_bot
        power = percent_of_screen / (t - b) - b / (t - b)
        if power > 1:
            return 1
        if power < 0:
            return 0
        return power

    def __init__(self):
        cursor_set = False
        quit = False
        while not cursor_set and not quit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit = True
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    r = simulation.Constants.rect_to_start
                    if r.x < x < (r.x + r.width) and r.y < y < (r.y + r.height):
                        cursor_set = True
        pygame.mouse.set_visible(True)
        pygame.mouse.set_pos(simulation.Constants.pos_mouse_start)
        if not quit:
            self.status = True
        else:
            self.status = False

    def getPower(self, height, velocity):
        # input
        x, y = pygame.mouse.get_pos()
        percent_of_screen = (simulation.Constants.screen_size[1] - y) / simulation.Constants.screen_size[1]
        normalized_power = self.scale_to_power(percent_of_screen)
        return normalized_power

class AnfisController(Controller):

    fuzzy_system: sf.FuzzySystem

    def __init__(self, path):
        self.status = True
        fr = fuzzyReader.FuzzyReader(path)
        self.fuzzy_system = fr.read()

    def getPower(self, height, velocity):
        self.fuzzy_system.set_variable("input1", height)
        self.fuzzy_system.set_variable("input2", velocity)
        result = self.fuzzy_system.Sugeno_inference(["Power"])['Power']
        if result>1:
            result=1
        elif result<0:
            result=0
        return result
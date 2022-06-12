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

    def __init__(self, path, function_type):
        self.status = True
        fr = fuzzyReader.FuzzyReader(path, function_type)
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


class FisController(Controller):
    fuzzy_system: sf.FuzzySystem

    def __init__(self):
        self.status = True
        self.fuzzy_system = self.construct_fis()


    def construct_fis(self):
        FS = sf.FuzzySystem(show_banner=False)


        h1 = sf.FuzzySet(function=sf.Triangular_MF(a=80, b=200, c=4000), term="very_small")
        h2 = sf.FuzzySet(function=sf.Triangular_MF(a=3500, b=30000, c=75000), term="small")
        h3 = sf.FuzzySet(function=sf.Triangular_MF(a=40000, b=110000, c=200000), term="medium")
        h4 = sf.FuzzySet(function=sf.Triangular_MF(a=100000, b=550000, c=800000), term="big")
        h5 = sf.FuzzySet(function=sf.Triangular_MF(a=350000, b=900000, c=1000000), term="very_big")
        h6 = sf.FuzzySet(function=sf.Triangular_MF(a=0, b=1, c=100), term="ground")
        FS.add_linguistic_variable("Height", sf.LinguisticVariable([h1, h2, h3,h4,h5,h6], concept="Height",
                                                                 universe_of_discourse=[0, 1000000]))

        p1 = sf.FuzzySet(function=sf.Triangular_MF(a=0.96, b=0.99, c=1), term="very_big")
        p2 = sf.FuzzySet(function=sf.Triangular_MF(a=0.75, b=0.95, c=1), term="big")
        p3 = sf.FuzzySet(function=sf.Triangular_MF(a=0.4, b=0.6, c=0.8), term="medium")
        p4 = sf.FuzzySet(function=sf.Triangular_MF(a=0, b=0.01, c=0.5), term='small')
        FS.add_linguistic_variable("Power", sf.LinguisticVariable([p1, p2, p3,p4], universe_of_discourse=[0, 1]))

        v1 = sf.FuzzySet(function=sf.Triangular_MF(a=-2000, b=-1999, c=-600), term="neg_very_big")
        v2 = sf.FuzzySet(function=sf.Triangular_MF(a=-1100, b=-800, c=-500), term="neg_big")
        v3 = sf.FuzzySet(function=sf.Triangular_MF(a=-600, b=-200, c=-100), term="neg_medium")
        v4 = sf.FuzzySet(function=sf.Triangular_MF(a=-100, b=0, c=5), term="neg_small")
        v5 = sf.FuzzySet(function=sf.Triangular_MF(a=-50, b=0, c=5), term="very_neg_small")
        v8 = sf.FuzzySet(function=sf.Triangular_MF(a=-10, b=0, c=10), term="zero1")
        v6 = sf.FuzzySet(function=sf.Triangular_MF(a=-2, b=0, c=2), term="zero2")
        v7 = sf.FuzzySet(function=sf.Triangular_MF(a=-5, b=199, c=200), term="pos")
        FS.add_linguistic_variable("Velocity", sf.LinguisticVariable([v1, v2, v3, v4,v5,v6,v7,v8], concept="Velocity",
                                                                  universe_of_discourse=[-2000, 200]))

        r1 = "IF (Height IS big) AND (Velocity IS neg_medium) THEN (Power IS medium)"
        r2 = "IF (Height IS big) AND (Velocity IS neg_big) THEN (Power IS very_big)"
        r3 = "IF (Height IS big) AND  (Velocity IS neg_small) THEN (Power IS small)"
        r4 = "IF (Height IS very_big) THEN (Power IS small)"

        r5 = "IF (Height IS medium) AND  (Velocity IS neg_big ) THEN (Power IS very_big)"
        r6 = "IF (Height IS medium) AND  (Velocity IS neg_medium) THEN (Power IS big)"
        r7 = "IF (Height IS medium) AND  (Velocity IS neg_small) THEN (Power IS medium)"

        r8 = "IF (Height IS small)  AND ((Velocity IS neg_medium ) OR (Velocity IS neg_big )) THEN (Power IS very_big)"
        r9 = "IF (Height IS small)   THEN (Power IS big)"

        r10 = "IF (Height IS very_small) OR (Height IS ground) THEN (Power IS very_big)"
        r11 = "IF (Height IS very_small)  AND (Velocity IS zero1) THEN (Power IS small)"

        r12 = "IF (Velocity IS pos) THEN (Power IS small)"
        r13= "IF (Velocity IS neg_very_big) THEN (Power IS very_big)"
        r14="IF (Velocity IS neg_big) THEN (Power IS very_big)"

        r15 = "IF (Height IS ground)  AND (Velocity IS zero2) THEN (Power IS small)"
        FS.add_rules([r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r12,r11,r13,r14, r15])

        return FS

    def getPower(self, height, velocity):
        self.fuzzy_system.set_variable("Height", height)
        self.fuzzy_system.set_variable("Velocity", velocity)
        res = self.fuzzy_system.Mamdani_inference(["Power"])['Power']
        return res
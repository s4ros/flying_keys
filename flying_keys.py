import sys
import keyboard
import pygame
import queue
import threading
import random


class Hooker(object):
    def __init__(self, q):
        self.queue = q

    def add_key_to_queue(self, e):
        if e.event_type == "down":
            self.queue.put(e.name)


class ThreadKeyHooker(threading.Thread):
    def __init__(self, q):
        threading.Thread.__init__(self)
        self.hooker = Hooker(q)

    def run(self):
        keyboard.hook(self.hooker.add_key_to_queue)
        keyboard.wait()


class Particle(object):
    def __init__(self, startx, starty, col, width):
        self.x = startx
        self.y = starty
        self.wide = width
        self.color = col

    def move(self, x, y):
        self.x = x + random.randint(0, self.wide)
        self.y = y + random.randint(-5, 15)
        self.color -= 2


class Keystroke(object):
    def __init__(self, surface, font):
        max_x, max_y = surface.get_size()
        self.x = 10
        self.dx = random.randint(3, 25)
        self.y = 10
        self.dy = 0
        self.gravity = 0.3
        self.width = font.get_width() + 4
        self.height = font.get_height()
        self.color = 255
        self.font = font
        self.n_particles = 50
        self.particles = [Particle(self.x, self.y, 255, self.width)
                          for x in range(self.n_particles)]

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            (self.color, 0, 0),
            (self.x, self.y, self.width, self.height),
            0)
        for p in self.particles:
            pygame.draw.circle(
                surface,
                (p.color, p.color, 0),
                (int(p.x), int(p.y)), 2
            )
            p.move(self.x,
                   self.y - self.dy)
        surface.blit(self.font, (self.x + 2, self.y))

    def newton(self):
        self.dy += self.gravity
        self.x += self.dx
        self.y += self.dy
        self.color -= 2


class KeyVisualizer(object):
    def __init__(self, q, width=640, height=480):
        self.queue = q
        self.width = width
        self.height = height
        self.tkh = ThreadKeyHooker(self.queue)
        self.tkh.setDaemon(True)
        self.tkh.start()
        pygame.init()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 42)
        self.screen = pygame.display.set_mode((width, height))
        random.seed()
        self.buttons = []
        # pygame.display.update()

    def check_dead_buttons(self, buttons):
        max_x, max_y = self.width, self.height
        for b in buttons:
            if b.x >= max_x or b.y >= max_y:
                index = self.buttons.index(b)
                self.buttons.pop(index)
            else:
                b.newton()

    def get_key_from_queue(self):
            return self.queue.get(False)

    def create_button(self, key):
        text = self.font.render(key, True, (255, 255, 255))
        g = Keystroke(self.screen, text)
        self.buttons.append(g)

    def draw_all_buttons(self):
        for b in self.buttons:
            b.draw(self.screen)

    def run(self):
        while True:
            self.screen.fill((0, 255, 0))
            try:
                key = self.get_key_from_queue()
                print(key)
                print(self.buttons)
                self.create_button(key)
            except:
                pass
            self.draw_all_buttons()
            pygame.display.flip()
            self.check_dead_buttons(self.buttons)
            self.clock.tick(30)



if __name__ == "__main__":
    q = queue.Queue()
    kv = KeyVisualizer(q, 1720, 1080)
    kv.run()

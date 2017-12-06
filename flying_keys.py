import sys
import keyboard
import pygame
import queue
import threading
import random
import os


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
    def __init__(self, startx, starty, width):
        self.x = startx
        self.y = starty
        self.wide = width

    def move(self, x, y):
        self.x = x
        self.y = y


class Keystroke(object):
    def __init__(self, surface, font, images):
        self.images = images
        max_x, max_y = surface.get_size()
        self.x = 10
        self.dx = random.randint(3, 25)
        self.y = 10
        self.dy = 0
        self.gravity = 0.3
        self.width = font.get_width() + 4
        self.height = font.get_height()
        # self.color = 255
        self.color = (128, 128, 128)
        self.font = font
        self.n_particles = 1
        self.particles = [Particle(self.x - (self.width),
                                   self.y - (self.height),
                                   self.width)
                          for x in range(self.n_particles)]

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            self.color,
            (self.x-20, self.y-5, self.width+40, self.height+10),
            5)
        pygame.draw.rect(
            surface,
            (255, 255, 255),
            (self.x-18, self.y-2, self.width+36, self.height+4),
            0)
        # for p in self.particles:
        #     p.move(self.x - self.width ,
        #            self.y - self.dy - self.height // 2)
        #     surface.blit(random.choice(images), (p.x, p.y))
        surface.blit(self.font, (self.x + 2, self.y))

    def newton(self):
        self.dy += self.gravity
        self.x += self.dx
        self.y += self.dy
        # self.color -= 2


class KeyVisualizer(object):
    def __init__(self, q, images, width=640, height=480):
        self.queue = q
        self.images = images
        self.width = width
        self.height = height
        # keyboard thread
        self.tkh = ThreadKeyHooker(self.queue)
        self.tkh.setDaemon(True)
        self.tkh.start()
        # //
        pygame.init()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
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
        text = self.font.render(key, True, (0, 0, 0))
        g = Keystroke(self.screen, text, self.images)
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
                # print(self.buttons)
                self.create_button(key)
            except:
                pass
            self.draw_all_buttons()
            pygame.display.flip()
            self.check_dead_buttons(self.buttons)
            self.clock.tick(30)


if __name__ == "__main__":
    q = queue.Queue()
    images = []
    for file in os.listdir("PNG/black_smoke"):
        if file.endswith(".png"):
            filepath = os.path.join("PNG/black_smoke", file)
            images.append(pygame.image.load(filepath))
    kv = KeyVisualizer(q, images, 1920, 1080)
    kv.run()

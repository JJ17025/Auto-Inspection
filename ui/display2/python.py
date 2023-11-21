import statistics
from datetime import datetime

import cv2
import numpy as np
import pygame
import sys


class Button:
    def __init__(self, name, image_path, position, size, text_on_button=None):
        self.image = pygame.image.load(image_path)
        self.text_on_button = text_on_button
        self.default_image = pygame.Surface(size, pygame.SRCALPHA)
        self.hover_image = pygame.Surface(size, pygame.SRCALPHA)
        self.default_image.blit(self.image, (0, 0), pygame.Rect(0, 0, size[0], size[1]))
        self.hover_image.blit(self.image, (0, 0), pygame.Rect(0, size[1], size[0], size[1]))
        self.name = name
        self.image = self.default_image
        self.rect = self.default_image.get_rect()
        self.rect.topleft = position
        if text_on_button:
            font = pygame.font.Font('NotoSansThai.ttf', 20)
            text_render = font.render(f'{self.text_on_button}', True, (255, 255, 255))
            self.default_image.blit(text_render, (5, 0))
            self.hover_image.blit(text_render, (6, 0))

    def is_mouse_over(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def draw(self, display):
        display.blit(self.image, self.rect)


class Buttons:
    def __init__(self):
        self.buttons = {}

    def add(self, button):
        self.buttons[button.name] = button

    def is_mouse_over(self, mouse_pos):
        res = None
        for name, button in self.buttons.items():
            if button.is_mouse_over(mouse_pos):
                button.image = button.hover_image
                res = name
            else:
                button.image = button.default_image
        return res

    def draw(self, display):
        for name, button in self.buttons.items():
            button.draw(display)


class Windows:
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size
        self.show = False
        self.data = ['1', '2']
        self.rect = None

        self.surface = pygame.Surface(size, pygame.SRCALPHA)

    def draw_rect(self, display):
        if self.show:
            self.rect = (*self.pos, *self.size)
            # buttons = Buttons()
            # buttons.add(Button('x1', "main button/button box.png", self.pos, (47, 40), 'a'))
            # buttons.add(Button('x2', "main button/button box.png", self.pos, (47, 40), 'b'))

            # is_mouse_over_button = buttons.is_mouse_over(mouse_pos)
            # buttons.draw(display)
            a = Button('x1', "main button/close.png", (0,0), (47, 40), 'a')
            b = Button('x1', "main button/close.png", (0,10), (47, 40), 'b')

            self.surface.blit(a.image, (0, 0))

            win = pygame.draw.rect(display, (43, 45, 48), self.rect)


# def cvimage_to_pygame(image):
#     """Convert cvimage into a pygame image"""
#     if type(None) == type(image):
#         image = np.full((1008, 1344, 3), (30, 50, 25), np.uint8)
#     else:
#         image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     return pygame.image.frombuffer(image.tobytes(), image.shape[1::-1], "RGB")
#
#
# display = cv2.imread('display.png')
#
#
pygame.init()
display = pygame.display.set_mode((1920, 1080))
# display = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Auto Inspection')
clock = pygame.time.Clock()

buttons = Buttons()
buttons.add(Button('minimize button', "main button/minimize.png", (1920 - 47 * 3, 0), (47, 40)))
buttons.add(Button('maximize button', "main button/maximize.png", (1920 - 47 * 2, 0), (47, 40)))
buttons.add(Button('close button', "main button/close.png", (1920 - 47, 0), (47, 40)))
buttons.add(Button('setting button', "main button/setting.png", (1920 - 47 * 4, 5), (30, 30)))
buttons.add(Button('select button', "main button/select model.png", (50, 5), (30, 30)))

buttons.add(Button('mode', "main button/button box.png", (5, 70), (30, 30), 'M'))
win = Windows((0, 0), (200, 200))
time_list = []
text_out_list = []
while True:
    t1 = datetime.now()
    mouse_pos = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()
    events = pygame.event.get()
    for event in events:
        is_mouse_over_button = buttons.is_mouse_over(mouse_pos)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if is_mouse_over_button:
                print(f"{is_mouse_over_button} Clicked!")
                if is_mouse_over_button == 'close button':
                    pygame.quit()
                    sys.exit()
                if is_mouse_over_button == 'minimize button':
                    pygame.display.iconify()
            if event.button == 3:
                win.show = True
                win.pos = mouse_pos
            if event.button == 1:
                win.show = False

    display.fill((31, 30, 34), (0, 0, 1920, 1080))
    # display.fill((55, 71, 103), (0, 0, 1920, 40))
    # display.fill((43, 45, 48), (0, 41, 40, 1008))  # l bar
    # display.fill((43, 45, 48), (1386, 41, 534, 80))  # top2 bar
    # display.fill((43, 45, 48), (1386, 122, 32, 927))  # r bar
    # display.fill((43, 45, 48), (0, 1050, 1920, 30))  # bottom bar
    # pygame.draw.rect(display, (31, 30, 34), (0, 0, 1920, 1080))  # bg
    top_bar = pygame.draw.rect(display, (55, 71, 103), (0, 0, 1920, 40))  # top bar
    left_bar = pygame.draw.rect(display, (43, 45, 48), (0, 41, 40, 1008))  # left bar
    top2_bar = pygame.draw.rect(display, (43, 45, 48), (1386, 41, 534, 80))  # top2 bar
    right_bar = pygame.draw.rect(display, (43, 45, 48), (1386, 122, 32, 927))  # right bar
    bottom_bar = pygame.draw.rect(display, (43, 45, 48), (0, 1050, 1920, 30))  # bottom bar
    buttons.draw(display)

    win.draw_rect(display)

    if top_bar.collidepoint(mouse_pos):
        print('top')

    t2 = datetime.now()
    t_sec = (t2 - t1).total_seconds()
    time_list.append(t_sec)
    if len(time_list) > 20:
        time_list = time_list[1:]
    text_bottom_list = [
        ((10, 1055), f'fps: {round(1 / statistics.mean(time_list))}'),
        ((100, 1055), f'pos: {mouse_pos}'),
    ]
    font = pygame.font.Font('NotoSansThai.ttf', 14)
    for pos, text_bottom in text_bottom_list:
        text_render = font.render(text_bottom, True, (255, 255, 255))
        display.blit(text_render, pos)

    pygame.display.flip()
    clock.tick(30)

import os
import statistics
import time
from datetime import datetime

import cv2
import numpy as np
import pygame
import sys


class Button:
    def __init__(self, name, xywh, image_path=None, text=None, text_size=18, text_center='center'):
        self.name = name
        self.rect = pygame.Rect(*xywh)
        self.image_path = image_path
        self.text = text
        self.text_size = text_size
        self.text_center = text_center
        self.text_color = (255, 255, 255)
        self.update()

    def is_mouse_over(self, rect, mouse_pos):
        res = self.rect.move(rect.x, rect.y).collidepoint(mouse_pos)
        self.image = self.hover_image if res else self.default_image
        return res

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'text_color':
                self.text_color = v

        self.default_image = pygame.Surface(self.rect[2:], pygame.SRCALPHA)  # if mouse not on
        self.hover_image = pygame.Surface(self.rect[2:], pygame.SRCALPHA)  # if mouse on
        if self.image_path:
            self.image = pygame.image.load(self.image_path)
            self.default_image.blit(self.image, (0, 0), pygame.Rect(0, 0, *self.rect[2:]))
            self.hover_image.blit(self.image, (0, 0), pygame.Rect(0, self.rect[3], *self.rect[2:]))
            self.image = self.default_image

        if self.text:
            font = pygame.font.Font('ui/display2/NotoSansThai.ttf', self.text_size)
            text_render = font.render(f'{self.text}', True, self.text_color)

            W, H = self.rect.size
            w, h = text_render.get_rect().size
            x, y = self.rect.center
            if self.text_center == 'center':
                x = W // 2 - w // 2
                y = H // 2 - h // 2
            if self.text_center == 'l':
                x = 0
                y = H // 2 - h // 2
            # print(x, y, w, h)
            # print()
            self.default_image.blit(text_render, (x - 1, y))
            self.hover_image.blit(text_render, (x, y + 1))
            pygame.draw.rect(self.hover_image, (67, 69, 74), self.rect.move(-self.rect.x, -self.rect.y), 1)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Text:
    def __init__(self, text, pos, font):
        self.text = text
        self.pos = pos
        self.font = font


class Texts:
    def __init__(self, font):
        self.texts = {}
        self.font = font

    def add(self, name, pos, text):
        self.texts[name] = Text(text, pos, self.font)

    def putTextall(self, display):
        # self.surface = pygame.draw.rect(display, (40, 40, 40), (41, 41, 1385 - 41, 1008))  # center bar
        # self.surface = pygame.Surface((1344, 1008))  # center bar
        for name, text in self.texts.items():
            text_render = text.font.render(text.text, True, (255, 255, 255))
            # pygame.draw.rect(text_render, (67, 69, 74), text_render.get_rect(), 1)
            display.blit(text_render, text.pos)


class Flex:
    def __init__(self, name, xywh, color):
        self.name = name
        self.where_is_mose = None
        self.rect = pygame.Rect(*xywh)
        self.surface = pygame.Surface((self.rect.w, self.rect.h))
        self.show_flex = True
        self.color = pygame.Color(color)
        self.buttons = {}
        self.texts = Texts(pygame.font.Font('ui/display2/NotoSansThai.ttf', 14))
        self.dict_data = {}

    def add_button(self, button):
        self.buttons[button.name] = button

    def mouse_on_surface(self, pos):
        return self.rect.collidepoint(pos)

    def have_mouse_on_is(self, mouse_pos):
        res = None
        if self.show_flex:
            for name, button in self.buttons.items():
                if button.is_mouse_over(self.rect, mouse_pos):
                    res = name
        return res

    def draw(self, display):
        if self.show_flex:
            self.surface.fill(self.color)
            pygame.draw.rect(self.surface, (67, 69, 74), self.rect.move(-self.rect.x, -self.rect.y), 1)

            # button
            for name, button in self.buttons.items():
                button.draw(self.surface)
            # for name, button in self.buttons.items():
            #     self.surface.blit(button.image,button.rect)
            display.blit(self.surface, (self.rect.x, self.rect.y))

            # text
            self.texts.putTextall(display)


def main(img):
    pygame.init()
    display = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption('Auto Inspection')
    clock = pygame.time.Clock()

    top_flex = Flex('top_surface', (0, 0, 1920, 40), (55, 71, 103))
    top_flex.add_button(Button('minimize button', (1920 - 47 * 3, 0, 47, 40), "ui/display2/main button/minimize.png", ))
    top_flex.add_button(Button('maximize button', (1920 - 47 * 2, 0, 47, 40), "ui/display2/main button/maximize.png", ))
    top_flex.add_button(Button('close button', (1920 - 47 * 1, 0, 47, 40), "ui/display2/main button/close.png", ))
    top_flex.add_button(Button('setting button', (1920 - 47 * 4, 5, 30, 30), "ui/display2/main button/setting.png", ))
    top_flex.add_button(Button('select model button', (50, 5, 30, 30), "ui/display2/main button/select model.png"))
    top_flex.add_button(Button('model PCB name', (100, 5, 200, 30),
                               text='model PCB name', text_size=18, text_center='l'))

    bottom_flex = Flex('but_surface', (0, 1050, 1920, 30), (43, 45, 48))

    tool_flex = Flex('but_surface', (0, 41, 40, 1008), (43, 45, 48))
    tool_flex.dict_data['mode'] = 'debug'
    tool_flex.add_button(Button('debug mode', (5, 5, 30, 30), "ui/display2/main button/button box.png",
                                text='D', text_size=15, text_center='center'))
    tool_flex.add_button(Button('manual mode', (5, 40, 30, 30), "ui/display2/main button/button box.png",
                                text='M', text_size=15, text_center='center'))
    tool_flex.add_button(Button('auto mode', (5, 75, 30, 30), "ui/display2/main button/button box.png",
                                text='A', text_size=15, text_center='center'))

    sup_tool_flex = Flex('but_surface', (1386, 41, 534, 80), (43, 45, 48))
    sup_tool_flex.add_button(Button('cap button', (0 + 80 * 0, 0, 80, 80), "ui/display2/main button/cap.png", ))
    sup_tool_flex.add_button(Button('adj button', (0 + 80 * 1, 0, 80, 80), "ui/display2/main button/adj.png", ))
    sup_tool_flex.add_button(Button('predict button', (0 + 80 * 2, 0, 80, 80), "ui/display2/main button/predict.png", ))

    select_model_win = Flex('select model win', (40, 40, 220, 500), (43, 45, 48))
    select_model_win.show_flex = False

    setting_win = Flex('setting win', (1000, 150, 220, 500), (43, 45, 48))
    setting_win.show_flex = False

    time_list = []
    while True:
        t1 = datetime.now()
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        where_is_mose = (
                top_flex.have_mouse_on_is(mouse_pos) or
                bottom_flex.have_mouse_on_is(mouse_pos) or
                tool_flex.have_mouse_on_is(mouse_pos) or
                sup_tool_flex.have_mouse_on_is(mouse_pos) or
                select_model_win.have_mouse_on_is(mouse_pos) or
                setting_win.have_mouse_on_is(mouse_pos)
        )

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # if event.button == 3:
                select_model_win.show_flex = False
                setting_win.show_flex = False

                if where_is_mose:
                    print(f"Click --> {where_is_mose} <--")
                    if where_is_mose == 'close button':
                        pygame.quit()
                        sys.exit()
                    if where_is_mose == 'minimize button':
                        pygame.display.iconify()
                    if where_is_mose == 'maximize button':
                        top_flex.show_flex = False

                    if where_is_mose == 'select model button':
                        select_model_win.show_flex = True
                        data = os.listdir('data')
                        i = 0
                        for d in data:
                            i += 1
                            select_model_win.add_button(Button(f'{d}', (10, 10 + i * 35, 195, 30),
                                                               "ui/display2/main button/button box.png",
                                                               text=f'          {d}', text_size=14, text_center='l'))
                        # select_model_win.add_button(Button('model 2', (10, 40, 195, 30),
                        #                                    "ui/display2/main button/button box.png",
                        #                                    text='          model 2', text_size=14, text_center='l'))
                        # select_model_win.add_button(Button('model 3', (10, 70, 195, 30),
                        #                                    "ui/display2/main button/button box.png",
                        #                                    text='          model 3', text_size=14, text_center='l'))
                    if where_is_mose == 'setting button':
                        setting_win.show_flex = True
                        setting_win.add_button(Button('model 1', (10, 10, 195, 30),
                                                      "ui/display2/main button/button box.png",
                                                      text='          model 1', text_size=14, text_center='l'))
                        setting_win.add_button(Button('model 2', (10, 40, 195, 30),
                                                      "ui/display2/main button/button box.png",
                                                      text='          model 2', text_size=14, text_center='l'))
                        setting_win.add_button(Button('model 3', (10, 70, 195, 30),
                                                      "ui/display2/main button/button box.png",
                                                      text='          model 3', text_size=14, text_center='l'))
                    w = (255, 255, 255)
                    if where_is_mose == 'debug mode':
                        tool_flex.buttons['debug mode'].update(text_color=(20, 255, 0))
                        tool_flex.buttons['manual mode'].update(text_color=w)
                        tool_flex.buttons['auto mode'].update(text_color=w)
                    if where_is_mose == 'manual mode':
                        tool_flex.buttons['debug mode'].update(text_color=w)
                        tool_flex.buttons['manual mode'].update(text_color=(20, 255, 0))
                        tool_flex.buttons['auto mode'].update(text_color=w)
                    if where_is_mose == 'auto mode':
                        tool_flex.buttons['debug mode'].update(text_color=w)
                        tool_flex.buttons['manual mode'].update(text_color=w)
                        tool_flex.buttons['auto mode'].update(text_color=(20, 255, 0))

        t2 = datetime.now()
        t_sec = (t2 - t1).total_seconds()
        time_list.append(t_sec)
        if len(time_list) > 20:
            time_list = time_list[1:]

        bottom_flex.texts.add('fps', (10, 1055), f'fps: {round(1 / max(0.0001, statistics.mean(time_list)))}')
        bottom_flex.texts.add('pos', (100, 1055), f'pos: {mouse_pos}')
        bottom_flex.texts.add('name', (1800, 1055), f'Auto Inspection')

        display.fill((21, 20, 24), (0, 0, 1920, 1080))

        top_flex.draw(display)
        bottom_flex.draw(display)
        tool_flex.draw(display)
        sup_tool_flex.draw(display)
        select_model_win.draw(display)
        setting_win.draw(display)

        pygame.display.flip()
        clock.tick(30)


main(0)

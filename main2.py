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


pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pygame Surface Example")

# Set up colors
blue = (0, 0, 255)
red = (255, 0, 0)
green = (0, 255, 0)

blue_surface = pygame.Surface((800, 600))
blue_surface.fill(blue)

red_surface = pygame.Surface((200, 200))
red_surface.fill(red)

green_surface = pygame.Surface((20, 20))
green_surface.fill(green)

x = Button('close button', (50, 50, 47, 40), "ui/display2/main button/close.png", )

while True:
    mouse_pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    x.is_mouse_over(mouse_pos)

    pygame.draw.circle(red_surface, (0, 255, 0), [200, 200], 170, 3)
    x.draw(red_surface)
    red_surface.blit(green_surface, (10, 10))
    blue_surface.blit(red_surface, (200, 100))
    screen.blit(blue_surface, (0, 0))

    # Update the display
    pygame.display.flip()
    pygame.time.Clock().tick(60)

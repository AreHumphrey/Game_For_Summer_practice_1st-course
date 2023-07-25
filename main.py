import pygame
import pickle
from os import path

pygame.init()

clock = pygame.time.Clock()
fps = 60
screen_w = 700
screen_h = 700

tile_size = 35
game_over = 0
main_menu = True
level = 9
score = 0

screen = pygame.display.set_mode((screen_w, screen_h))
pygame.display.set_caption('Game_FEFU')
icon = pygame.image.load("background/fefu_logo.png")
pygame.display.set_icon(icon)

font_score = pygame.font.SysFont('Bauhaus 93', 20)
font = pygame.font.SysFont('Bauhaus 93', 60)
white = (255, 255, 255)
blue = (0, 0, 255)

# изображения для фона
bg_img = pygame.image.load('background/fefu_bg.png')
bg_img = pygame.transform.scale(bg_img, (screen_w, screen_h))

start_ing = pygame.image.load('background/start.png')
img_size = start_ing.get_size()
new_size = (img_size[0] * 4, img_size[1] * 4)
start_ing = pygame.transform.scale(start_ing, new_size)

exit_ing = pygame.image.load('background/end.png')
exit_ing = pygame.transform.scale(exit_ing, new_size)

restart_img = pygame.image.load('background/restart.png')
new_restart = (img_size[0] * 3, img_size[1] * 3)
restart_img = pygame.transform.scale(restart_img, new_restart)

img_logo = pygame.image.load('background/fefu_logo.png')
size_logo = img_logo.get_size()
new_size_logo = (size_logo[0] * 5, img_size[1] * 5)
img_logo = pygame.transform.scale(img_logo, new_size_logo)

pygame.mixer.music.load('music/ost.mp3')
pygame.mixer.music.play(-1)


def draw_text(text, fonts, text_color, x, y):
    img = fonts.render(text, True, text_color)
    screen.blit(img, (x, y))


def reset_level(levels):
    global worlds_data
    player.reset(100, screen_h - 106)
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()

    if path.exists(f'levels/level{levels}_data'):
        pickles_in = open(f'levels/level{levels}_data', 'rb')
        worlds_data = pickle.load(pickles_in)

    worlds = World(worlds_data)
    return worlds


class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        position = pygame.mouse.get_pos()

        if self.rect.collidepoint(position):

            if pygame.mouse.get_pressed()[0] and (not self.clicked):
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)
        return action




class World:
    def __init__(self, data):
        self.tile_list = []

        blocks_img = pygame.image.load('background/block_base_01.png')
        blocks_floor = pygame.image.load('background/block_floor2.png')
        blocks_dop = pygame.image.load('background/block_dop.png')
        counter_coins = 0
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:

                if tile == 1:
                    img = pygame.transform.scale(blocks_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 2:
                    img = pygame.transform.scale(blocks_floor, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 4:
                    img = pygame.transform.scale(blocks_floor, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 5 or tile == 9:
                    img = pygame.transform.scale(blocks_dop, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 3:
                    blob = Enemy(col_count * tile_size - 40, row_count * tile_size - 9)
                    blob_group.add(blob)

                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + 30)
                    lava_group.add(lava)

                if tile == 7:
                    counter_coins += 1
                    coins = Coin(col_count * tile_size + (tile_size // 2),
                                 row_count * tile_size - (tile_size // 2) + 10)
                    coin_group.add(coins)


                if tile == 8:
                    exits = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2) + 10)
                    exit_group.add(exits)

                col_count += 1
            row_count += 1

    def draw(self):

        for title in self.tile_list:
            screen.blit(title[0], title[1])


class Player:
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, games_over):
        dx = 0
        dy = 0
        walk_cooldown = 10

        if games_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and (not self.jump) and (not self.in_air):
                self.vel_y = -15
                self.jump = True
            if not key[pygame.K_SPACE]:
                self.jump = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.count += 1
                self.direction = - 1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.count += 1
                self.direction = 1
            if (not key[pygame.K_LEFT]) and (not key[pygame.K_RIGHT]):
                self.count = 0
                self.index = 0

                if self.direction == 1:
                    self.image = self.images_right[self.index]

                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # анимация
            if self.count > walk_cooldown:
                self.count = 0
                self.index += 1

                if self.index >= len(self.images_right):
                    self.index = 0

            if self.direction == 1:
                self.image = self.images_right[self.index]

            if self.direction == -1:
                self.image = self.images_left[self.index]

            # гравитация
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10

            dy += self.vel_y

            # коллизия
            self.in_air = True
            for tile in world.tile_list:

                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.hight):
                    dx = 0

                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.hight):

                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0

                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            if pygame.sprite.spritecollide(self, blob_group, False):
                games_over = -1

            if pygame.sprite.spritecollide(self, lava_group, False):
                games_over = -1

            if pygame.sprite.spritecollide(self, exit_group, False):
                games_over = 1

            self.rect.x += dx
            self.rect.y += dy

        elif games_over == -1:
            self.image = self.dead_image
            draw_text('You were expelled!', font, blue, screen_w // 2 - 260, screen_h // 2 - 110)

            if self.rect.y > 150:
                self.rect.y -= 5

        screen.blit(self.image, self.rect)
        return games_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.count = 0

        for num in range(1, 4):
            img_r = pygame.image.load(f'background/p{num}.png')
            img_r = pygame.transform.scale(img_r, (40, 60))
            img_l = pygame.transform.flip(img_r, True, False)
            self.images_right.append(img_r)
            self.images_left.append(img_l)

        self.dead_image = pygame.image.load('background/ghost_dead.png')
        dead_img_size = self.dead_image.get_size()
        new_size_dead = (int(dead_img_size[0] * 2.2), int(dead_img_size[1] * 2.2))
        self.dead_image = pygame.transform.scale(self.dead_image, new_size_dead)
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.hight = self.image.get_height()
        self.vel_y = 0
        self.jump = False
        self.direction = 0
        self.in_air = True


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('background/fair.png')
        image_size = self.image.get_size()
        new_size_img = (image_size[0] * 1.5, image_size[1] * 1.5)
        self.image = pygame.transform.scale(self.image, new_size_img)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_count = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_count += 1
        counter = 1

        if abs(self.move_count) > 50 and counter % 2:
            self.move_direction *= -1
            self.move_count *= -1
        counter += 1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('background/floor_fair.png')
        size_floor = img.get_size()
        new_floor_f = (size_floor[0] * 3, size_floor[1] * 3)
        img = pygame.transform.scale(img, new_floor_f)
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2 - 3))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_count = 0


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('background/windowOpen.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.2)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_count = 0


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('background/coin.png')
        self.image = pygame.transform.scale(img, (tile_size // 2 + 5, tile_size // 2 + 5))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


player = Player(100, screen_h - 200)
blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
score_coin = Coin(tile_size // 2 + 17, tile_size // 2)
coin_group.add(score_coin)

if path.exists(f'levels/level{level}_data'):
    pickle_in = open(f'levels/level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

restart_button = Button(screen_w // 2 - 50, screen_h // 2 - 50, restart_img)
start_button = Button(screen_w // 2 - 230, screen_h // 2 - 50, start_ing)
exit_button = Button(screen_w // 2 + 100, screen_h // 2 - 45, exit_ing)
logo_button = Button(screen_w // 2 - 70, screen_h // 2 - 300, img_logo)

run = True

while run:
    clock.tick(fps)
    screen.blit(bg_img, (0, 0))
    if main_menu:
        logo_button.draw()

        if exit_button.draw():
            run = False

        if start_button.draw():
            main_menu = False
    else:
        world.draw()

        if not game_over:
            blob_group.update()

            if pygame.sprite.spritecollide(player, coin_group, True):
                score += 1
            draw_text('your  RAY: ' + str(score), font_score, white, tile_size + 20, 6)

        blob_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        if game_over == -1:

            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0

        if game_over == 1:
            level += 1

            if level <= 9:
                world_data = []
                world = reset_level(level)
                game_over = 0

            else:
                draw_text('YOU GRADUATED!', font, blue, screen_w // 2 - 240, screen_h // 2 - 110)
                draw_text('RAY: ' + str(score / 200), font, blue, screen_w // 2 - 110, screen_h // 2 - 180)

                if restart_button.draw():
                    level = 0
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()

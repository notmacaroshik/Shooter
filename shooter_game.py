from pygame import *
from random import random, randint
from time import time as timer

# вынесем размер окна в константы для удобства
# W - width, ширина
# H - height, высота
WIN_W = 700
WIN_H = 500
ENEMY = 5
FPS = 144
WHITE = (255, 255, 255)
BLACK = (0, 0, 0 )
OHCKO = 15
LOX = 5
HP = 5
FIRES = 10
FIRES_RECHARGE = 3
ASTEROIDS = 3

# создание окна размером 700 на 500
window = display.set_mode((WIN_W, WIN_H))

class GameSprite(sprite.Sprite):
    def __init__(self, img, x, y, width=65, height=65, speed=5):
        super().__init__()
        self.image = transform.scale(image.load(img),(width, height))
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = x 
        self.rect.y = y
    def reset(self):
        window.blit(self.image,(self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, img, x, y, width=35, height=65, speed=5, hp=HP):
        super().__init__(img, x, y, width, height, speed)
        self.dead = 0
        self.lost = 0
        self.bulls =sprite.Group()
        self.hp = hp
        self.bullscount = 0
        self.is_recharge = False
        self.last_time = timer()
        self.kurrent_time = timer()
    def update(self):
        keys_pressed = key.get_pressed()
        if keys_pressed[K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys_pressed[K_d] and self.rect.x < WIN_W - 5 - self.rect.width:
            self.rect.x += self.speed
    def fire(self):
        bull = Bullet('bullet.png', self.rect.x + (self.rect.width // 2), self.rect.y)
        self.bullscount += 1
        self.bulls.add(bull)


class Enemy(GameSprite):
    def __init__(self, img, x, y, width=65, height=35, speed=1):
        super().__init__(img, x, y, width, height, speed)
    def update(self, rocket = None):
        if self.rect.y > WIN_H - self.rect.height:
            self.rect.x = randint(0,WIN_W - self.rect.width)
            self.rect.y = 0
            if rocket:
                rocket.lost += 1
        self.rect.y += self.speed

class Bullet(GameSprite):
    def __init__(self, img, x, y, width=5, height=10, speed=5):
        super().__init__(img, x, y, width, height, speed)
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y <= 0:
            self.kill()

clock = time.Clock()
# название окна
display.set_caption("")

# задать картинку фона такого же размера, как размер окна
background = transform.scale(
    image.load("galaxy.jpg"),
    # здесь - размеры картинки
    (WIN_W, WIN_H)
)

mixer.init()
mixer.music.load('space.ogg')
#mixer.music.play()
hit = mixer.Sound('fire.ogg')
font.init()
font_size = 70
myfont = font.SysFont('Verdana', font_size)

win = myfont.render('Сюда)', True, WHITE)
lose = myfont.render('Лошара)', True, WHITE)

myfont2 = font.SysFont('Verdana', font_size // 2)

scor_txt = myfont2.render('Cчет:', True, WHITE)
lost_txt = myfont2.render('Пропущено:', True, WHITE)
recharge = myfont2.render('Перезарядка', True, WHITE)

scor = myfont2.render('0', True, WHITE)
lost = myfont2.render('0', True, WHITE)

rocket = Player('rocket.png', 215,435)

enemys = sprite.Group()
for i in range(ENEMY):
    enemy = Enemy('ufo.png', randint(0,WIN_W-65), randint(0,100))
    enemys.add(enemy)

asteroids = sprite.Group()
for i in range(ASTEROIDS):
    asteroid = Enemy('asteroid.png', randint(0,WIN_W-65), randint(0,100), 65, 65)
    asteroids.add(asteroids)


finish = False
# игровой цикл
game = True
while game:

    # отобразить картинку фона

    
    # слушать события и обрабатывать
    for e in event.get():
        # выйти, если нажат "крестик"
        if e.type == QUIT:
            game = False
        if e.type == KEYDOWN:
            # если нажата клавиша Q
            if e.key == K_SPACE:
                if not rocket.is_recharge and rocket.bullscount < FIRES:
                    rocket.fire()
                if not rocket.is_recharge and rocket.bullscount >= FIRES:
                    rocket.is_recharge = True
                    rocket.last_time = timer()


    if not finish:
        window.blit(background,(0, 0))
        lost = myfont2.render(str(rocket.lost), True, WHITE) 
        window.blit(scor_txt,(0, 0))
        window.blit(lost_txt,(0, 40))
        window.blit(lost,(225, 40))
        window.blit(scor,(100, 0))
        rocket.reset()
        rocket.update()
        enemys.draw(window)
        enemys.update(rocket)
        asteroids.draw(window)
        asteroids.update()
        rocket.bulls.draw(window)
        rocket.bulls.update()

        if rocket.is_recharge:
            rocket.kurrent_time = timer()
            if rocket.kurrent_time - rocket.last_time < FIRES_RECHARGE:
                window.blit(recharge,(200,450))
            else:
                rocket.bullscount = 0
                rocket.is_recharge = False

        collide_enemys = sprite.spritecollide(
            rocket, enemys, True
        )

        collide_asteroids = sprite.spritecollide(
            rocket, asteroids, False
        )
        if collide_enemys:
            if rocket.hp > 0:
                rocket.hp -= 1
            else:
                window.blit(lose,(200, 200))
                display.update()
                finish = True

        if rocket.lost > LOX or collide_asteroids:
            window.blit(lose,(200, 200))
            display.update()
            finish = True

        enemy_vs_bull = sprite.groupcollide(
            enemys, rocket.bulls,True,True
        )
        if enemy_vs_bull:
            rocket.dead += 1
            enemy = Enemy('ufo.png', randint(0,WIN_W-65), randint(0,100))
            enemys.add(enemy)
            scor = myfont2.render(str(rocket.dead), True, WHITE)
        if rocket.dead > OHCKO:
            window.blit(win,(200, 200))
            display.update()
            finish = True

    else:
        finish = False
        rocket.dead = 0
        rocket.lost = 0
        rocket.bullscount = 0
        rocket.is_recharge = False
        #enemys.kill()
        #asteroids.kill()
        #rocket.bulls.kill()

        time.delay(3)

        # enemys = sprite.Group()
        # for i in range(ENEMY):
        #     enemy = Enemy('ufo.png', randint(0,WIN_W-65), randint(0,100))
        #     enemys.add(enemy)

        # asteroids = sprite.Group()
        # for i in range(ASTEROIDS):
        #     asteroid = Enemy('asteroid.png', randint(0,WIN_W-65), randint(0,100), 65, 65)
        #     asteroids.add(asteroids)
        # time.delay(50)

    display.update()     
    clock.tick(FPS)

import time, random
import board, digitalio
from PIL import Image, ImageDraw
from adafruit_rgb_display import st7789

W = H = 240
FPS = 20

cs  = digitalio.DigitalInOut(board.CE0)
dc  = digitalio.DigitalInOut(board.D25)
rst = digitalio.DigitalInOut(board.D24)

bl = digitalio.DigitalInOut(board.D26)
bl.switch_to_output()
bl.value = True

spi = board.SPI()
disp = st7789.ST7789(spi, width=W, height=H, rotation=180, y_offset=80,
                     cs=cs, dc=dc, rst=rst, baudrate=24000000)

def btn(pin):
    d = digitalio.DigitalInOut(pin)
    d.direction = digitalio.Direction.INPUT
    d.pull = digitalio.Pull.UP
    return d

LEFT, RIGHT = btn(board.D27), btn(board.D23)
JUMP = btn(board.D6)
ATTACK = btn(board.D5)

# 시작화면
mode = "title"
title_pressed = False

def any_button():
    return (not JUMP.value) or (not ATTACK.value)

#플레이어
player_image = Image.open("assets/knight_small.png").convert("RGBA")
player_image.thumbnail((20, 20))  
player_width = player_image.width // 2
player_height = player_image.height // 2

img = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(img)

player = [225, 200 - player_height]
speed = 2

#설정값
Gravity = 0.4
Velocity = 0.0
On_ground = True

prev = time.monotonic()
acc = 0.0
STEP = 1 / 60

# 문
door = Image.open("assets/door.png").convert("RGBA")
door.thumbnail((25, 20))

# 용암
lava = Image.open("assets/lava.png").convert("RGBA")
lava = lava.resize((240, 15))

# 기둥 사이즈
PILLARS = [
    (210, 200, W),
    (170, 165, 185),
    (130, 130, 145),
    (90, 95, 105),
    (50, 60, 65),
    (0, 25, 30),
]
stand = 0
Pillar_on = [True, True, True, True, True, True]
timer = 0.0
trap = False

def game_stage(n):
    global stage, player, Velocity, On_ground, stand

# 리셋 값
def reset_game():
    global player, Velocity, On_ground, stand, Pillar_on, timer, trap
    player = [225, 200 - player_height]
    Velocity = 0.0
    On_ground = True
    stand = 0
    Pillar_on = [True, True, True, True, True, True]
    timer = 0.0
    trap = False

while True:
    now = time.monotonic()
    acc += now - prev
    prev = now
    if acc > 0.25:
        acc = 0.0

    while acc >= STEP:

        # 시작 화면
        if mode == "title":
            if any_button():
                title_pressed = True
            elif title_pressed:
                title_pressed = False
                reset_game()
                mode = "play"
            acc -= STEP
            continue
        
        # 사망 화면
        if mode == "dead":
            if any_button():
                title_pressed = True
            elif title_pressed:
                title_pressed = False
                mode = "title"
            acc -= STEP
            continue
            
        # 기둥 타이머
        if timer > 0:
            timer -= STEP
            if timer <= 0:
                Pillar_on[3] = True
                

        # 좌우이동
        dx = 0
        if not LEFT.value:
            dx -= speed
        if not RIGHT.value:
            dx += speed
        player[0] += dx
        player[0] = max(player_width, min(W - player_width, player[0]))

        # 기둥 옆면 충돌 판정
        feet = player[1] + player_height
        i = 0
        for x1, y1, x2 in PILLARS:
            if Pillar_on[i]:
                crash_x = player[0] + player_width > x1 and player[0] - player_width < x2
                if crash_x and feet > y1 + 1:
                    if dx > 0:
                        player[0] = x1 - player_width
                    elif dx < 0:
                        player[0] = x2 + player_width
            i += 1


        # 점프
        if not JUMP.value and On_ground:
            Velocity = - 6.0
            On_ground = False

        if stand == 2 and On_ground == False and trap == False:
            Pillar_on[3] = False
            timer = 0.8
            trap = True

        # 중력
        before_feet = player[1] + player_height
        Velocity += Gravity
        player[1] += Velocity
        after_feet = player[1] + player_height

        # 기둥 위 착지
        On_ground = False
        i = 0
        for x1, y1, x2 in PILLARS:
            if Pillar_on[i]:
                crash_x = player[0] + player_width > x1 and player[0] - player_width < x2
                if crash_x and Velocity >= 0 and before_feet <= y1 and after_feet >= y1:
                    player[1] = y1 - player_height
                    Velocity = 0.0
                    On_ground = True
                    stand = i
                    break
            i += 1
        
        if after_feet >= 230:
            reset_game()
            mode = "dead"
            title_pressed = False

        acc -= STEP


    # 시작 화면 및 배경 그리기
    if mode == "title":
        draw.rectangle((0, 0, W, H), fill=(30, 30, 40))
        draw.text((25, 60), "REGRET TOWER", fill=(230, 70, 50), font_size = 26)
        draw.text((60, 175), "PRESS ANY BUTTON", fill=(255, 255, 255), font_size = 13)

    elif mode == "dead":
        draw.rectangle((0, 0, W, H), fill = (60, 10, 5))
        draw.text((45, 60), "GAME OVER", fill = (255, 140, 30), font_size = 26)
        draw.text((60, 175), "PRESS ANY BUTTON", fill=(255, 255, 255), font_size = 13)

    else:
        draw.rectangle((0, 0, W, H), fill=(80, 80, 80))
        j = 0
        for x1, y1, x2 in PILLARS:
            if Pillar_on[j]:
                draw.rectangle((x1, y1, x2, H), fill=(150, 150, 150))
            j += 1
            img.paste(lava, (0, 240 - 15), lava)
            img.paste(door, (2, 5), door)
        img.paste(player_image, (int(player[0] - player_width), int(player[1] - player_height)), player_image)
    
    disp.image(img)

    time.sleep(max(0, 1 / FPS - (time.monotonic() - now)))


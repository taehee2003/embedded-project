"""game.py의 pygame 버전: HDMI 모니터에 전체 화면으로 표시.

조작: 키보드 ←/→ 이동, R 점수 초기화, ESC 종료
      GPIO 버튼(LEFT=D27, RIGHT=D23, CENTER=D4)도 그대로 사용 가능
"""
import random
import pygame

# 게임 로직은 원래와 같은 240x240 좌표계에서 돌리고, 화면에 맞게 확대해서 그린다.
W = H = 240
STEP = 1 / 60

# GPIO 버튼: 없거나 사용할 수 없으면 키보드만으로 동작
try:
    import board, digitalio

    def btn(pin):
        d = digitalio.DigitalInOut(pin)
        d.direction = digitalio.Direction.INPUT
        d.pull = digitalio.Pull.UP
        return d

    LEFT, RIGHT, CENTER = btn(board.D27), btn(board.D23), btn(board.D4)
    pressed = lambda b: not b.value
except Exception as e:
    print("GPIO 버튼 없이 키보드로만 실행합니다:", e)
    LEFT = RIGHT = CENTER = None
    pressed = lambda b: False

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Pi Game")
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

SW, SH = screen.get_size()
scale = min(SW, SH) // H or 1            # 정수 배율 → 선명하게 확대
view = pygame.Rect(0, 0, W * scale, H * scale)
view.center = (SW // 2, SH // 2)

canvas = pygame.Surface((W, H))
font = pygame.font.Font(None, 20)

player = [W // 2, H - 40]
ball = [W // 2, 40]
score = 0
speed = 4
acc = 0.0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False
            elif event.key == pygame.K_r:
                score = 0

    acc += clock.tick(60) / 1000
    if acc > 0.25:
        acc = 0.0

    keys = pygame.key.get_pressed()
    while acc >= STEP:
        if keys[pygame.K_LEFT] or pressed(LEFT):
            player[0] -= speed
        if keys[pygame.K_RIGHT] or pressed(RIGHT):
            player[0] += speed
        player[0] = max(12, min(W - 12, player[0]))

        ball[1] += 3
        if ball[1] > H:
            ball[1] = 0
            ball[0] = random.randint(20, W - 20)
            score -= 1

        if abs(ball[1] - player[1]) < 12 and abs(ball[0] - player[0]) < 20:
            ball[1] = 0
            ball[0] = random.randint(20, W - 20)
            score += 1

        if pressed(CENTER):
            score = 0

        acc -= STEP

    canvas.fill((10, 10, 25))
    pygame.draw.rect(canvas, (0, 220, 140),
                     (player[0] - 20, player[1] - 6, 40, 12))
    pygame.draw.circle(canvas, (255, 200, 0), ball, 6)
    canvas.blit(font.render(f"SCORE {score}", True, (255, 255, 255)), (8, 8))

    screen.fill((0, 0, 0))
    screen.blit(pygame.transform.scale(canvas, view.size), view)
    pygame.display.flip()

pygame.quit()

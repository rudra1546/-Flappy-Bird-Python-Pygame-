import pygame, random, sys
pygame.init()

# Screen
WIDTH, HEIGHT = 400, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Colors & Fonts
WHITE, BLUE, GREEN = (255,255,255), (0,155,255), (0,200,0)
font = pygame.font.SysFont("Arial", 64, bold=True)
score_font = pygame.font.SysFont("Arial", 32)

# Bird
bird_img = pygame.image.load("bird.png").convert_alpha()
bird_img = pygame.transform.scale(bird_img, (30, 30))  # same size as before
# Bird rectangle
bird_rect = bird_img.get_rect(topleft=(50, 250))
# Physics
gravity, velocity, jump = 0.25, 0, -7
# ---- inside your game loop when drawing ----
win.blit(bird_img, bird_rect)
# Pipes
pipe_width, pipe_gap = 70, 150
pipes = []   # list of (rect, id)
pipe_id = 0  # unique ID for each pipe pair
for i in range(3):
    x = 300 + i * 200
    h = random.randint(100, 400)
    pipes += [(pygame.Rect(x,0,pipe_width,h), pipe_id),
              (pygame.Rect(x,h+pipe_gap,pipe_width,HEIGHT), pipe_id)]
    pipe_id += 1

# Score
score, pipe_speed = 0, 2
scored_pipes = set()   # track scored pipe IDs

def draw():
    win.fill(BLUE)
    win.blit(bird_img, bird_rect)
    for p, _ in pipes: pygame.draw.rect(win, GREEN, p)
    win.blit(score_font.render(f"Score: {score}", True, WHITE),(10,10))
    pygame.display.update()

def reset():
    global bird_rect, velocity, pipes, score, scored_pipes, pipe_id
    bird_rect, velocity, score = pygame.Rect(50,250,30,30), 0, 0
    scored_pipes.clear()
    pipes.clear()
    pipe_id = 0
    for i in range(3):
        x = 300 + i * 200
        h = random.randint(100, 400)
        pipes += [(pygame.Rect(x,0,pipe_width,h), pipe_id),
                  (pygame.Rect(x,h+pipe_gap,pipe_width,HEIGHT), pipe_id)]
        pipe_id += 1

# Game loop
clock, run = pygame.time.Clock(), True
while run:
    clock.tick(60)
    velocity += gravity; bird_rect.y += int(velocity)

    for e in pygame.event.get():
        if e.type == pygame.QUIT: run = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE: velocity = jump

    # Move pipes
    for p, _ in pipes: p.x -= pipe_speed

    # Score: when bird passes a TOP pipe
    for i in range(0,len(pipes),2):
        top_pipe, pid = pipes[i]
        if bird_rect.left > top_pipe.right and pid not in scored_pipes:
            score += 1
            scored_pipes.add(pid)

    # Recycle pipes
    if pipes[0][0].x + pipe_width < 0:
        pipes = pipes[2:]  # drop first pair
        x = pipes[-1][0].x + 200
        h = random.randint(100, 400)
        pipes += [(pygame.Rect(x,0,pipe_width,h), pipe_id),
                  (pygame.Rect(x,h+pipe_gap,pipe_width,HEIGHT), pipe_id)]
        pipe_id += 1

    # Collision
   # i = 1
  #  while True:
    if bird_rect.top<=0 or bird_rect.bottom>=HEIGHT or any(bird_rect.colliderect(p) for p,_ in pipes):
        reset()
    # if not (i <= 3):  # condition check at the end
    #    break
    draw()

pygame.quit(); sys.exit()

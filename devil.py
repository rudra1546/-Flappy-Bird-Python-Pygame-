# level_devil.py
import pygame as pg, sys, math, random
pg.init()
W,H=960,540; screen=pg.display.set_mode((W,H)); pg.display.set_caption("Level Devil (Python)")
clock=pg.time.Clock(); FONT=pg.font.SysFont("consolas",24)

# -------------------- helpers --------------------
GRAV=0.7; JUMP=12; SPD=5
def rect(x,y,w,h,c): pg.draw.rect(screen,c,(x,y,w,h))
def text(s,x,y,c=(255,255,255)): screen.blit(FONT.render(s,True,c),(x,y))

class Player:
    def __init__(s,spawn): s.x,s.y=spawn; s.vx=s.vy=0; s.w,s.h=28,36; s.on_g=False; s.dead=False; s.color=(240,230,90)
    @property
    def r(s): return pg.Rect(s.x,s.y,s.w,s.h)
    def reset(s,spawn): s.__init__(spawn)
    def update(s,keys):
        s.vx=(keys[pg.K_RIGHT]-keys[pg.K_LEFT])*SPD
        if keys[pg.K_UP] and s.on_g: s.vy=-JUMP
        s.vy+=GRAV; s.x+=s.vx; s.y+=s.vy

class Thing: # generic for spikes, platforms, etc.
    def __init__(s,rect,type,**kw): s.rect=pg.Rect(rect); s.type=type; s.t=0; s.enabled=True; s.__dict__.update(kw)
    def draw(s):
        if s.type=="plat": rect(s.rect.x,s.rect.y,s.rect.w,s.rect.h,(90,90,120))
        elif s.type=="goal": rect(s.rect.x,s.rect.y,s.rect.w,s.rect.h,(80,220,120))
        elif s.type=="spike":
            # draw triangles
            n=max(1,s.rect.w//20); w=s.rect.w/n
            for i in range(n):
                x=s.rect.x+i*w; pg.draw.polygon(screen,(220,80,80),[(x,s.rect.bottom),(x+w/2,s.rect.y),(x+w,s.rect.bottom)])
        elif s.type=="fake":
            if not s.broken: rect(s.rect.x,s.rect.y,s.rect.w,s.rect.h,(70,140,160))
        elif s.type=="popup":
            if s.up: Thing((s.rect.x,s.rect.y,s.rect.w,s.h),"spike").draw()
        elif s.type=="moving":
            rect(s.rect.x,s.rect.y,s.rect.w,s.rect.h,(110,110,160))
        elif s.type=="hint":
            text(s.msg,s.rect.x,s.rect.y,(200,200,200))

    def update(s,player,dt):
        s.t+=dt
        if s.type=="fake" and not s.broken and player.r.colliderect(s.rect) and player.vy>0:
            s.broken=True; s.drop_v=0
        if s.type=="fake" and s.broken:
            s.drop_v+=GRAV; s.rect.y+=s.drop_v
        if s.type=="popup":
            if not s.triggered and player.r.centerx> s.trigger_x: s.triggered=True; s.up=True; s.h=0
            if s.triggered and s.up and s.h<s.max_h: s.h+=8
        if s.type=="moving":
            # sinusoidal or ping-pong
            if s.axis=="x":
                s.rect.x=int(s.cx+s.amp*math.sin(s.t*s.spd))
            else:
                s.rect.y=int(s.cy+s.amp*math.sin(s.t*s.spd))

# -------------------- levels --------------------
def make_levels():
    levels=[]
    # Level 1: fake floor near flag + popup spikes on approach
    L=[]
    ground=Thing((0,H-40,W,40),"plat"); L+=[ground]
    L+=[Thing((100, H-140,160,20),"plat"), Thing((360,H-220,120,20),"plat")]
    L+=[Thing((560,H-300,120,20),"plat"), Thing((760,H-380,140,20),"plat")]
    L+=[Thing((870,H-420,30,40),"goal")]
    L+=[Thing((790,H-380,110,20),"fake",broken=False,drop_v=0)]
    L+=[Thing((720,H-60,120,28),"spike")]
    L+=[Thing((820,H-420,80,40),"popup",trigger_x=730,triggered=False,up=False,max_h=36,h=0)]
    levels.append({"spawn":(40,H-76),"things":L,"msg":"L1: Trust nothing."})

    # Level 2: moving platform baits + spikes below + popup behind start
    L=[]
    L+=[Thing((0,H-40,W,40),"plat"), Thing((820,H-60,120,20),"spike")]
    L+=[Thing((140,H-180,120,18),"moving",axis="y",cy=H-180,cx=140,amp=70,spd=2.0)]
    L+=[Thing((420,H-260,120,18),"moving",axis="x",cx=420,cy=H-260,amp=90,spd=2.2)]
    L+=[Thing((640,H-340,120,18),"plat")]
    L+=[Thing((880,H-420,40,40),"goal")]
    L+=[Thing((20,H-80,70,30),"popup",trigger_x=60,triggered=False,up=False,max_h=34,h=0)]
    L+=[Thing((300,H-60,100,28),"spike")]
    levels.append({"spawn":(30,H-76),"things":L,"msg":"L2: The floor bites."})

    # Level 3: tight jumps, hidden fake, mid-air spike rise
    L=[]
    L+=[Thing((0,H-40,W,40),"plat")]
    L+=[Thing((160,H-160,120,18),"plat"), Thing((320,H-240,120,18),"plat")]
    L+=[Thing((480,H-320,120,18),"fake",broken=False,drop_v=0)]
    L+=[Thing((700,H-400,120,18),"plat"), Thing((880,H-440,40,40),"goal")]
    L+=[Thing((520,H-60,160,28),"spike")]
    L+=[Thing((600,H-380,80,40),"popup",trigger_x=560,triggered=False,up=False,max_h=40,h=0)]
    L+=[Thing((350,H-60,120,28),"spike")]
    levels.append({"spawn":(40,H-76),"things":L,"msg":"L3: Last laugh."})
    return levels

levels=make_levels()
lvl=0; deaths=0; timer=0

def collide_player_with_level(p,things):
    p.on_g=False
    # platforms first (incl. moving)
    for t in things:
        if t.type in ("plat","moving") and p.r.colliderect(t.rect):
            # horizontal vs vertical resolution
            r=p.r
            dx=min(r.right - t.rect.left, t.rect.right - r.left)
            dy=min(r.bottom - t.rect.top, t.rect.bottom - r.top)
            if dx<dy: # resolve x
                if r.centerx<t.rect.centerx: p.x-=dx
                else: p.x+=dx
                p.vx=0
            else: # resolve y
                if r.centery<t.rect.centery:
                    p.y-=dy; p.vy=0; p.on_g=True
                else:
                    p.y+=dy; p.vy=0
    # hazards
    for t in things:
        if t.type=="spike":
            if p.r.colliderect(t.rect.inflate(-4,-6)): return True
        if t.type=="popup" and t.up:
            hit=pg.Rect(t.rect.x,t.rect.y,t.rect.w,t.h)
            if p.r.colliderect(hit.inflate(-4,-6)): return True
    # goal
    for t in things:
        if t.type=="goal" and p.r.colliderect(t.rect): return "goal"
    # fell
    if p.y>H+100: return True
    return False

def draw_ui():
    text(f"Level: {lvl+1}/{len(levels)}",10,8)
    text(f"Deaths: {deaths}",10,34)
    text(f"Time: {timer/1000:.1f}s",10,60)

player=Player(levels[lvl]["spawn"])

# -------------------- main loop --------------------
while True:
    dt=clock.tick(60); timer+=dt
    for e in pg.event.get():
        if e.type==pg.QUIT: pg.quit(); sys.exit()
        if e.type==pg.KEYDOWN and e.key==pg.K_r:
            player.reset(levels[lvl]["spawn"])

    keys=pg.key.get_pressed()
    player.update(keys)
    # update level things (AI)
    for t in levels[lvl]["things"]:
        t.update(player, dt/1000)

    # collisions and deaths
    hit=collide_player_with_level(player,levels[lvl]["things"])
    if hit is True:
        deaths+=1; player.reset(levels[lvl]["spawn"])
    elif hit=="goal":
        lvl+=1
        if lvl>=len(levels):
            # win screen
            screen.fill((15,18,26))
            text("You survived the devilish levels!", W//2-250, H//2-20, (120,230,160))
            text(f"Deaths: {deaths}   Time: {timer/1000:.1f}s   Press ESC to quit", W//2-300, H//2+18,(220,220,220))
            pg.display.flip()
            # wait loop
            while True:
                for e in pg.event.get():
                    if e.type==pg.QUIT: pg.quit(); sys.exit()
                    if e.type==pg.KEYDOWN and e.key==pg.K_ESCAPE: pg.quit(); sys.exit()
                clock.tick(30)
        else:
            player.reset(levels[lvl]["spawn"])

    # render
    screen.fill((18,20,28))
    # background parallax lines
    for i in range(0,W,40): pg.draw.line(screen,(30,32,45),(i,0),(i,H))
    for t in levels[lvl]["things"]: t.draw()
    rect(player.x,player.y,player.w,player.h,player.color)
    draw_ui()
    # level hint
    text(levels[lvl]["msg"], W-400, 10, (180,180,220))
    text("R to reset", W-140, 36, (160,160,160))
    pg.display.flip()

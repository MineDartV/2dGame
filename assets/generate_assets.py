from PIL import Image, ImageDraw, ImageOps
import random

def grass_tile():
    img = Image.new('RGBA', (32, 32), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Dirt base with shadow
    for y in range(16, 32):
        for x in range(32):
            base = 139 + random.randint(-8,8)
            shadow = int(base * (0.85 if x > 24 else 1.0))
            color = (shadow, 69 + random.randint(-8,8), 19 + random.randint(-4,4))
            draw.point((x,y), fill=color)
    # Grass top with highlights and shadow
    for y in range(0, 16):
        for x in range(32):
            base = 34 + random.randint(-6,6)
            shadow = int(base * (0.85 if x < 8 else 1.0))
            highlight = min(255, int(base * (1.12 if 12 < x < 20 and y < 4 else 1.0)))
            color = (highlight, 139 + random.randint(-10,10), 34 + random.randint(-6,6))
            draw.point((x,y), fill=color)
    # Grass edge and highlight
    draw.rectangle([0,15,31,16], fill=(44, 160, 44))
    for x in range(6,26):
        draw.point((x,14), fill=(200,255,200))
    img.save('assets/grass.png')

def dirt_tile():
    img = Image.new('RGBA', (32, 32), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    for y in range(32):
        for x in range(32):
            base = 139 + random.randint(-10,10)
            shadow = int(base * (0.9 if y > 20 else 1.0))
            color = (shadow, 69 + random.randint(-10,10), 19 + random.randint(-8,8))
            draw.point((x,y), fill=color)
    # Pebbles and shadow
    for _ in range(8):
        px, py = random.randint(2,29), random.randint(2,29)
        draw.ellipse([px,py,px+2,py+2], fill=(100,80,40,180))
    # Gradient shadow at bottom
    for y in range(28,32):
        for x in range(32):
            draw.point((x,y), fill=(90, 50, 15, 200))
    img.save('assets/dirt.png')

def stone_tile():
    img = Image.new('RGBA', (32, 32), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    for y in range(32):
        for x in range(32):
            base = 120 + random.randint(-18,18)
            shadow = int(base * (0.8 if y > 20 else 1.0))
            draw.point((x,y), fill=(shadow,shadow,shadow))
    # Add cracks and shadow
    for _ in range(3):
        x0 = random.randint(0,20)
        y0 = random.randint(10,28)
        draw.line([x0,y0,x0+random.randint(6,11),y0+random.randint(-3,3)], fill=(70,70,70), width=1)
    for y in range(28,32):
        for x in range(32):
            draw.point((x,y), fill=(60,60,60,180))
    img.save('assets/stone.png')

def tree_sprite():
    img = Image.new('RGBA', (32, 96), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Trunk with shading
    for y in range(32,96):
        for x in range(12,20):
            base = 139 + random.randint(-8,8)
            shadow = int(base * (0.75 if x > 16 else 1.0))
            draw.point((x,y), fill=(shadow, 69 + random.randint(-8,8), 19 + random.randint(-4,4)))
    # Foliage (3 layers with highlight)
    for i, (w,h,dy) in enumerate([(32,18,0),(28,16,10),(24,14,20)]):
        for y in range(h):
            for x in range(w):
                if (x-0.5*w)**2 + (y-0.5*h)**2 < (0.5*w)**2:
                    base = 34 + random.randint(-6,6)
                    highlight = min(255, int(base * (1.18 if x > w//2 else 1.0)))
                    color = (highlight, 139 + random.randint(-10,10), 34 + random.randint(-6,6), 255)
                    draw.point((x+16-w//2, y+dy), fill=color)
    img.save('assets/tree.png')




def goblin_sprite():
    img = Image.new('RGBA', (96, 144), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # Body (pixelated, dithered green)
    for y in range(72, 130):
        for x in range(36, 60):
            base = (34 + random.randint(-12,12), 139 + random.randint(-30,30), 34 + random.randint(-12,12))
            if x > 48:
                base = (24 + random.randint(-12,12), 100 + random.randint(-30,30), 24 + random.randint(-12,12))
            draw.point((x, y), fill=base)
    # Legs
    for y in range(130, 142):
        for x in range(38, 48):
            draw.point((x, y), fill=(30 + random.randint(-10,10),80 + random.randint(-10,10),30 + random.randint(-10,10)))
        for x in range(48, 58):
            draw.point((x, y), fill=(30 + random.randint(-10,10),80 + random.randint(-10,10),30 + random.randint(-10,10)))
    # Feet
    for y in range(140, 144):
        for x in range(38, 48):
            draw.point((x, y), fill=(60 + random.randint(-20,10),100 + random.randint(-10,10),60))
        for x in range(48, 58):
            draw.point((x, y), fill=(60 + random.randint(-20,10),100 + random.randint(-10,10),60))
    # Arms (dithered)
    for y in range(90, 120):
        for x in range(24, 36):
            draw.point((x, y), fill=(144 + random.randint(-20,20),238 + random.randint(-30,30),144 + random.randint(-20,20)))
        for x in range(60, 72):
            draw.point((x, y), fill=(144 + random.randint(-20,20),238 + random.randint(-30,30),144 + random.randint(-20,20)))
    # Head (blocky, pixelated, dithered)
    for y in range(24, 72):
        for x in range(24, 72):
            if (x-48)**2 + (y-48)**2 < 24**2:
                draw.point((x, y), fill=(144 + random.randint(-15,15),238 + random.randint(-30,30),144 + random.randint(-15,15)))
    # Cheek highlight
    for y in range(50, 62):
        for x in range(50, 64):
            if random.random() < 0.25:
                draw.point((x, y), fill=(255,255,255,80))
    # Eyes (yellow pixel dots)
    for y in range(50,54):
        for x in range(42,44):
            draw.point((x, y), fill=(220,220,60))
        for x in range(60,62):
            draw.point((x, y), fill=(220,220,60))
    # Mouth (pixel arc)
    for x in range(52,56):
        draw.point((x, 65), fill=(60,120,60))
    # Pixelated hair (dark green, with color noise)
    for y in range(22, 32):
        for x in range(28, 69, 3):
            if random.random() > 0.25:
                draw.rectangle([x, y, x+2, y+random.randint(2,4)], fill=(40 + random.randint(-20,20),80 + random.randint(-20,20),40 + random.randint(-10,10)))
    # Ears (pixelated, left/right)
    for y in range(36, 60):
        if random.random() > 0.7:
            draw.point((18, y), fill=(144 + random.randint(-15,15),238 + random.randint(-30,30),144 + random.randint(-15,15)))
        if random.random() > 0.7:
            draw.point((78, y), fill=(144 + random.randint(-15,15),238 + random.randint(-30,30),144 + random.randint(-15,15)))
    img.save('assets/goblin.png')

grass_tile()
dirt_tile()
stone_tile()
tree_sprite()

def hero_sprite():
    from PIL import Image, ImageOps
    # Terraria-style side-view hero: big square head, wide body, two legs, arm, shoes, clear face direction
    base = Image.new('RGBA', (20, 40), (0,0,0,0))
    px = base.load()
    # Colors
    SKIN = (210, 140, 80, 255)
    HAIR = (92, 44, 18, 255)
    EYE_WHITE = (255, 255, 255, 255)
    EYE_OUTLINE = (40, 20, 10, 255)
    SHIRT = (80, 120, 200, 255)
    SHIRT_SH = (40, 60, 120, 255)
    PANTS = (90, 70, 40, 255)
    PANTS_SH = (60, 40, 20, 255)
    SHOE = (60, 30, 10, 255)
    OUTLINE = (20, 10, 5, 255)
    # --- HEAD (8x8, offset forward) ---
    for y in range(2,10):
        for x in range(6,14):
            px[x,y] = SKIN
    for x in range(6,14): px[x,2] = HAIR
    for x in range(6,14): px[x,3] = HAIR
    for x in range(6,14): px[x,9] = OUTLINE
    for y in range(2,10): px[6,y] = OUTLINE
    for y in range(2,10): px[13,y] = OUTLINE
    # Face (right)
    px[12,5] = EYE_WHITE
    px[13,5] = EYE_OUTLINE
    # --- BODY (6x8, under head) ---
    for y in range(10,18):
        for x in range(8,14): px[x,y] = SHIRT
    for y in range(16,18):
        for x in range(8,14): px[x,y] = SHIRT_SH
    for x in range(8,14): px[x,10] = OUTLINE
    for x in range(8,14): px[x,17] = OUTLINE
    for y in range(10,18): px[8,y] = OUTLINE
    for y in range(10,18): px[13,y] = OUTLINE
    # --- ARM (side, visible) ---
    for y in range(12,18): px[14,y] = SKIN
    for y in range(16,18): px[14,y] = (160, 100, 60, 255)
    for y in range(12,18): px[14,y] = OUTLINE
    # --- LEGS (two, spaced) ---
    for y in range(18,32): px[9,y] = PANTS
    for y in range(18,32): px[12,y] = PANTS
    for y in range(30,32): px[9,y] = PANTS_SH
    for y in range(30,32): px[12,y] = PANTS_SH
    for y in range(18,32): px[8,y] = OUTLINE
    for y in range(18,32): px[13,y] = OUTLINE
    # --- SHOES ---
    for y in range(32,35): px[9,y] = SHOE
    for y in range(32,35): px[12,y] = SHOE
    for y in range(32,35): px[8,y] = OUTLINE
    for y in range(32,35): px[13,y] = OUTLINE
    # Save right-facing
    base.save('assets/hero_right.png')
    # Save left-facing (flipped)
    base_left = ImageOps.mirror(base)
    base_left.save('assets/hero_left.png')

hero_sprite()
goblin_sprite()

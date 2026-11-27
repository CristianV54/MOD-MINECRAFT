#!/usr/bin/env python3
"""Variante "Sombra Roxa com capuz": pega a skin Sombra Roxa e desenha um capuz na camada de
cima da cabeça (topo, lados e nuca fechados; na frente, só a moldura com borda roxa).
Uso: python3 tools/gerar_skin_sombra_roxa_capuz.py arte/skins/sombra_roxa.png arte/skins/sombra_roxa_capuz.png
"""
import random
import sys
from PIL import Image

random.seed(7)
sk = Image.open(sys.argv[1]).convert("RGBA")
px = sk.load()
PANO = [(14, 10, 20), (20, 14, 28), (10, 8, 14), (24, 18, 34)]
NEON, NEON_C = (122, 26, 214), (168, 85, 255)


def pano():
    return random.choice(PANO) + (255,)


# camada de cima da cabeça: topo (40,0), lados (32,8) e (48,8), nuca (56,8), frente (40,8)
for x in range(40, 48):
    for y in range(0, 8):
        px[x, y] = pano()                       # topo fechado
for (x0, y0) in [(32, 8), (48, 8), (56, 8)]:
    for x in range(x0, x0 + 8):
        for y in range(y0, y0 + 8):
            px[x, y] = pano()                   # lados e nuca fechados
# ponta do capuz caindo na nuca
for x in range(59, 61):
    px[x, 15] = NEON + (255,)
# frente: moldura em volta do rosto (2 linhas em cima, 1 coluna de cada lado), borda roxa por dentro
for x in range(40, 48):
    for y in range(8, 16):
        px[x, y] = (0, 0, 0, 0)
for x in range(40, 48):
    px[x, 8] = pano(); px[x, 9] = pano()
for y in range(8, 16):
    px[40, y] = pano(); px[47, y] = pano()
for x in range(41, 47):
    px[x, 10] = (NEON_C if x in (41, 46) else NEON) + (255,)    # borda roxa na testa
for y in range(10, 16):
    px[41, y] = NEON + (255,) if y < 12 else px[41, y]
    px[46, y] = NEON + (255,) if y < 12 else px[46, y]
sk.save(sys.argv[2])

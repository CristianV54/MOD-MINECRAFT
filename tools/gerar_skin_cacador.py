#!/usr/bin/env python3
"""Gera a skin "Caçador da Ordem" (64x64). Uso: python3 tools/gerar_skin_cacador.py arte/skins/cacador_da_ordem.png"""
import random, sys
from PIL import Image
random.seed(5)
sk = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
px = sk.load()

def var(c, a=10):
    d = random.randint(-a, a)
    return tuple(max(0, min(255, v + d)) for v in c[:3]) + (255,)

def fill(x, y, w, h, c, a=8):
    for i in range(x, x + w):
        for j in range(y, y + h):
            px[i, j] = var(c, a)

def p(x, y, c): px[x, y] = c + (255,) if len(c) == 3 else c

PELE, PELE_S = (200, 150, 118), (168, 118, 90)
CAPUZ, CAPUZ_S = (44, 38, 54), (30, 26, 38)
COURO, COURO_S = (70, 52, 44), (52, 38, 32)
ROXO, ROXO_C = (122, 70, 205), (190, 150, 255)
CALCA, BOTA, OURO = (40, 40, 50), (78, 54, 38), (214, 170, 60)

# ---------------- cabeça (base): pele, com sombra do capuz em cima
for (x, y) in [(0, 8), (8, 8), (16, 8), (24, 8)]:
    fill(x, y, 8, 8, PELE, 6)
fill(8, 0, 8, 8, CAPUZ); fill(16, 0, 8, 8, PELE_S)
fill(8, 8, 8, 2, CAPUZ_S, 4)                       # sombra do capuz na testa
fill(9, 11, 2, 1, (240, 240, 245), 0); fill(13, 11, 2, 1, (240, 240, 245), 0)   # olhos
p(10, 11, ROXO_C); p(13, 11, ROXO_C)               # íris de ametista
fill(9, 10, 2, 1, PELE_S, 3); fill(13, 10, 2, 1, PELE_S, 3)   # sobrancelhas na sombra
p(12, 12, PELE_S)                                   # nariz
fill(11, 14, 2, 1, (130, 84, 70), 0)                # boca
p(14, 13, (150, 100, 80))                           # cicatriz
for x in (0, 16, 24):
    fill(x, 8, 8, 3, CAPUZ, 4)                      # cabelo/capuz nas laterais e atrás
fill(24, 8, 8, 8, CAPUZ, 6)
# ---------------- capuz (camada de cima da cabeça)
fill(40, 0, 8, 8, CAPUZ, 6)                         # topo
fill(32, 8, 8, 8, CAPUZ, 6); fill(48, 8, 8, 8, CAPUZ, 6); fill(56, 8, 8, 8, CAPUZ, 6)
for i in range(8): px[40 + i, 8] = var(CAPUZ, 4)    # borda do capuz na testa
for j in range(8, 16):                               # laterais do capuz emoldurando o rosto
    px[40, j] = var(CAPUZ, 4); px[47, j] = var(CAPUZ, 4)
for j in range(9, 13): px[41, j] = var(CAPUZ_S, 3); px[46, j] = var(CAPUZ_S, 3)
for i in range(1, 7): px[40 + i, 9] = var(CAPUZ_S, 3) if i in (1, 6) else (0, 0, 0, 0)
for i in range(8): px[40 + i, 15] = var(ROXO, 6) if i in (0, 7) else px[40 + i, 15]   # cordão roxo do capuz
# ---------------- corpo: casaco de couro com faixa roxa e fragmento do Selo
fill(20, 16, 8, 4, COURO); fill(28, 16, 8, 4, COURO_S)
fill(16, 20, 4, 12, COURO); fill(28, 20, 4, 12, COURO); fill(32, 20, 8, 12, COURO)
fill(20, 20, 8, 12, COURO)
for j in range(20, 32):
    px[23, j] = var(ROXO, 6); px[24, j] = var(ROXO, 6)      # fechamento roxo
fill(20, 27, 8, 2, (60, 40, 28), 4)                          # cinto
fill(23, 27, 2, 2, OURO, 6)                                  # fivela
p(21, 22, ROXO_C); p(21, 23, ROXO); p(22, 23, ROXO_C); p(21, 24, ROXO)   # fragmento no peito
fill(32, 27, 8, 2, (60, 40, 28), 4)                                         # costas: cinto
for (x, y, c) in [(35, 21, ROXO_C), (36, 21, ROXO), (34, 22, ROXO), (35, 22, ROXO_C), (36, 22, ROXO), (37, 22, ROXO),
                  (34, 23, ROXO), (35, 23, ROXO), (36, 23, ROXO_C), (37, 23, ROXO), (35, 24, ROXO), (36, 24, ROXO)]:
    px[x, y] = var(c, 4)                                                     # fragmento do Selo nas costas
# camada de cima do corpo: gola do capuz
fill(20, 36, 8, 2, CAPUZ, 4); fill(32, 36, 8, 3, CAPUZ, 4); fill(16, 36, 4, 2, CAPUZ, 4); fill(28, 36, 4, 2, CAPUZ, 4)
fill(20, 32, 8, 4, CAPUZ, 4)
# ---------------- braços (largos): manga de couro, bracelete, mão
def braco(x0, y0, ox0, oy0):
    fill(x0 + 4, y0, 4, 4, COURO); fill(x0 + 8, y0, 4, 4, PELE)
    for k in range(4):
        fill(x0 + k * 4, y0 + 4, 4, 8, COURO)
        fill(x0 + k * 4, y0 + 12, 4, 2, (34, 30, 40), 4)      # bracelete
        px[x0 + k * 4 + 1, y0 + 12] = var(ROXO, 6)
        fill(x0 + k * 4, y0 + 14, 4, 2, PELE, 5)              # mão
        px[x0 + k * 4, y0 + 4] = var(ROXO, 6)
    fill(ox0 + 4, oy0, 4, 4, COURO_S, 4)                      # ombreira (camada de cima)
    for k in range(4): fill(ox0 + k * 4, oy0 + 4, 4, 2, COURO_S, 4)
braco(40, 16, 40, 32)
braco(32, 48, 48, 48)
# ---------------- pernas: calça escura e bota
def perna(x0, y0):
    fill(x0 + 4, y0, 4, 4, CALCA); fill(x0 + 8, y0, 4, 4, BOTA)
    for k in range(4):
        fill(x0 + k * 4, y0 + 4, 4, 7, CALCA, 6)
        fill(x0 + k * 4, y0 + 11, 4, 5, BOTA, 6)
        px[x0 + k * 4 + 1, y0 + 11] = var(OURO, 4) if k == 1 else px[x0 + k * 4 + 1, y0 + 11]
perna(0, 16); perna(16, 48)
sk.save(sys.argv[1])

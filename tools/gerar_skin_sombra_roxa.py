#!/usr/bin/env python3
"""Skin "Sombra Roxa" (64x64, braços largos), feita a partir da referência do jogador:
cabelo preto, olhos roxos brilhando, máscara preta com linha roxa, casaco preto com faixas
roxas, losangos roxos nos braços, emblema de fogo roxo nas costas e botas com sola roxa.
Uso: python3 tools/gerar_skin_sombra_roxa.py arte/skins/sombra_roxa.png
"""
import random
import sys
from PIL import Image

random.seed(42)
sk = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
px = sk.load()

# paleta da referência
PRETO_ROXO = (22, 12, 34)
NEON = (122, 26, 214)
NEON_C = (168, 85, 255)
BRILHO = (215, 175, 255)
PRETO = (20, 20, 22)
CINZA = (36, 33, 44)
PELE = (243, 218, 196)
PELE_S = (214, 182, 160)
BRANCO = (250, 246, 255)


def ruido():
    """Preto com textura: mistura de preto, preto-arroxeado e cinza escuro."""
    r = random.random()
    base = PRETO if r < 0.5 else (PRETO_ROXO if r < 0.8 else CINZA)
    d = random.randint(-4, 4)
    return tuple(max(0, min(255, v + d)) for v in base) + (255,)


def set_(x, y, c):
    px[x, y] = c + (255,) if len(c) == 3 else c


def preto(x, y, w, h):
    for i in range(x, x + w):
        for j in range(y, y + h):
            px[i, j] = ruido()


def caixa(u, v, w, h, d):
    """Retângulos das faces de uma caixa no layout da skin."""
    return {"topo": (u + d, v, w, d), "base": (u + d + w, v, d and w, d),
            "dir": (u, v + d, d, h), "frente": (u + d, v + d, w, h),
            "esq": (u + d + w, v + d, d, h), "costas": (u + d + w + d, v + d, w, h)}


# ============================== CABEÇA
H = caixa(0, 0, 8, 8, 8)
for f, (x, y, w, h) in H.items():
    preto(x, y, w, h)
fx, fy = H["frente"][:2]
# rosto: cada bloco com a cor tirada da referência do jogador (contados um a um).
# Olhos em 2x2: lilás e roxo escuro em cima; BRANCO por fora e roxo forte por dentro embaixo.
CAB = [(0, 0, 0), (8, 8, 8), (8, 8, 8), (16, 16, 16), (16, 16, 16), (24, 24, 24), (34, 33, 36), (44, 43, 46)]
h = None
ROSTO = [
    [h, h, h, h, h, h, h, h],
    [h, h, h, h, h, h, h, h],
    [h, h, h, h, h, h, h, h],
    [h, h, (132, 95, 95), (25, 24, 24), h, (132, 95, 95), h, h],                                   # pele entre as mechas
    [(26, 12, 40), (151, 120, 174), (37, 6, 68), (18, 17, 19), (6, 5, 5), (39, 4, 80), (140, 106, 165), (32, 12, 51)],
    [(87, 54, 94), (243, 234, 235), (148, 45, 221), (127, 90, 95), (110, 77, 83), (133, 39, 204), (241, 234, 237), (62, 36, 80)],
    [(120, 87, 91), (158, 117, 115), (169, 124, 126), (175, 132, 126), (162, 120, 115), (164, 122, 119), (156, 118, 116), (142, 105, 101)],
    [(29, 14, 47), (3, 3, 3), (6, 5, 5), (4, 4, 3), (3, 3, 3), (4, 4, 3), (3, 3, 2), (29, 14, 47)],
]
for j, linha in enumerate(ROSTO):
    for i, cor in enumerate(linha):
        set_(fx + i, fy + j, random.choice(CAB) if cor is None else cor)
# laterais: cabelo, pele perto do rosto na altura da bochecha, máscara embaixo
for lado in ("dir", "esq"):
    x, y, w, h = H[lado]
    perto = x + w - 1 if lado == "dir" else x
    for i in range(w):
        for j in range(8):
            set_(x + i, y + j, random.choice(CAB))
        set_(x + i, y + 7, (4, 3, 3))
    set_(perto, y + 6, (117, 84, 87))
    set_(x + (2 if lado == "dir" else 5), y + 7, (29, 14, 46))
# nuca: faixa roxa da máscara amarrada atrás
x, y, w, h = H["costas"]
for i in range(1, 7):
    set_(x + i, y + 6, NEON)                                        # faixa roxa amarrada na nuca
set_(x + 3, y + 7, NEON); set_(x + 4, y + 7, NEON_C)               # nó da faixa

def cabelo():
    """Preto do cabelo da referência (mais escuro que o do casaco)."""
    return random.choice(CAB) + (255,)


# camada de cima da cabeça: mechas do cabelo saindo da frente e dos lados
C = caixa(32, 0, 8, 8, 8)
cx, cy = C["frente"][:2]
for i, comp in enumerate([2, 3, 2, 1, 1, 2, 3, 2]):                  # franja irregular
    for j in range(comp):
        px[cx + i, cy + j] = cabelo()
for lado in ("dir", "esq"):
    x, y, w, h = C[lado]
    for i in range(w):
        for j in range(random.choice([2, 3, 3, 4])):
            px[x + i, y + j] = cabelo()
x, y, w, h = C["topo"]
for i in range(w):
    for j in range(h):
        if random.random() < 0.35:
            px[x + i, y + j] = cabelo()
# máscara saindo um pouco do rosto (volume), só na parte de baixo
for i in range(1, 7):
    px[cx + i, cy + 7] = random.choice([(3, 3, 3), (6, 5, 5), (4, 4, 3)]) + (255,)   # máscara preta

# ============================== CORPO
B = caixa(16, 16, 8, 12, 4)
for f, (x, y, w, h) in B.items():
    preto(x, y, w, h)
x, y, w, h = B["frente"]
for j in range(1, 12):                                               # duas faixas do casaco
    set_(x + 2, y + j, NEON); set_(x + 5, y + j, NEON)
set_(x + 2, y + 1, NEON_C); set_(x + 5, y + 1, NEON_C)
for i in range(8):                                                   # gola
    set_(x + i, y, PRETO_ROXO)
# costas: emblema de fogo roxo
x, y, w, h = B["costas"]
CHAMA = ["....C...",
         "...CC...",
         "..CNC.C.",
         "..CN.CC.",
         ".CN..NC.",
         ".CN.CCNC",
         ".C.CN.CC",
         ".CN.CC.C",
         "..CN..C.",
         "...CCCC."]
for j, linha in enumerate(CHAMA):
    for i, ch in enumerate(linha):
        if ch == "C": set_(x + i, y + 1 + j, NEON_C)
        if ch == "N": set_(x + i, y + 1 + j, NEON)
for lado in ("dir", "esq"):                                          # lateral do casaco
    x, y, w, h = B[lado]
    for j in range(2, 12, 3):
        set_(x + 1, y + j, NEON)

# ============================== BRAÇOS (largos)
def braco(u, v, ou, ov):
    A = caixa(u, v, 4, 12, 4)
    for f, (x, y, w, h) in A.items():
        preto(x, y, w, h)
    for f in ("frente", "costas", "dir", "esq"):
        x, y, w, h = A[f]
        # losangos quadriculados em roxo
        padrao = [".NN.", "N..N", ".NN.", "N..N", ".CC.", "N..N"]
        for j, linha in enumerate(padrao):
            for i, ch in enumerate(linha):
                if ch == "N": set_(x + i, y + 2 + j, NEON)
                if ch == "C": set_(x + i, y + 2 + j, NEON_C)
        for i in range(4):
            set_(x + i, y + 9, NEON)                                # punho roxo
            set_(x + i, y + 10, PELE); set_(x + i, y + 11, PELE_S)  # mão
    x, y, w, h = A["base"]
    for i in range(4):
        for j in range(4): set_(x + i, y + j, PELE_S)
    x, y, w, h = A["topo"]
    for i in range(4): set_(x + i, y, NEON)                         # risco roxo no ombro
    # camada de cima: ombro com volume
    O = caixa(ou, ov, 4, 12, 4)
    for f in ("frente", "costas", "dir", "esq"):
        x, y, w, h = O[f]
        for i in range(4):
            px[x + i, y] = ruido(); px[x + i, y + 1] = ruido()
        px[x + 1, y + 1] = NEON + (255,)


braco(40, 16, 40, 32)
braco(32, 48, 48, 48)

# ============================== PERNAS
def perna(u, v):
    L = caixa(u, v, 4, 12, 4)
    for f, (x, y, w, h) in L.items():
        preto(x, y, w, h)
    for f in ("frente", "costas", "dir", "esq"):
        x, y, w, h = L[f]
        set_(x, y + 5, NEON); set_(x + 3, y + 5, NEON)              # "V" roxo no joelho
        set_(x + 1, y + 6, NEON); set_(x + 2, y + 6, NEON)
        set_(x + 1, y + 9, NEON); set_(x + 2, y + 9, NEON_C)        # detalhe da bota
        for i in range(4):
            set_(x + i, y + 11, NEON)                               # sola roxa
    x, y, w, h = L["base"]
    for i in range(4):
        for j in range(4): set_(x + i, y + j, PRETO_ROXO)


perna(0, 16)
perna(16, 48)
sk.save(sys.argv[1] if len(sys.argv) > 1 else "sombra_roxa.png")

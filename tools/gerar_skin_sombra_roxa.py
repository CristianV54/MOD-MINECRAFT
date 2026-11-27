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
# rosto: traçado bloco a bloco sobre a referência do jogador (grade real de ~27 px por bloco).
# A referência tem 9 colunas e 9 linhas; aqui ficam as 8 colunas do rosto (bochecha a bochecha)
# e as 8 linhas de baixo, com os dois cantos roxos da máscara.
CAB = [(0, 0, 0), (8, 8, 8), (8, 8, 8), (16, 16, 16), (16, 16, 16), (24, 24, 24), (34, 33, 36), (44, 43, 46)]
ROSTO = [
    [(17, 17, 16), (4, 4, 4), (14, 13, 13), (10, 10, 10), (2, 2, 2), (13, 12, 12), (2, 2, 2), (10, 10, 10)],
    [(14, 14, 13), (19, 18, 17), (7, 7, 7), (3, 2, 2), (10, 10, 10), (15, 15, 15), (11, 10, 10), (4, 4, 3)],
    [(27, 27, 26), (9, 8, 8), (37, 27, 33), (11, 11, 11), (15, 15, 15), (24, 24, 25), (17, 17, 17), (14, 14, 14)],
    [(8, 8, 7), (9, 9, 9), (129, 92, 93), (25, 24, 24), (14, 14, 13), (7, 6, 6), (62, 43, 48), (10, 9, 9)],
    [(25, 12, 38), (137, 106, 163), (33, 5, 64), (19, 18, 19), (6, 6, 5), (33, 4, 69), (138, 103, 162), (12, 11, 13)],
    [(85, 54, 93), (244, 235, 236), (132, 34, 211), (128, 89, 96), (110, 77, 83), (115, 33, 187), (240, 234, 236), (10, 8, 9)],
    [(170, 126, 121), (158, 117, 115), (169, 123, 126), (175, 132, 126), (163, 120, 115), (163, 121, 119), (157, 118, 116), (134, 97, 95)],
    [(28, 12, 45), (7, 6, 5), (4, 4, 3), (4, 3, 3), (4, 4, 4), (4, 4, 3), (3, 2, 2), (28, 12, 45)],
]
ROSTO[4][7] = ROSTO[4][0]    # brilho roxo na bochecha direita, igual ao da esquerda
ROSTO[5][7] = ROSTO[5][0]
for j, linha in enumerate(ROSTO):
    for i, cor in enumerate(linha):
        set_(fx + i, fy + j, cor)
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
# (a frente da camada de cima fica vazia: o rosto traçado aparece exatamente como na referência)
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

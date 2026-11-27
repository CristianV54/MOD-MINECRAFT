#!/usr/bin/env python3
"""Skin "Sombra Roxa" traçada cubo a cubo sobre a referência do jogador.

Cada face vem de uma vista da imagem de referência (frente, costas, lado direito e lado esquerdo):
a cor de cada bloco é a mediana do quadradinho correspondente, numa grade própria por parte
(a arte tem a cabeça maior que o corpo, então cada parte tem a sua caixa). A frente da cabeça
vem do close dos olhos (rosto_tracado.json), que tem mais detalhe.

Uso: python3 tools/gerar_skin_sombra_roxa_tracada.py <referencia.webp> <rosto_tracado.json> <saida.png>
"""
import json
import random
import sys

import numpy as np
from PIL import Image

random.seed(3)
ref = np.array(Image.open(sys.argv[1]).convert("RGB")).astype(int)
OX, OY = 480, 60          # canto do painel com as 4 vistas
CAIXAS = {                # (x0, y0, x1, y1, colunas, linhas) no painel das vistas
    "f_corpo": (60, 122, 178, 282, 8, 12), "f_braco_d": (18, 122, 60, 282, 4, 12), "f_braco_e": (178, 122, 218, 282, 4, 12),
    "f_perna_d": (60, 282, 119, 442, 4, 12), "f_perna_e": (119, 282, 178, 442, 4, 12),
    "c_cabeca": (277, 12, 387, 122, 8, 8), "c_corpo": (277, 122, 387, 282, 8, 12),
    "c_braco_e": (233, 122, 277, 282, 4, 12), "c_braco_d": (387, 122, 430, 282, 4, 12),
    "c_perna_e": (277, 282, 332, 442, 4, 12), "c_perna_d": (332, 282, 387, 442, 4, 12),
    "ld_cabeca": (445, 12, 556, 122, 8, 8), "ld_braco": (473, 122, 530, 282, 4, 12), "ld_perna": (473, 282, 530, 442, 4, 12),
    "le_cabeca": (612, 12, 723, 122, 8, 8), "le_braco": (640, 122, 697, 282, 4, 12), "le_perna": (640, 282, 697, 442, 4, 12),
}


def cor_do_bloco(p):
    """Cor de um quadradinho: detalhes finos (faixas roxas, pele) ganham do preto em volta.
    Se pelo menos 30% do quadradinho for roxo, o bloco é roxo; o mesmo para a pele."""
    r, g, b = p[:, 0], p[:, 1], p[:, 2]
    roxo = (b > g + 35) & (b > 80)
    pele = (r > 140) & (r > b) & (g > 100)
    for m in (roxo, pele):
        if m.mean() >= 0.35:
            return tuple(int(v) for v in np.median(p[m], axis=0))
    c = np.median(p, axis=0)
    if c.max() < 70:                       # bloco preto: realça a textura de cinza da referência
        c = np.minimum(c * 1.7, 72)
    return tuple(int(v) for v in c)


# Desenhos feitos à mão, bloco a bloco, a partir do mapa de roxo da referência
# (C = roxo vivo, N = roxo escuro, . = mantém o preto traçado).
VIVO, MEDIO, ESCURO = (175, 95, 255), (140, 45, 230), (78, 24, 128)
DESENHOS = {
    "c_corpo": ["........",      # chama em contorno, como na referência: ponta à direita, pontinha à
                ".....C..",      # esquerda, lados descendo, espiral por dentro e base fechada
                "....CN..",
                "...C.C..",
                "..CN.C..",
                "..C.C.C.",
                ".C.CN.C.",
                ".C.C.NC.",
                "..C.CC..",
                "..NC..C.",
                "...CCCN.",
                "........"],
    "f_corpo": ["........",      # faixas do casaco: começam abaixo da gola, escuras em cima e vivas embaixo
                "........",
                "........",
                "..N..N..",
                "..N..N..",
                "..N..N..",
                "..N..N..",
                "..N..N..",
                "N.C..C.N",
                "N.C..C.N",
                "..C..C..",
                "..N..N.."],
    "f_perna_d": [".N..",        # perna direita: a faixa continua e se abre para fora
                  "N...",
                  "....", "....", "....", "....", "....", "....",
                  ".CN.",          # blocos roxos acima da sola
                  "....",
                  "NCN.",          # sola
                  "...."],
    "f_perna_e": ["..N.",
                  "...N",
                  "....", "....", "....", "....", "....", "....",
                  ".NC.",
                  "....",
                  ".NCN",
                  "...."],
}


def aplicar_desenho(nome, g):
    eh_roxo = lambda c: c[2] > c[1] + 25 and c[2] > 55
    for j, linha in enumerate(DESENHOS[nome]):
        for i, ch in enumerate(linha):
            eh_pele = g[j][i][0] > 140 and g[j][i][0] > g[j][i][2]
            if ch == "." and (eh_roxo(g[j][i]) or eh_pele):
                g[j][i] = random.choice([(14, 12, 18), (20, 18, 24), (10, 9, 12)])   # só o desenho fica roxo
            if ch == "C": g[j][i] = VIVO if (i + j) % 2 else MEDIO
            elif ch == "N": g[j][i] = ESCURO
    return g


def encaixe(nome):
    """Acha a grade que melhor encaixa nos cubos da referência: testa deslocamentos e tamanhos
    e fica com a que deixa cada quadradinho com uma cor só (menor variação dentro dos blocos)."""
    x0, y0, x1, y1, nc, nl = CAIXAS[nome]
    melhor = None
    for sx in (0.94, 0.97, 1.0, 1.03, 1.06):
        for sy in (0.94, 0.97, 1.0, 1.03, 1.06):
            cw, ch = (x1 - x0) / nc * sx, (y1 - y0) / nl * sy
            for dx in range(-6, 7, 2):
                for dy in range(-6, 7, 2):
                    bx = OX + x0 + dx + (x1 - x0 - cw * nc) / 2
                    by = OY + y0 + dy + (y1 - y0 - ch * nl) / 2
                    custo = 0.0
                    for j in range(nl):
                        for i in range(nc):
                            a0, a1 = int(bx + (i + 0.2) * cw), int(bx + (i + 0.8) * cw)
                            b0, b1 = int(by + (j + 0.2) * ch), int(by + (j + 0.8) * ch)
                            bloco = ref[b0:b1, a0:a1].reshape(-1, 3)
                            custo += bloco.var(axis=0).sum()
                    if melhor is None or custo < melhor[0]:
                        melhor = (custo, bx, by, cw, ch)
    return melhor[1:], (nc, nl)


_cache = {}


def tracar(nome):
    if nome in _cache:
        return [l[:] for l in _cache[nome]]
    (bx, by, cw, ch), (nc, nl) = encaixe(nome)
    g = []
    for j in range(nl):
        linha = []
        for i in range(nc):
            a0, a1 = int(bx + (i + 0.15) * cw), int(bx + (i + 0.85) * cw)
            b0, b1 = int(by + (j + 0.15) * ch), int(by + (j + 0.85) * ch)
            linha.append(cor_do_bloco(ref[b0:b1, a0:a1].reshape(-1, 3)))
        g.append(linha)
    _cache[nome] = g
    return [l[:] for l in g]


sk = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
px = sk.load()


def por(g, x, y, espelhar=False):
    for j, linha in enumerate(g):
        for i, c in enumerate(linha[::-1] if espelhar else linha):
            px[x + i, y + j] = c + (255,)


def liso(x, y, w, h, cores):
    for i in range(w):
        for j in range(h):
            px[x + i, y + j] = random.choice(cores) + (255,)


CAB = [(0, 0, 0), (8, 8, 8), (14, 14, 13), (16, 16, 16), (24, 24, 24), (26, 12, 40), (20, 10, 32)]
ROUPA = [(6, 5, 8), (10, 9, 12), (14, 12, 18)]
PELE = [(214, 176, 150), (226, 190, 165)]

# ---------------- cabeça (base)
rosto = json.load(open(sys.argv[2]))[1:]                 # 8 linhas de baixo do close
rosto = [list(map(tuple, l)) for l in rosto]
rosto[7][0] = (28, 12, 45); rosto[4][7] = rosto[4][0]; rosto[5][7] = rosto[5][0]
liso(8, 0, 8, 8, CAB); liso(16, 0, 8, 8, ROUPA)          # topo (cabelo) e base
por(tracar("ld_cabeca"), 0, 8)                           # lado direito
por(rosto, 8, 8)                                          # frente
por(tracar("le_cabeca"), 16, 8)                          # lado esquerdo
por(tracar("c_cabeca"), 24, 8)                           # nuca
# ---------------- corpo
liso(20, 16, 8, 4, ROUPA); liso(28, 16, 8, 4, ROUPA)
por(aplicar_desenho("f_corpo", tracar("f_corpo")), 20, 20)
por(aplicar_desenho("c_corpo", tracar("c_corpo")), 32, 20)
lado_corpo = [[tracar("f_corpo")[j][0]] * 0 + [random.choice(ROUPA)] * 4 for j in range(12)]
por(lado_corpo, 16, 20); por(lado_corpo, 28, 20)
# ---------------- braço direito (40,16) e esquerdo (32,48)
for (u, v, fr, co, fora, dentro_de) in [(40, 16, "f_braco_d", "c_braco_d", "ld_braco", "le_braco"),
                                         (32, 48, "f_braco_e", "c_braco_e", "le_braco", "ld_braco")]:
    liso(u + 4, v, 4, 4, ROUPA); liso(u + 8, v, 4, 4, PELE)              # topo e mão embaixo
    direito = (u == 40)
    por(tracar(fora) if direito else tracar(dentro_de), u, v + 4, espelhar=not direito)       # face da direita
    por(tracar(fr), u + 4, v + 4)                                                              # frente
    por(tracar(dentro_de) if direito else tracar(fora), u + 8, v + 4, espelhar=direito)       # face da esquerda
    por(tracar(co), u + 12, v + 4)                                                             # costas
# ---------------- perna direita (0,16) e esquerda (16,48)
for (u, v, fr, co, fora, dentro_de) in [(0, 16, "f_perna_d", "c_perna_d", "ld_perna", "le_perna"),
                                         (16, 48, "f_perna_e", "c_perna_e", "le_perna", "ld_perna")]:
    liso(u + 4, v, 4, 4, ROUPA); liso(u + 8, v, 4, 4, ROUPA)
    direita = (u == 0)
    por(tracar(fora) if direita else tracar(dentro_de), u, v + 4, espelhar=not direita)
    por(aplicar_desenho(fr, tracar(fr)), u + 4, v + 4)
    por(tracar(dentro_de) if direita else tracar(fora), u + 8, v + 4, espelhar=direita)
    por(tracar(co), u + 12, v + 4)
# ---------------- camada de cima: cabelo com volume (capuz de cabelo), copiando a camada de baixo
for (bx, by, ox, oy, linhas) in [(8, 0, 40, 0, 8), (0, 8, 32, 8, 5), (8, 8, 40, 8, 4), (16, 8, 48, 8, 5), (24, 8, 56, 8, 5)]:
    for i in range(8):
        for j in range(linhas):
            px[ox + i, oy + j] = px[bx + i, by + j]
sk.save(sys.argv[3])

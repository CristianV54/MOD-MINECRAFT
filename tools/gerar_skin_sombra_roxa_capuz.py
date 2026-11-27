#!/usr/bin/env python3
"""Variante "Sombra Roxa com capuz de cabelo", como na referência do jogador: a camada de cima
da cabeça é o próprio cabelo (blocos pretos e cinza), cobrindo topo, lados e nuca, com a franja
na frente e mechas descendo nas bordas até a altura dos olhos. Pele, olhos, máscara e a faixa
roxa da nuca ficam à mostra.
Uso: python3 tools/gerar_skin_sombra_roxa_capuz.py arte/skins/sombra_roxa.png arte/skins/sombra_roxa_capuz.png
"""
import random
import sys
from PIL import Image

random.seed(11)
sk = Image.open(sys.argv[1]).convert("RGBA")
px = sk.load()
# cores do cabelo tiradas da referência (preto com alguns blocos cinza-escuro)
CAB = [(0, 0, 0), (8, 8, 8), (8, 8, 8), (14, 14, 13), (16, 16, 16), (24, 24, 24), (27, 27, 26), (37, 36, 39),
       (26, 12, 40), (20, 10, 32), (34, 16, 52)]   # blocos roxo-escuros misturados no cabelo


def cabelo():
    return random.choice(CAB) + (255,)


def limpa(x0, y0, w, h):
    for x in range(x0, x0 + w):
        for y in range(y0, y0 + h):
            px[x, y] = (0, 0, 0, 0)


# camada de cima da cabeça: topo (40,0) | lado direito (32,8) | frente (40,8) | lado esquerdo (48,8) | nuca (56,8)
limpa(32, 0, 32, 16)
for x in range(40, 48):
    for y in range(0, 8):
        px[x, y] = cabelo()                                  # topo inteiro
# frente: franja nas 4 linhas de cima + mechas nas bordas até a altura dos olhos
for x in range(40, 48):
    for y in range(8, 12):
        px[x, y] = cabelo()
for y in range(12, 14):
    px[40, y] = cabelo(); px[47, y] = cabelo()
# lados: cabelo até a altura dos olhos; embaixo fica a pele da bochecha e a máscara
for x0 in (32, 48):
    for x in range(x0, x0 + 8):
        for y in range(8, 14):
            px[x, y] = cabelo()
    # mecha mais comprida atrás da orelha (lado oposto ao rosto)
    atras = x0 if x0 == 32 else x0 + 7
    px[atras, 14] = cabelo()
# nuca: cabelo até logo acima da faixa roxa amarrada
for x in range(56, 64):
    for y in range(8, 14):
        px[x, y] = cabelo()
sk.save(sys.argv[2])

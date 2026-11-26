#!/usr/bin/env python3
"""Gera a arte do SealCraft: o logo da tela inicial e o ícone quadrado.

Uso:  python3 tools/gerar_arte.py
Saída:
  pack/config/openloader/resources/sealcraft_visual/assets/aquamirae/textures/gui/title/logo.png
      Logo "SEALCRAFT" que substitui o logo do Aquamirae embaixo do "MINECRAFT" na tela inicial
      (o Aquamirae desenha o próprio logo nessa posição; trocamos só a imagem).
  arte/logo_sealcraft.png  (1000x240, o mesmo logo, para usar em divulgação)
  arte/icone_sealcraft.png (400x400, ícone do perfil no CurseForge e do projeto publicado)
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DESTINO_LOGO = os.path.join(RAIZ, "pack", "config", "openloader", "resources", "sealcraft_visual",
                            "assets", "aquamirae", "textures", "gui", "title", "logo.png")
PASTA_ARTE = os.path.join(RAIZ, "arte")

# Letras em blocos, 5 colunas x 7 linhas, no estilo do logo do Minecraft.
GLIFOS = {
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "R": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "#...#"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
}

# Paleta: ametista (o Fragmento do Selo) com sombra quase preta.
CLARO = (226, 205, 255)
MEIO = (150, 92, 230)
ESCURO = (72, 30, 140)
LATERAL = (46, 18, 92)
CONTORNO = (14, 8, 22)


def gradiente_vertical(tamanho, cores):
    """Imagem RGB com gradiente de cima para baixo passando pelas cores dadas."""
    w, h = tamanho
    img = Image.new("RGB", tamanho)
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1) * (len(cores) - 1)
        i = min(int(t), len(cores) - 2)
        f = t - i
        c = tuple(int(cores[i][k] + (cores[i + 1][k] - cores[i][k]) * f) for k in range(3))
        for x in range(w):
            px[x, y] = c
    return img


def textura_cristal(img, semente=7):
    """Riscos claros diagonais, como faces de cristal, por cima do gradiente."""
    rnd = random.Random(semente)
    camada = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    w, h = img.size
    for _ in range(int(w * h / 2500)):
        x, y = rnd.randrange(w), rnd.randrange(h)
        comp = rnd.randrange(10, 60)
        a = rnd.randrange(18, 60)
        d.line([(x, y), (x + comp, y - comp * 0.55)], fill=(255, 255, 255, a), width=rnd.choice([1, 2, 3]))
    camada = camada.filter(ImageFilter.GaussianBlur(1.2))
    return Image.alpha_composite(img.convert("RGBA"), camada)


def logo(largura=1000, altura=240, texto="SEALCRAFT"):
    colunas = len(texto) * 6 - 1
    cel_w = int((largura - 70) / colunas)
    cel_h = int((altura - 70) / 7)
    texto_w, texto_h = colunas * cel_w, 7 * cel_h
    ox, oy = (largura - texto_w) // 2 - 8, (altura - texto_h) // 2 - 10

    frente = Image.new("L", (largura, altura), 0)
    topo = Image.new("L", (largura, altura), 0)
    df, dt = ImageDraw.Draw(frente), ImageDraw.Draw(topo)
    for i, letra in enumerate(texto):
        for r, linha in enumerate(GLIFOS[letra]):
            for c, v in enumerate(linha):
                if v != "#":
                    continue
                x0 = ox + (i * 6 + c) * cel_w
                y0 = oy + r * cel_h
                df.rectangle([x0, y0, x0 + cel_w - 1, y0 + cel_h - 1], fill=255)
                # brilho no topo de cada bloco que não tem bloco em cima
                if r == 0 or GLIFOS[letra][r - 1][c] != "#":
                    dt.rectangle([x0, y0, x0 + cel_w - 1, y0 + max(3, cel_h // 6)], fill=255)

    profundidade = 14
    lateral = Image.new("L", (largura, altura), 0)
    for d in range(1, profundidade + 1):
        lateral = ImageChops.lighter(lateral, ImageChops.offset(frente, d, d))
    silhueta = ImageChops.lighter(frente, lateral)
    contorno = silhueta.filter(ImageFilter.MaxFilter(17))

    img = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    img.paste(Image.new("RGBA", img.size, CONTORNO + (255,)), (0, 0), contorno)
    lado = gradiente_vertical(img.size, [ESCURO, LATERAL]).convert("RGBA")
    img.paste(lado, (0, 0), lateral)
    face = textura_cristal(gradiente_vertical(img.size, [CLARO, MEIO, ESCURO]))
    img.paste(face, (0, 0), frente)
    img.paste(Image.new("RGBA", img.size, (245, 236, 255, 255)), (0, 0), topo.point(lambda v: int(v * 0.75)))
    return img


def icone(tamanho=400):
    """Cristal roxo partido atravessado por uma espada, sobre fundo de obsidiana."""
    s = tamanho / 180
    img = Image.new("RGBA", (tamanho, tamanho), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, tamanho - 1, tamanho - 1], radius=int(28 * s), fill=(25, 21, 36, 255))
    d.ellipse([12 * s, 12 * s, 168 * s, 168 * s], outline=(60, 51, 82, 255), width=max(2, int(2 * s)))
    for a in range(0, 360, 12):
        r1, r2 = 70 * s, 74 * s
        x, y = 90 * s + math.cos(math.radians(a)) * r1, 90 * s + math.sin(math.radians(a)) * r1
        x2, y2 = 90 * s + math.cos(math.radians(a)) * r2, 90 * s + math.sin(math.radians(a)) * r2
        d.line([(x, y), (x2, y2)], fill=(60, 51, 82, 255), width=max(1, int(s)))

    def poligono(pontos, cor_ou_grad):
        mascara = Image.new("L", img.size, 0)
        ImageDraw.Draw(mascara).polygon([(x * s, y * s) for x, y in pontos], fill=255)
        if isinstance(cor_ou_grad, tuple):
            img.paste(Image.new("RGBA", img.size, cor_ou_grad + (255,)), (0, 0), mascara)
        else:
            img.paste(cor_ou_grad, (0, 0), mascara)

    grad = gradiente_vertical(img.size, [(201, 166, 255), (139, 79, 224), (75, 35, 144)]).convert("RGBA")
    poligono([(90, 26), (120, 74), (96, 92), (84, 70)], grad)
    poligono([(90, 26), (84, 70), (62, 80)], (106, 53, 189))
    poligono([(62, 88), (86, 80), (98, 100), (90, 154)], grad)
    poligono([(104, 98), (124, 82), (118, 120), (92, 154)], (90, 42, 168))
    d = ImageDraw.Draw(img)
    d.line([(84 * s, 70 * s), (96 * s, 92 * s), (86 * s, 80 * s), (98 * s, 100 * s)],
           fill=(241, 236, 250, 255), width=max(2, int(1.5 * s)), joint="curve")
    # espada (lâmina vertical, guarda e cabo)
    d.line([(90 * s, 14 * s), (90 * s, 150 * s)], fill=(214, 128, 70, 255), width=max(3, int(3 * s)))
    d.rectangle([76 * s, 148 * s, 104 * s, 153 * s], fill=(180, 90, 31, 255))
    d.rectangle([87.5 * s, 153 * s, 92.5 * s, 166 * s], fill=(120, 60, 24, 255))
    return img


def main():
    os.makedirs(os.path.dirname(DESTINO_LOGO), exist_ok=True)
    os.makedirs(PASTA_ARTE, exist_ok=True)
    lg = logo()
    lg.save(DESTINO_LOGO)
    lg.save(os.path.join(PASTA_ARTE, "logo_sealcraft.png"))
    icone().save(os.path.join(PASTA_ARTE, "icone_sealcraft.png"))
    mcmeta = os.path.join(os.path.dirname(DESTINO_LOGO).split("assets")[0], "pack.mcmeta")
    with open(mcmeta, "w", encoding="utf-8") as f:
        f.write('{\n  "pack": {\n    "pack_format": 15,\n    "description": "SealCraft: tela inicial e textos do menu"\n  }\n}\n')
    print("logo:", DESTINO_LOGO)
    print("arte:", PASTA_ARTE)


if __name__ == "__main__":
    main()

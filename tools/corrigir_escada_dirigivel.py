#!/usr/bin/env python3
"""Corrige a escada do Small Blimp (When Dungeons Arise).

A escada original tem 48 blocos pendurados no ar, sem nada atrás. No Minecraft,
uma escada sem parede só sobe segurando o pulo, e quem anda pra frente nela não sobe.
Esta versão põe um tronco de carvalho escuro na coluna ao lado (que no original só
tinha os dois blocos de encaixe nas pontas) e vira a escada para ele. O tamanho da peça
não muda, então o dirigível continua gerando igual.

Uso: python3 tools/corrigir_escada_dirigivel.py <jar do When Dungeons Arise>
"""
import gzip
import io
import os
import struct
import sys
import zipfile

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CAMINHO = "data/dungeons_arise/structures/small_blimp/small_blimp_ladders_0.nbt"
DESTINO = os.path.join(RAIZ, "pack", "config", "openloader", "data", "terras_partidas", CAMINHO)


# ---- NBT mínimo (só os tipos usados em estruturas: int, string, list, compound)
def ler(dados):
    f = io.BytesIO(dados)

    def r(n): return f.read(n)
    def s(): return r(struct.unpack(">H", r(2))[0]).decode()

    def payload(t):
        if t == 1: return ("b", struct.unpack(">b", r(1))[0])
        if t == 3: return struct.unpack(">i", r(4))[0]
        if t == 6: return ("d", struct.unpack(">d", r(8))[0])
        if t == 8: return s()
        if t == 9:
            et = r(1)[0]
            return [payload(et) for _ in range(struct.unpack(">i", r(4))[0])]
        if t == 10:
            o = {}
            while (tt := r(1)[0]) != 0:
                k = s()
                o[k] = payload(tt)
            return o
        raise ValueError(f"tipo NBT {t} não suportado")

    t = r(1)[0]
    s()
    return payload(t)


def escrever(obj):
    out = io.BytesIO()

    def tipo(v):
        if isinstance(v, tuple): return {"b": 1, "d": 6}[v[0]]
        if isinstance(v, int): return 3
        if isinstance(v, str): return 8
        if isinstance(v, list): return 9
        if isinstance(v, dict): return 10

    def st(x):
        b = x.encode()
        out.write(struct.pack(">H", len(b)) + b)

    def payload(v):
        t = tipo(v)
        if t == 1: out.write(struct.pack(">b", v[1]))
        elif t == 6: out.write(struct.pack(">d", v[1]))
        elif t == 3: out.write(struct.pack(">i", v))
        elif t == 8: st(v)
        elif t == 9:
            out.write(bytes([tipo(v[0]) if v else 0]) + struct.pack(">i", len(v)))
            for e in v: payload(e)
        elif t == 10:
            for k, e in v.items():
                out.write(bytes([tipo(e)]))
                st(k)
                payload(e)
            out.write(b"\x00")

    out.write(b"\x0a")
    st("")
    payload(obj)
    return gzip.compress(out.getvalue())


def main(jar):
    n = ler(gzip.decompress(zipfile.ZipFile(jar).read(CAMINHO)))
    assert n["size"] == [2, 48, 1], n["size"]
    pal = n["palette"]
    escada = next(i for i, b in enumerate(pal) if b["Name"] == "minecraft:ladder")
    pal[escada]["Properties"]["facing"] = "west"   # apoiada no bloco a leste (x = 1)
    pal.append({"Name": "minecraft:stripped_dark_oak_log", "Properties": {"axis": "y"}})
    tronco = len(pal) - 1
    ocupados = {tuple(b["pos"]) for b in n["blocks"]}
    for y in range(48):
        if (1, y, 0) not in ocupados:
            n["blocks"].append({"pos": [1, y, 0], "state": tronco})
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    with open(DESTINO, "wb") as f:
        f.write(escrever(n))
    print("escrito:", DESTINO)


if __name__ == "__main__":
    main(sys.argv[1])

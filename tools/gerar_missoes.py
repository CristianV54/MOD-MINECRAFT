#!/usr/bin/env python3
"""Gera os arquivos de missões do FTB Quests (formato SNBT, versão 13 / MC 1.20.1).

Uso:  python3 tools/gerar_missoes.py
Saída: pack/config/ftbquests/quests/

Os IDs são gerados a partir de uma chave fixa, então rodar de novo não quebra o
progresso de quem já está jogando. ATENÇÃO: se alguém editar as missões dentro do
jogo, essas mudanças são sobrescritas na próxima vez que este script rodar.
"""
import hashlib
import json
import os

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pack", "config", "ftbquests", "quests")


# ---------------------------------------------------------------- utilidades

def qid(chave):
    """ID hexadecimal de 16 dígitos, estável para a mesma chave.

    O FTB Quests só aceita IDs positivos (primeiro dígito de 0 a 7); IDs fora disso
    são trocados por aleatórios ao carregar, o que apagaria o progresso dos jogadores.
    """
    n = int(hashlib.sha1(chave.encode()).hexdigest()[:16], 16) & 0x7FFF_FFFF_FFFF_FFFF
    return f"{max(n, 2):016X}"


def snbt(valor, nivel=0):
    tab = "\t" * nivel
    if isinstance(valor, dict):
        if not valor:
            return "{ }"
        linhas = [f"{tab}\t{k}: {snbt(v, nivel + 1)}" for k, v in valor.items()]
        return "{\n" + "\n".join(linhas) + f"\n{tab}}}"
    if isinstance(valor, list):
        if not valor:
            return "[ ]"
        if all(isinstance(v, (str, int, float, bool)) for v in valor):
            return "[" + ", ".join(snbt(v, nivel) for v in valor) + "]"
        itens = [f"{tab}\t{snbt(v, nivel + 1)}" for v in valor]
        return "[\n" + "\n".join(itens) + f"\n{tab}]"
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, Raw):
        return valor.s
    if isinstance(valor, float):
        return f"{valor}d"
    if isinstance(valor, int):
        return str(valor)
    return json.dumps(valor, ensure_ascii=False)


class Raw:
    """Valor SNBT escrito literalmente (ex.: 1b, 16L)."""
    def __init__(self, s):
        self.s = s


def L(n):
    return Raw(f"{n}L")


def item(id_, count=1, tag=None):
    if tag is None and count == 1:
        return id_
    d = {"id": id_, "Count": Raw(f"{count}b")}
    if tag:
        d["tag"] = tag
    return d


def nome_lore(nome, cor, lore):
    return {"display": {
        "Name": json.dumps({"text": nome, "color": cor, "italic": False}, ensure_ascii=False),
        "Lore": [json.dumps({"text": l, "color": "gray", "italic": True}, ensure_ascii=False) for l in lore],
    }}


def livro_skill(skill):
    return item("epicfight:skillbook", tag={"skill": skill})


def pergaminho(spell, nivel=1):
    return item("irons_spellbooks:scroll", tag={"ISB_Spells": {
        "data": [{"id": spell, "index": 0, "level": nivel, "locked": Raw("1b")}],
        "maxSpells": 1, "mustEquip": Raw("0b"), "spellWheel": Raw("0b")}})


def pocao(tipo):
    return item("minecraft:potion", tag={"Potion": tipo})


def ovo_dragao(raca):
    return item("dragonmounts:dragon_egg", tag={"BlockEntityTag": {"Breed": raca}})


def fragmento(ato, numero, total):
    return item("minecraft:amethyst_shard", tag={
        **nome_lore("Fragmento do Selo", "light_purple",
                    [f"Ato {ato}: fragmento {numero} de {total}.",
                     "Um pedaço do cristal que prendia o mal antigo.",
                     "Ainda está quente ao toque."]),
        "Enchantments": [{"id": "minecraft:unbreaking", "lvl": Raw("1s")}],
        "HideFlags": 1,
    })


# ---------------------------------------------------------------- tarefas e recompensas

class Capitulo:
    def __init__(self, chave):
        self.chave = chave
        self.quests = []
        self.n = 0

    def _id(self, sufixo):
        self.n += 1
        return qid(f"{self.chave}/{sufixo}/{self.n}")

    # tarefas
    def t_check(self, titulo=None):
        t = {"id": self._id("t"), "type": "checkmark"}
        if titulo:
            t["title"] = titulo
        return t

    def t_item(self, it, count=1, consumir=False, titulo=None):
        t = {"id": self._id("t"), "type": "item", "item": it, "count": L(count)}
        if consumir:
            t["consume_items"] = True
        if titulo:
            t["title"] = titulo
        return t

    def t_matar(self, entidade, n=1, titulo=None):
        t = {"id": self._id("t"), "type": "kill", "entity": entidade, "value": L(n)}
        if titulo:
            t["title"] = titulo
        return t

    def t_estrutura(self, estrutura, titulo=None):
        t = {"id": self._id("t"), "type": "structure", "structure": estrutura}
        if titulo:
            t["title"] = titulo
        return t

    def t_conquista(self, adv, titulo=None):
        t = {"id": self._id("t"), "type": "advancement", "advancement": adv, "criterion": ""}
        if titulo:
            t["title"] = titulo
        return t

    # recompensas
    def r_item(self, it, count=1):
        r = {"id": self._id("r"), "type": "item", "item": it}
        if count != 1:
            r["count"] = count
        return r

    def r_xp(self, niveis):
        return {"id": self._id("r"), "type": "xp_levels", "xp_levels": niveis}

    def r_comando(self, comando, titulo=None, icone=None):
        r = {"id": self._id("r"), "type": "command", "command": comando,
             "elevate_perms": True, "silent": True}
        if titulo:
            r["title"] = titulo
        if icone:
            r["icon"] = icone
        return r

    def r_mapa(self, nome, titulo):
        """Mapa do tesouro apontando para a estrutura (loot table do datapack)."""
        return self.r_comando(f"/loot give {{p}} loot terras_partidas:mapas/{nome}",
                              titulo=titulo, icone="minecraft:filled_map")

    def r_localizar(self, estrutura, titulo, dimensao="minecraft:the_nether"):
        """Roda /locate e mostra as coordenadas no chat do jogador."""
        return {"id": self._id("r"), "type": "command",
                "command": f"/execute in {dimensao} run locate structure {estrutura}",
                "elevate_perms": True, "silent": False,
                "title": titulo, "icon": "minecraft:compass"}

    def t_dimensao(self, dimensao, titulo=None):
        t = {"id": self._id("t"), "type": "dimension", "dimension": dimensao}
        if titulo:
            t["title"] = titulo
        return t

    def r_skill(self, skill):
        return self.r_item(livro_skill(skill))

    # missão
    def quest(self, chave, titulo, x, y, descricao, tarefas, recompensas=(), deps=(),
              subtitulo=None, icone=None, forma=None, tamanho=None, **extra):
        q = {"id": qid(f"{self.chave}/quest/{chave}"), "title": titulo, "x": float(x), "y": float(y)}
        if subtitulo:
            q["subtitle"] = subtitulo
        if icone:
            q["icon"] = icone
        if forma:
            q["shape"] = forma
        if tamanho:
            q["size"] = float(tamanho)
        q["description"] = descricao
        if deps:
            # "@ato1/relatorio" aponta para uma missão de outro capítulo
            q["dependencies"] = [qid(f"{d[1:].split('/')[0]}/quest/{d[1:].split('/')[1]}") if d.startswith("@")
                                 else qid(f"{self.chave}/quest/{d}") for d in deps]
        q.update(extra)
        # IDs de tarefas/recompensas dependem só desta missão e da posição dentro dela,
        # assim inserir missões novas em outro lugar não muda nada aqui.
        for i, t in enumerate(tarefas):
            t["id"] = qid(f"{self.chave}/quest/{chave}/tarefa/{i}")
        for i, r in enumerate(recompensas):
            r["id"] = qid(f"{self.chave}/quest/{chave}/recompensa/{i}")
        q["tasks"] = list(tarefas)
        if recompensas:
            q["rewards"] = list(recompensas)
        self.quests.append(q)
        return q


# ---------------------------------------------------------------- ATO 1

def ato1():
    c = Capitulo("ato1")
    M = "&6Mestre Vellan&r"  # o Mestre da Ordem dos Caçadores

    # ---- Prólogo
    c.quest("chamado", "O Chamado", 0, 0, forma="gear", tamanho=1.5,
            icone="minecraft:writable_book",
            subtitulo="Uma carta com o selo da Ordem",
            descricao=[
                "&o\"Caçador,",
                "",
                "&oHá trezentos anos, sete guardiões prenderam um mal antigo dentro de um cristal: o &dSelo&r&o.",
                "&oNa última lua cheia, o Selo se partiu. Os fragmentos caíram pelo mundo e cada um corrompeu uma criatura poderosa.",
                "",
                "&oSe juntarmos os fragmentos antes que o mal desperte, ainda há esperança.",
                "&oA Ordem dos Caçadores precisa de você.\"",
                "",
                f"— {M}, Mestre da Ordem",
                "{@pagebreak}",
                "&eComo usar este livro:&r",
                "• Cada missão mostra o objetivo e a recompensa.",
                "• Clique em uma missão para ver os detalhes e pegar a recompensa.",
                "• Missões novas aparecem conforme você avança.",
                "",
                "&eCombate:&r este mundo usa o &cEpic Fight&r. Aperte &eR&r para alternar entre o modo normal e o modo de combate.",
                "As outras teclas ficam em &eOpções > Controles&r, na seção do Epic Fight.",
            ],
            tarefas=[c.t_check("Li a carta do Mestre")],
            recompensas=[c.r_item("minecraft:bread", 8), c.r_item("minecraft:torch", 16),
                         c.r_item(livro_skill("epicfight:roll"))])

    # ---- Escolha de classe
    c.quest("caminho", "Escolha seu Caminho", 2.5, 0, forma="hexagon", tamanho=1.25,
            icone="minecraft:compass", deps=["chamado"],
            max_completable_dependents=1,
            subtitulo="Só dá para escolher uma vez",
            descricao=[
                f"{M}: \"Todo caçador tem um estilo. Qual é o seu?\"",
                "",
                "Escolha &cuma&r das cinco classes ao lado. Cada uma dá um kit inicial diferente.",
                "&cAtenção:&r depois de completar uma classe, as outras ficam bloqueadas.",
                "",
                "&cGuerreiro&r: espada longa e armadura. Equilibrado.",
                "&9Tanque&r: escudo, armadura pesada e técnica de aparar.",
                "&8Assassino&r: duas adagas, velocidade e esquiva rápida.",
                "&5Mago&r: livro de feitiços e pergaminhos de magia.",
                "&aCaçador&r: arco, flechas e mobilidade.",
            ],
            tarefas=[c.t_check("Estou pronto para escolher")])

    classes = [
        ("guerreiro", "&cGuerreiro", -2, "epicfight:iron_longsword",
         "Você luta de frente, com espada longa e armadura. Bom para quem está começando.",
         [c.r_item("epicfight:iron_longsword"), c.r_item("minecraft:chainmail_chestplate"),
          c.r_item("minecraft:chainmail_helmet"), c.r_item("minecraft:cooked_beef", 12)]),
        ("tanque", "&9Tanque", -1, "minecraft:shield",
         "Você aguenta pancada. Escudo, armadura de ferro e a técnica de &eAparar&r do Epic Fight.",
         [c.r_item("minecraft:shield"), c.r_item("minecraft:iron_chestplate"),
          c.r_item("epicfight:iron_spear"), c.r_item(livro_skill("epicfight:parrying")),
          c.r_item("minecraft:cooked_beef", 12)]),
        ("assassino", "&8Assassino", 0, "epicfight:iron_dagger",
         "Você é rápido. Duas adagas (uma em cada mão), poções de velocidade e o &ePasso&r, uma esquiva mais curta e ágil.",
         [c.r_item("epicfight:iron_dagger"), c.r_item("epicfight:iron_dagger"),
          c.r_item(pocao("minecraft:swiftness"), 2), c.r_item(livro_skill("epicfight:step")),
          c.r_item("minecraft:ender_pearl", 2), c.r_item("minecraft:cooked_beef", 12)]),
        ("mago", "&5Mago", 1, "irons_spellbooks:copper_spell_book",
         "Você usa magia. Pergaminhos podem ser lidos direto (clique direito) ou gravados no livro na &eMesa de Inscrição&r.",
         [c.r_item("irons_spellbooks:copper_spell_book"), c.r_item("irons_spellbooks:inscription_table"),
          c.r_item(pergaminho("irons_spellbooks:firebolt")), c.r_item(pergaminho("irons_spellbooks:magic_missile")),
          c.r_item(pergaminho("irons_spellbooks:heal")), c.r_item("irons_spellbooks:wandering_magician_chestplate"),
          c.r_item("minecraft:cooked_beef", 12)]),
        ("cacador", "&aCaçador", 2, "minecraft:bow",
         "Você ataca de longe. Arco, muitas flechas e uma adaga para quando o inimigo chegar perto.",
         [c.r_item("minecraft:bow"), c.r_item("minecraft:arrow", 64), c.r_item("epicfight:iron_dagger"),
          c.r_item("minecraft:leather_chestplate"), c.r_item("minecraft:cooked_beef", 12)]),
    ]
    for chave, nome, dy, icone, texto, recs in classes:
        c.quest(chave, nome, 5, dy * 1.25, icone=icone, deps=["caminho"], forma="diamond",
                descricao=[f"{M}: \"Então você é um {nome}&r.\"", "", texto],
                tarefas=[c.t_check(f"Eu escolho ser {nome}")], recompensas=recs)
    nomes_classes = [k for k, *_ in classes]

    # ---- Trilha de sobrevivência (em cima)
    c.quest("ferro", "Ferramentas de Ferro", 7.5, -2.5, icone="minecraft:iron_pickaxe",
            deps=nomes_classes, dependency_requirement="one_completed",
            descricao=[f"{M}: \"Ninguém caça de mãos vazias. Arrume ferramentas decentes.\"",
                       "", "Faça uma &fpicareta de ferro&r."],
            tarefas=[c.t_item("minecraft:iron_pickaxe")],
            recompensas=[c.r_xp(3), c.r_item("minecraft:iron_ingot", 4)])

    c.quest("mochila", "Uma Mochila de Verdade", 10, -3.5, icone="sophisticatedbackpacks:backpack",
            deps=["ferro"],
            descricao=["O inventário vai encher rápido. Faça uma &fmochila&r.",
                       "Dá para melhorar ela depois (cobre, ferro, ouro...)."],
            tarefas=[c.t_item("sophisticatedbackpacks:backpack")],
            recompensas=[c.r_xp(2), c.r_item("minecraft:leather", 4)])

    c.quest("dormir", "Abrigo Seguro", 10, -1.5, icone="minecraft:red_bed",
            deps=["ferro"],
            descricao=["As noites aqui são bem mais perigosas do que você está acostumado.",
                       "Faça uma cama e &fdurma&r para pular a noite e marcar seu ponto de renascer."],
            tarefas=[c.t_conquista("minecraft:adventure/sleep_in_bed", "Dormir em uma cama")],
            recompensas=[c.r_item("minecraft:lantern", 4), c.r_item("minecraft:cooked_porkchop", 8)])

    c.quest("vila", "Uma Vila Amiga", 12.5, -2.5, icone="minecraft:emerald",
            deps=["mochila", "dormir"],
            descricao=[f"{M}: \"As vilas são o último refúgio deste mundo. Os &fguardas&r protegem os aldeões, mas precisam de ajuda.\"",
                       "", "Encontre uma &fvila&r. Muitas delas têm uma &bWaystone&r, uma pedra que te teleporta entre lugares já visitados."],
            tarefas=[c.t_estrutura("#minecraft:village", "Encontrar uma vila")],
            recompensas=[c.r_xp(3), c.r_item("minecraft:emerald", 8)])

    # ---- Trilha de combate (embaixo)
    c.quest("treino", "Treino de Combate", 7.5, 2.5, icone="minecraft:iron_sword",
            deps=nomes_classes, dependency_requirement="one_completed",
            descricao=[f"{M}: \"Antes de enfrentar algo de verdade, aprenda a lutar.\"",
                       "", "No Epic Fight, &eesquivar&r e &edefender&r gasta a barra de fôlego. Não ataque sem parar: espere a abertura do inimigo.",
                       "", "Derrote &c10 zumbis&r."],
            tarefas=[c.t_matar("minecraft:zombie", 10, "Derrotar 10 zumbis")],
            recompensas=[c.r_xp(3), c.r_item("minecraft:golden_apple")])

    c.quest("ossos", "Ossos Inquietos", 10, 2.5, icone="minecraft:bone",
            deps=["treino"],
            descricao=["Esqueletos de longe são piores que zumbis. Use cobertura e aproxime-se esquivando.",
                       "", "Derrote &c10 esqueletos&r."],
            tarefas=[c.t_matar("minecraft:skeleton", 10, "Derrotar 10 esqueletos")],
            recompensas=[c.r_xp(3), c.r_item("minecraft:arrow", 32)])

    # ---- Chefe 1: Swampjaw
    c.quest("isca", "Algo no Pântano", 12.5, 2.5, icone="meetyourfight:fossil_bait",
            deps=["ossos"],
            subtitulo="Primeiro fragmento",
            descricao=[f"{M}: \"Pescadores sumiram perto dos pântanos. Algo enorme come qualquer coisa que se move por lá... e eu sinto um fragmento do Selo dentro dele.\"",
                       "", "Pegue esta &fIsca Fóssil&r. Quando estiver pronto, use-a (clique direito) para chamar a criatura.",
                       "", "&7Equipamento recomendado: pedra ou ferro.&r"],
            tarefas=[c.t_check("Estou pronto")],
            recompensas=[c.r_item("meetyourfight:fossil_bait"), c.r_item(pocao("minecraft:healing"), 2)])

    c.quest("swampjaw", "Chefe: Swampjaw", 15, 2.5, icone="meetyourfight:fossil_bait",
            deps=["isca"], forma="octagon", tamanho=1.5,
            descricao=["Use a Isca Fóssil e derrote &cSwampjaw&r.",
                       "", "&dRecompensa especial:&r o livro de &ePulo Fantasma&r (pulo duplo no ar).",
                       "", "&7Se morrer, a isca é gasta. Volte aqui: a missão &e\"Mais uma Isca\"&7 dá outra."],
            tarefas=[c.t_matar("meetyourfight:swampjaw", 1, "Derrotar Swampjaw")],
            recompensas=[c.r_item(fragmento(1, 1, 3)), c.r_skill("epicfight:phantom_ascent"), c.r_xp(5),
                         c.r_item("minecraft:diamond", 1)])

    c.quest("isca_extra", "Mais uma Isca", 15, 4.5, icone="meetyourfight:fossil_bait",
            deps=["isca"], forma="circle", tamanho=0.75, optional=True,
            can_repeat=True,
            descricao=["Perdeu a luta? Troque &f8 ossos&r por outra Isca Fóssil.", "Pode repetir quantas vezes precisar."],
            tarefas=[c.t_item("minecraft:bone", 8, consumir=True)],
            recompensas=[c.r_item("meetyourfight:fossil_bait")])

    # ---- Chefe 2: Bellringer
    c.quest("sino", "O Sino Assombrado", 17.5, 0, icone="meetyourfight:haunted_bell",
            deps=["swampjaw", "ferro"],
            subtitulo="Segundo fragmento",
            descricao=[f"{M}: \"Muito bem. O segundo fragmento está preso a um espírito que toca um sino nas ruínas. Cada badalada atrai a morte.\"",
                       "", "Pegue o &fSino Assombrado&r. Tocá-lo invoca o &cBellringer&r.",
                       "", "&7Equipamento recomendado: ferro ou diamante. Ele é rápido: guarde a esquiva para quando ele avançar.&r"],
            tarefas=[c.t_item("minecraft:iron_chestplate", titulo="Ter um peitoral de ferro")],
            recompensas=[c.r_item("meetyourfight:haunted_bell"), c.r_item(pocao("minecraft:healing"), 3)])

    c.quest("bellringer", "Chefe: Bellringer", 20, 0, icone="meetyourfight:haunted_bell",
            deps=["sino"], forma="octagon", tamanho=1.5,
            descricao=["Toque o Sino Assombrado e derrote o &cBellringer&r."],
            tarefas=[c.t_matar("meetyourfight:bellringer", 1, "Derrotar o Bellringer")],
            recompensas=[c.r_item(fragmento(1, 2, 3)), c.r_skill("epicfight:technician"), c.r_xp(7),
                         c.r_item("minecraft:diamond", 2)])

    c.quest("sino_extra", "Outro Sino", 20, 2, icone="meetyourfight:haunted_bell",
            deps=["sino"], forma="circle", tamanho=0.75, optional=True, can_repeat=True,
            descricao=["Perdeu a luta? Troque &f4 lingotes de ouro&r por outro Sino Assombrado."],
            tarefas=[c.t_item("minecraft:gold_ingot", 4, consumir=True)],
            recompensas=[c.r_item("meetyourfight:haunted_bell")])

    # ---- Chefe 3: Ferrous Wroughtnaut
    c.quest("rumores", "Rumores na Vila", 15, -4.5, icone="minecraft:filled_map",
            deps=["vila", "swampjaw"],
            subtitulo="Terceiro fragmento",
            descricao=[f"{M}: \"Os aldeões falam de um &fcavaleiro de metal&r que guarda uma câmara no subsolo. Nunca saiu de lá, nunca dormiu... e agora carrega um fragmento do Selo.\"",
                       "", "&o\"Um minerador desenhou este mapa antes de fugir. O X marca a entrada.\"",
                       "", "&7Segure o mapa na mão para ver o caminho. O mapa pode demorar alguns segundos para aparecer.&r"],
            tarefas=[c.t_check("Pegar o mapa")],
            recompensas=[c.r_mapa("camara_forjada", "Mapa: Câmara Forjada"),
                         c.r_item(pocao("minecraft:night_vision"), 2)])

    c.quest("camara", "A Câmara Forjada", 17.5, -4.5, icone="mowziesmobs:wrought_helmet",
            deps=["rumores"],
            descricao=["Siga o mapa até o &fX vermelho&r. A Câmara fica &fno subsolo&r (entre as camadas Y 20 e 50): cave para baixo quando chegar no ponto.",
                       "", "&7Dica: os mapas do Xaero ajudam a marcar o caminho (tecla &eB&7 para criar um ponto de referência).&r"],
            tarefas=[c.t_estrutura("mowziesmobs:wrought_chamber", "Encontrar a Câmara Forjada")],
            recompensas=[c.r_xp(3), c.r_item(pocao("minecraft:strength"), 2)])

    c.quest("wroughtnaut", "Chefe: Cavaleiro Forjado", 20, -4.5, icone="mowziesmobs:wrought_axe",
            deps=["camara"], forma="octagon", tamanho=1.5,
            descricao=["Derrote o &cCavaleiro de Ferro Forjado&r (Ferrous Wroughtnaut).",
                       "", "&7Dica: a armadura dele é quase indestrutível pela frente. Espere ele errar um golpe, fique atrás dele e ataque as costas.&r"],
            tarefas=[c.t_matar("mowziesmobs:ferrous_wroughtnaut", 1, "Derrotar o Cavaleiro Forjado")],
            recompensas=[c.r_item(fragmento(1, 3, 3)), c.r_skill("epicfight:swordmaster"), c.r_xp(7),
                         c.r_item("minecraft:diamond", 2)])

    # ---- Final do Ato 1
    c.quest("relatorio", "Relatório ao Mestre", 23, -1.75, icone="minecraft:amethyst_shard",
            deps=["swampjaw", "bellringer", "wroughtnaut"], forma="gear", tamanho=2.0,
            subtitulo="Fim do Ato 1",
            descricao=[f"{M}: \"Três fragmentos... Você fez o que nenhum caçador conseguiu em anos.\"",
                       "",
                       "&o\"Mas sinto o Selo pulsando mais forte. Os outros fragmentos foram para lugares piores: o gelo eterno, as savanas queimadas, o fundo do mar.",
                       "&oVocê vai precisar ir longe. Leve isto: um planador, para atravessar o mundo pelos céus.\"",
                       "",
                       "&dFim do Ato 1. O Ato 2 &7(Terras Selvagens)&d chega em breve.&r"],
            tarefas=[c.t_check("Entregar o relatório")],
            recompensas=[c.r_item("paraglider:paraglider"), c.r_item("minecraft:diamond", 3),
                         c.r_item("minecraft:golden_apple", 2), c.r_xp(10)])

    return {
        "id": qid("capitulo/ato1"),
        "group": "",
        "order_index": 0,
        "filename": "ato_1_o_chamado",
        "title": "Ato 1: O Chamado",
        "subtitle": ["Três fragmentos do Selo"],
        "icon": "minecraft:amethyst_shard",
        "default_quest_shape": "",
        "default_hide_dependency_lines": False,
        "quests": c.quests,
    }



# ---------------------------------------------------------------- ATO 2

def ato2():
    c = Capitulo("ato2")
    M = "&6Mestre Vellan&r"

    c.quest("asas", "Terras Selvagens", 0, 0, forma="gear", tamanho=1.75,
            icone="paraglider:paraglider", deps=["@ato1/relatorio"],
            subtitulo="Quatro fragmentos espalhados pelo mundo",
            descricao=[
                f"{M}: \"Os batedores da Ordem voltaram. Quatro fragmentos foram vistos em lugares onde poucos sobrevivem:\"",
                "",
                "• &bO Gelo Eterno&r, onde algo enorme dorme sob a neve.",
                "• &6As Savanas Queimadas&r, onde uma tribo mascarada serve a um pássaro de fogo.",
                "• &3O Labirinto de Gelo&r, um mar congelado cheio de navios fantasmas.",
                "• &5A Mesa da Fortuna&r, onde uma jogadora aposta almas.",
                "",
                "&o\"Use o planador para atravessar montanhas e vales. Ele gasta fôlego, então pouse antes que acabe.\"",
                "",
                "&7Você pode fazer as quatro frentes na ordem que quiser.&r",
            ],
            tarefas=[c.t_check("Partir para as Terras Selvagens")],
            recompensas=[c.r_item("minecraft:cooked_beef", 16), c.r_item("minecraft:golden_carrot", 8), c.r_xp(3)])

    # ---- Preparação (missões de apoio, em cima)
    c.quest("mochila_ferro", "Mochila Maior", -2.5, -3, icone="sophisticatedbackpacks:iron_backpack",
            deps=["asas"], optional=True,
            descricao=["Viagens longas pedem espaço. Melhore sua mochila para a de &fferro&r."],
            tarefas=[c.t_item("sophisticatedbackpacks:iron_backpack")],
            recompensas=[c.r_xp(3), c.r_item("minecraft:iron_ingot", 8)])

    c.quest("encantar", "Conhecimento Arcano", 0, -3, icone="minecraft:enchanting_table",
            deps=["asas"], optional=True,
            descricao=["Monstros das Terras Selvagens batem forte. Faça uma &fmesa de encantamento&r."],
            tarefas=[c.t_item("minecraft:enchanting_table")],
            recompensas=[c.r_item("minecraft:lapis_lazuli", 16), c.r_item("minecraft:bookshelf", 4), c.r_xp(5)])

    c.quest("waystone", "Sua Própria Waystone", 2.5, -3, icone="waystones:waystone",
            deps=["asas"], optional=True,
            descricao=["Faça uma &bWaystone&r e coloque perto da sua base. Assim você volta de qualquer frente em segundos."],
            tarefas=[c.t_item("waystones:waystone")],
            recompensas=[c.r_item("waystones:warp_dust", 8), c.r_xp(3)])

    # ---- Frente 1: Gelo Eterno (Frostmaw)
    c.quest("gelo", "O Gelo Eterno", 4, 2.5, icone="minecraft:snowball", deps=["asas"],
            subtitulo="Frente do Gelo",
            descricao=[f"{M}: \"Nas terras nevadas, um caçador viu uma criatura gigante dormindo ao lado de um cristal de gelo. Ele não voltou para contar o resto.\"",
                       "", "&o\"Este mapa marca onde ele foi visto pela última vez.\"",
                       "", "&7Leve roupas quentes... e comida. É longe.&r"],
            tarefas=[c.t_check("Pegar o mapa do gelo")],
            recompensas=[c.r_mapa("covil_frostmaw", "Mapa: Covil do Frostmaw"), c.r_item("minecraft:cooked_salmon", 12)])

    c.quest("covil", "O Covil Congelado", 7, 2.5, icone="minecraft:packed_ice", deps=["gelo"],
            descricao=["Siga o mapa até o &fX vermelho&r, em um bioma de neve."],
            tarefas=[c.t_estrutura("mowziesmobs:frostmaw_spawn", "Encontrar o covil do Frostmaw")],
            recompensas=[c.r_xp(3)])

    c.quest("frostmaw", "Chefe: Frostmaw", 10, 2.5, icone="mowziesmobs:ice_crystal",
            deps=["covil"], forma="octagon", tamanho=1.5,
            descricao=["O &cFrostmaw&r está dormindo. Acorde-o com um golpe e prepare-se.",
                       "", "&7Dica: ele sopra gelo em linha reta e dá saltos que esmagam. Corra para os lados e ataque depois do salto.",
                       "&7Ele pode soltar o &fCristal de Gelo&7, uma arma muito poderosa.&r"],
            tarefas=[c.t_matar("mowziesmobs:frostmaw", 1, "Derrotar o Frostmaw")],
            recompensas=[c.r_item(fragmento(2, 1, 4)), c.r_skill("epicfight:hypervitality"), c.r_xp(10),
                         c.r_item("minecraft:diamond", 3)])

    # ---- Frente 2: Savanas Queimadas (Umvuthi)
    c.quest("savana", "As Savanas Queimadas", 4, 5.5, icone="minecraft:acacia_sapling", deps=["asas"],
            subtitulo="Frente da Savana",
            descricao=[f"{M}: \"Nas savanas vive a tribo dos &6Umvuthana&r, guerreiros mascarados. Eles servem a &6Umvuthi, o Pássaro do Sol&r, e agora o fragmento brilha no peito dele.\"",
                       "", "&o\"Cuidado: eles atacam em bando e usam lanças e magia de cura.\""],
            tarefas=[c.t_check("Pegar o mapa da savana")],
            recompensas=[c.r_mapa("bosque_umvuthana", "Mapa: Bosque dos Umvuthana"), c.r_item(pocao("minecraft:fire_resistance"), 2)])

    c.quest("bosque", "O Bosque dos Umvuthana", 7, 5.5, icone="minecraft:acacia_log", deps=["savana"],
            descricao=["Siga o mapa até o bosque, em uma savana."],
            tarefas=[c.t_estrutura("mowziesmobs:umvuthana_grove", "Encontrar o bosque")],
            recompensas=[c.r_xp(3), c.r_item(pocao("minecraft:healing"), 2)])

    c.quest("umvuthi", "Chefe: Umvuthi", 10, 5.5, icone="minecraft:blaze_powder",
            deps=["bosque"], forma="octagon", tamanho=1.5,
            descricao=["Atravesse os guerreiros mascarados e suba até o &ftrono&r no centro do bosque. &cUmvuthi&r vai aparecer.",
                       "", "&7Dica: ele invoca raios de sol e guerreiros que o curam. Derrube os curandeiros primeiro.&r"],
            tarefas=[c.t_matar("mowziesmobs:umvuthi", 1, "Derrotar Umvuthi")],
            recompensas=[c.r_item(fragmento(2, 2, 4)), c.r_skill("epicfight:demolition_leap"), c.r_xp(10),
                         c.r_item("minecraft:diamond", 3)])

    # ---- Frente 3: Labirinto de Gelo (Capitã Cornelia)
    c.quest("mar", "O Mar Congelado", -4, 2.5, icone="minecraft:blue_ice", deps=["asas"],
            subtitulo="Frente do Mar",
            descricao=[f"{M}: \"Existe um mar onde o gelo forma corredores sem fim: o &3Labirinto de Gelo&r. Navios piratas congelados estão presos lá há séculos.\"",
                       "", "&o\"A capitã de um desses navios voltou como fantasma. O fragmento a mantém presa a este mundo.\"",
                       "", "&7Leve um barco. A água é gelada e cheia de criaturas das profundezas.&r"],
            tarefas=[c.t_check("Pegar o mapa do mar")],
            recompensas=[c.r_mapa("labirinto_de_gelo", "Mapa: Labirinto de Gelo"), c.r_item("minecraft:oak_boat"),
                         c.r_item(pocao("minecraft:water_breathing"), 2)])

    c.quest("labirinto", "O Labirinto de Gelo", -7, 2.5, icone="minecraft:packed_ice", deps=["mar"],
            descricao=["Siga o mapa e entre no &3Labirinto de Gelo&r: o oceano congelado profundo, cheio de icebergs e navios presos no gelo."],
            tarefas=[{"id": "", "type": "biome", "biome": "#aquamirae:ice_maze", "title": "Entrar no Labirinto de Gelo"}],
            recompensas=[c.r_xp(3)])

    c.quest("corneta", "A Concha-Corneta", -10, 2.5, icone="aquamirae:shell_horn", deps=["labirinto"],
            descricao=[f"{M} &7(por carta)&r: \"Encontrei nos arquivos da Ordem: a capitã atende ao som de uma &fConcha-Corneta&r. Mandei uma para você.\"",
                       "", "Use a Concha-Corneta &fperto da água, dentro do Labirinto de Gelo&r, para invocar a capitã.",
                       "", "&7Ela também aparece às vezes em baús dos navios congelados.&r"],
            tarefas=[c.t_check("Receber a Concha-Corneta")],
            recompensas=[c.r_item("aquamirae:shell_horn"), c.r_item(pocao("minecraft:healing"), 3)])

    c.quest("cornelia", "Chefe: Capitã Cornelia", -13, 2.5, icone="aquamirae:shell_horn",
            deps=["corneta"], forma="octagon", tamanho=1.5,
            descricao=["Toque a Concha-Corneta e derrote o &cFantasma da Capitã Cornelia&r.",
                       "", "&7Dica: lute em terra firme ou em cima do gelo, nunca dentro da água.&r"],
            tarefas=[c.t_matar("aquamirae:captain_cornelia", 1, "Derrotar a Capitã Cornelia")],
            recompensas=[c.r_item(fragmento(2, 3, 4)), c.r_skill("epicfight:meteor_slam"), c.r_xp(10),
                         c.r_item("minecraft:diamond", 3)])

    c.quest("corneta_extra", "Outra Corneta", -13, 4.5, icone="aquamirae:shell_horn",
            deps=["corneta"], forma="circle", tamanho=0.75, optional=True, can_repeat=True,
            descricao=["Perdeu a luta? Troque &f8 cristais de prismarinho&r por outra Concha-Corneta."],
            tarefas=[c.t_item("minecraft:prismarine_crystals", 8, consumir=True)],
            recompensas=[c.r_item("aquamirae:shell_horn")])

    c.quest("mae_labirinto", "A Mãe do Labirinto", -10, 0.5, icone="minecraft:spider_eye",
            deps=["labirinto"], forma="circle", optional=True,
            descricao=["&7Missão extra.&r Dizem que uma criatura chamada &cMãe do Labirinto&r caça nos corredores de gelo.",
                       "Derrote-a se tiver coragem."],
            tarefas=[c.t_matar("aquamirae:maze_mother", 1, "Derrotar a Mãe do Labirinto")],
            recompensas=[c.r_item("minecraft:diamond", 2), c.r_xp(5)])

    # ---- Frente 4: Mesa da Fortuna (Dame Fortuna)
    c.quest("fortuna", "A Aposta do Diabo", -4, 5.5, icone="meetyourfight:devils_ante", deps=["asas"],
            subtitulo="Frente da Fortuna",
            descricao=[f"{M}: \"Esta é a mais traiçoeira. &5Dame Fortuna&r é um espírito que aposta com a sorte. Ela ganhou um fragmento num jogo de cartas.\"",
                       "", "&o\"Só aceito te dar a ficha de aposta quando você estiver protegido. Volte com armadura de diamante.\"",
                       "", "&7Equipamento recomendado: diamante.&r"],
            tarefas=[c.t_item("minecraft:diamond_chestplate", titulo="Ter um peitoral de diamante")],
            recompensas=[c.r_item("meetyourfight:devils_ante"), c.r_item(pocao("minecraft:regeneration"), 2)])

    c.quest("dame_fortuna", "Chefe: Dame Fortuna", -7, 5.5, icone="meetyourfight:devils_ante",
            deps=["fortuna"], forma="octagon", tamanho=1.5,
            descricao=["Use a Aposta do Diabo e derrote &cDame Fortuna&r.",
                       "", "&7Dica: ela troca de padrão de ataque como quem embaralha cartas. Observe antes de atacar.&r"],
            tarefas=[c.t_matar("meetyourfight:dame_fortuna", 1, "Derrotar Dame Fortuna")],
            recompensas=[c.r_item(fragmento(2, 4, 4)), c.r_skill("epicfight:stamina_pillager"), c.r_xp(10),
                         c.r_item("minecraft:diamond", 3)])

    c.quest("ante_extra", "Nova Aposta", -7, 7.5, icone="meetyourfight:devils_ante",
            deps=["fortuna"], forma="circle", tamanho=0.75, optional=True, can_repeat=True,
            descricao=["Perdeu a aposta? Troque &f2 diamantes&r por outra ficha."],
            tarefas=[c.t_item("minecraft:diamond", 2, consumir=True)],
            recompensas=[c.r_item("meetyourfight:devils_ante")])

    # ---- Final do Ato 2
    c.quest("relatorio", "Relatório: Terras Selvagens", 0, 9, icone="minecraft:amethyst_shard",
            deps=["frostmaw", "umvuthi", "cornelia", "dame_fortuna"], forma="gear", tamanho=2.0,
            subtitulo="Fim do Ato 2",
            descricao=[f"{M}: \"Sete fragmentos. Mais da metade do Selo...\"",
                       "",
                       "&o\"Mas os batedores trouxeram notícias ruins. Os fragmentos que faltam não estão mais neste mundo. Eles caíram por uma fenda até o &cNether&o, e o calor lá está despertando algo antigo.\"",
                       "",
                       "&o\"Construa um portal. Quando estiver pronto, eu te conto o que sabemos.\"",
                       "",
                       "&dFim do Ato 2. O Ato 3 &7(Abismo e Fogo)&d chega em breve.&r"],
            tarefas=[c.t_check("Entregar o relatório")],
            recompensas=[c.r_item("minecraft:obsidian", 10), c.r_item("minecraft:flint_and_steel"),
                         c.r_item(pocao("minecraft:fire_resistance"), 4), c.r_item("minecraft:diamond", 5),
                         c.r_xp(15)])

    # ---- Ovo de dragão (recompensa do fim do Ato 2)
    c.quest("ovo", "O Presente do Mestre", 0, 12.5, icone="dragonmounts:dragon_egg",
            deps=["relatorio"], forma="hexagon", tamanho=1.5,
            max_completable_dependents=1,
            subtitulo="Escolha só um ovo",
            descricao=[f"{M}: \"Antes de você partir para o Nether, tenho algo guardado há muito tempo.\"",
                       "",
                       "&o\"Os antigos guardiões do Selo voavam em dragões. Quando o Selo foi criado, eles esconderam os últimos ovos com a Ordem. Você mereceu um.\"",
                       "",
                       "Escolha &cum&r dos quatro ovos ao lado. Depois de escolher, os outros ficam bloqueados.",
                       "",
                       "&6Fogo&r: resiste a fogo e lava. Bom para o Nether.",
                       "&bGelo&r: aguenta o frio e as terras nevadas.",
                       "&3Água&r: nada e respira embaixo d'água.",
                       "&aFloresta&r: o mais calmo, ótimo para viajar."],
            tarefas=[c.t_check("Quero um ovo de dragão")])

    ovos = [
        ("ovo_fogo", "&6Ovo de Dragão de Fogo", -4.5, "dragonmounts:fire", "minecraft:magma_block",
         "lava, fogo, fogueira ou blocos de magma"),
        ("ovo_gelo", "&bOvo de Dragão de Gelo", -1.5, "dragonmounts:ice", "minecraft:packed_ice",
         "gelo ou neve"),
        ("ovo_agua", "&3Ovo de Dragão de Água", 1.5, "dragonmounts:water", "minecraft:prismarine",
         "prismarinho, lanterna do mar, algas ou corais"),
        ("ovo_floresta", "&aOvo de Dragão de Floresta", 4.5, "dragonmounts:forest", "minecraft:moss_block",
         "folhas, flores, mudas ou musgo"),
    ]
    for chave, nome, x, raca, bloco, habitat in ovos:
        c.quest(chave, nome, x, 15, icone=ovo_dragao(raca), deps=["ovo"], forma="diamond",
                descricao=[f"Você escolheu o {nome}&r.",
                           "",
                           "&eComo chocar:&r coloque o ovo no chão e &fclique nele com o botão direito&r para ele começar a chocar. Depois é só esperar.",
                           "&7O ovo cai como areia: coloque em cima de um bloco firme.&r",
                           "",
                           f"&cCuidado:&r o ambiente muda o tipo do dragão! Deixe o ovo perto de &f{habitat}&r para ele continuar sendo deste tipo. Os blocos que vieram junto servem para isso.",
                           "",
                           "&eDepois de chocar:&r alimente o filhote com &fcarne&r. Quando ele crescer, coloque a &fsela&r e monte."],
                tarefas=[c.t_check(f"Escolher o {nome}")],
                recompensas=[c.r_item(ovo_dragao(raca)), c.r_item(bloco, 8), c.r_item("minecraft:saddle"),
                             c.r_item("minecraft:cooked_beef", 32)])

    c.quest("primeiro_voo", "Primeiro Voo", 0, 17.5, icone="minecraft:saddle",
            deps=[k for k, *_ in ovos], dependency_requirement="one_completed",
            forma="gear", tamanho=1.5,
            descricao=[f"{M}: \"Quando ele crescer, suba e voe. Não existe sensação igual.\"",
                       "",
                       "&eControles do dragão:&r use as teclas de pular e agachar para subir e descer. Os controles de voo ficam em &eOpções > Controles&r, na seção do Dragon Mounts.",
                       "",
                       "Marque esta missão quando fizer o primeiro voo."],
            tarefas=[c.t_check("Voei no meu dragão!")],
            recompensas=[c.r_item("minecraft:golden_apple", 3), c.r_item("minecraft:cooked_beef", 32), c.r_xp(10)])

    return {
        "id": qid("capitulo/ato2"),
        "group": "",
        "order_index": 1,
        "filename": "ato_2_terras_selvagens",
        "title": "Ato 2: Terras Selvagens",
        "subtitle": ["Quatro frentes, quatro fragmentos"],
        "icon": "paraglider:paraglider",
        "default_quest_shape": "",
        "default_hide_dependency_lines": False,
        "quests": c.quests,
    }



# ---------------------------------------------------------------- ATO 3

def ato3():
    c = Capitulo("ato3")
    M = "&6Mestre Vellan&r"
    COORD = "&7Pegue a recompensa &festando no Nether&7: as coordenadas aparecem no chat. Aperte &eF3&7 para ver onde você está.&r"

    c.quest("portal", "Abismo e Fogo", 0, 0, forma="gear", tamanho=1.75,
            icone="minecraft:obsidian", deps=["@ato2/relatorio"],
            subtitulo="Os fragmentos caíram no Nether",
            descricao=[
                f"{M}: \"Os últimos fragmentos atravessaram uma fenda e caíram no &cNether&r.\"",
                "",
                "&o\"Lá embaixo, três criaturas forjadas no fogo guardam cada uma um pedaço do Selo. E o calor dos fragmentos está acordando algo que deveria continuar dormindo...\"",
                "",
                "Construa um portal (obsidiana 4x5) e entre no Nether.",
                "",
                "&7Dica: use alguma peça de ouro na armadura. Os piglins não atacam quem usa ouro.&r",
                "",
                "&7Pegue a recompensa já dentro do Nether: ela mostra no chat as coordenadas da fortaleza mais próxima.&r",
            ],
            tarefas=[c.t_dimensao("minecraft:the_nether", "Entrar no Nether")],
            recompensas=[c.r_item(pocao("minecraft:long_fire_resistance"), 3), c.r_item("minecraft:golden_helmet"),
                         c.r_xp(5), c.r_localizar("betterfortresses:fortress", "Coordenadas de uma fortaleza")])

    # ---- Apoio (em cima)
    c.quest("fortaleza", "A Fortaleza Negra", -3, -3, icone="minecraft:nether_bricks", deps=["portal"],
            descricao=["As fortalezas do Nether são cheias de blazes e esqueletos wither.",
                       "Encontre uma. Você vai precisar voltar lá para o chefe final deste ato."],
            tarefas=[c.t_estrutura("betterfortresses:fortress", "Encontrar uma fortaleza do Nether")],
            recompensas=[c.r_xp(4), c.r_item(pocao("minecraft:healing"), 3)])

    c.quest("blaze", "Varas de Blaze", -6, -3, icone="minecraft:blaze_rod", deps=["fortaleza"],
            descricao=["Derrote blazes e junte &f8 varas de blaze&r.",
                       "&7Guarde algumas: elas vão ser importantes no fim da jornada.&r"],
            tarefas=[c.t_item("minecraft:blaze_rod", 8)],
            recompensas=[c.r_xp(5), c.r_item("minecraft:ender_pearl", 4)])

    c.quest("netherita", "Metal das Profundezas", 3, -3, icone="minecraft:netherite_ingot", deps=["portal"],
            optional=True,
            descricao=["&7Missão extra.&r Os &fdetritos antigos&r ficam escondidos no fundo do Nether. Faça um &flingote de netherita&r."],
            tarefas=[c.t_item("minecraft:netherite_ingot")],
            recompensas=[c.r_xp(8), c.r_item("minecraft:netherite_upgrade_smithing_template")])

    # ---- Frente A: Forja das Almas (Monstruosidade de Netherita)
    c.quest("forja", "A Forja das Almas", -4, 3, icone="minecraft:soul_lantern", deps=["portal"],
            subtitulo="Primeira frente",
            descricao=[f"{M}: \"Existe uma forja antiga, movida a almas, onde um colosso de netherita dorme dentro da lava. O fragmento caiu na fornalha dele.\"",
                       "", COORD],
            tarefas=[c.t_check("Pedir a localização da Forja")],
            recompensas=[c.r_localizar("cataclysm:soul_black_smith", "Coordenadas da Forja das Almas")])

    c.quest("forja_achar", "Chegando na Forja", -7, 3, icone="minecraft:soul_campfire", deps=["forja"],
            descricao=["Vá até as coordenadas e encontre a &fForja das Almas&r."],
            tarefas=[c.t_estrutura("cataclysm:soul_black_smith", "Encontrar a Forja das Almas")],
            recompensas=[c.r_xp(4), c.r_item(pocao("minecraft:strength"), 2)])

    c.quest("monstruosidade", "Chefe: Monstruosidade de Netherita", -10, 3, icone="minecraft:netherite_block",
            deps=["forja_achar"], forma="octagon", tamanho=1.5,
            descricao=["A &cMonstruosidade de Netherita&r acorda quando você chega perto.",
                       "", "&7Dica: ela é lenta, mas cada golpe é devastador. Fique fora do alcance dos socos e cuidado com as bombas de lava.&r"],
            tarefas=[c.t_matar("cataclysm:netherite_monstrosity", 1, "Derrotar a Monstruosidade de Netherita")],
            recompensas=[c.r_item(fragmento(3, 1, 4)), c.r_skill("epicfight:endurance"), c.r_xp(12),
                         c.r_item("minecraft:diamond", 4)])

    # ---- Frente B: Arena Ardente (Ignis)
    c.quest("arena", "A Arena Ardente", 4, 3, icone="minecraft:magma_block", deps=["portal"],
            subtitulo="Segunda frente",
            descricao=[f"{M}: \"Um campeão de fogo chamado &6Ignis&r guarda uma arena nos desertos do Nether. Ele só aparece para quem acende o &fAltar de Fogo&r.\"",
                       "", COORD],
            tarefas=[c.t_check("Pedir a localização da Arena")],
            recompensas=[c.r_localizar("cataclysm:burning_arena", "Coordenadas da Arena Ardente")])

    c.quest("arena_achar", "Chegando na Arena", 7, 3, icone="minecraft:blackstone", deps=["arena"],
            descricao=["Vá até as coordenadas e encontre a &fArena Ardente&r."],
            tarefas=[c.t_estrutura("cataclysm:burning_arena", "Encontrar a Arena Ardente")],
            recompensas=[c.r_xp(4)])

    c.quest("cinzas", "Cinzas Flamejantes", 10, 3, icone="cataclysm:burning_ashes", deps=["arena_achar"],
            descricao=[f"{M} &7(por carta)&r: \"Mandei as &fCinzas Flamejantes&r. Use-as no &fAltar de Fogo&r, no centro da arena, para chamar Ignis.\"",
                       "", "&7Equipamento recomendado: diamante encantado ou netherita. Leve muitas poções de resistência ao fogo.&r"],
            tarefas=[c.t_check("Receber as Cinzas Flamejantes")],
            recompensas=[c.r_item("cataclysm:burning_ashes"), c.r_item(pocao("minecraft:long_fire_resistance"), 2),
                         c.r_item(pocao("minecraft:strong_healing"), 3)])

    c.quest("ignis", "Chefe: Ignis", 13, 3, icone="cataclysm:burning_ashes",
            deps=["cinzas"], forma="octagon", tamanho=1.5,
            descricao=["Use as Cinzas Flamejantes no Altar de Fogo e derrote &cIgnis, o Campeão do Nether&r.",
                       "", "&7Dica: ele tem três fases e fica mais rápido em cada uma. Na última, o escudo dele quebra: é a hora de atacar.&r"],
            tarefas=[c.t_matar("cataclysm:ignis", 1, "Derrotar Ignis")],
            recompensas=[c.r_item(fragmento(3, 2, 4)), c.r_skill("epicfight:berserker"), c.r_xp(12),
                         c.r_item("minecraft:diamond", 4)])

    c.quest("cinzas_extra", "Mais Cinzas", 13, 5, icone="cataclysm:burning_ashes",
            deps=["cinzas"], forma="circle", tamanho=0.75, optional=True, can_repeat=True,
            descricao=["Perdeu a luta? Troque &f8 cremes de magma&r por outras Cinzas Flamejantes."],
            tarefas=[c.t_item("minecraft:magma_cream", 8, consumir=True)],
            recompensas=[c.r_item("cataclysm:burning_ashes")])

    # ---- Frente C: Manopla do Nether
    c.quest("manopla", "A Mão de Ferro", 0, 5, icone="minecraft:iron_bars", deps=["portal"],
            subtitulo="Terceira frente",
            descricao=[f"{M}: \"Os piglins falam de uma &fmão gigante de metal&r que flutua numa arena e esmaga quem entra. Ela agarrou um fragmento quando ele caiu.\"",
                       "", COORD],
            tarefas=[c.t_check("Pedir a localização da Arena da Manopla")],
            recompensas=[c.r_localizar("bosses_of_mass_destruction:gauntlet_arena", "Coordenadas da Arena da Manopla")])

    c.quest("manopla_achar", "A Arena da Manopla", 0, 7.5, icone="minecraft:chiseled_polished_blackstone", deps=["manopla"],
            descricao=["Vá até as coordenadas e encontre a &fArena da Manopla&r."],
            tarefas=[c.t_estrutura("bosses_of_mass_destruction:gauntlet_arena", "Encontrar a Arena da Manopla")],
            recompensas=[c.r_xp(4)])

    c.quest("gauntlet", "Chefe: Manopla do Nether", 0, 10, icone="minecraft:iron_block",
            deps=["manopla_achar"], forma="octagon", tamanho=1.5,
            descricao=["Derrote a &cManopla do Nether&r.",
                       "", "&7Dica: quando o olho vermelho dela brilhar, ela vai disparar um laser. Saia da linha de visão atrás de um pilar.&r"],
            tarefas=[c.t_matar("bosses_of_mass_destruction:gauntlet", 1, "Derrotar a Manopla do Nether")],
            recompensas=[c.r_item(fragmento(3, 3, 4)), c.r_skill("epicfight:emergency_escape"), c.r_xp(12),
                         c.r_item("minecraft:diamond", 4)])

    # ---- Chefe final: Wither
    c.quest("despertar", "O Que Despertou", 0, 13, icone="minecraft:wither_skeleton_skull",
            deps=["monstruosidade", "ignis", "gauntlet", "fortaleza"],
            subtitulo="O mal antigo",
            descricao=[f"{M}: \"Eu estava errado. O fragmento mais forte não caiu em uma criatura... caiu nos ossos dos &8esqueletos wither&r.\"",
                       "",
                       "&o\"Se juntarmos três crânios e o fragmento, o &8Wither&o desperta. É perigoso, mas é a única forma de arrancar o último pedaço do Selo do Nether.\"",
                       "",
                       "Junte &f3 crânios de esqueleto wither&r (das fortalezas) e &f4 areias das almas&r."],
            tarefas=[c.t_item("minecraft:wither_skeleton_skull", 3, titulo="3 crânios de esqueleto wither"),
                     c.t_item("minecraft:soul_sand", 4, titulo="4 areias das almas")],
            recompensas=[c.r_item(pocao("minecraft:strong_healing"), 4), c.r_item(pocao("minecraft:strong_strength"), 2),
                         c.r_item("minecraft:golden_apple", 4)])

    c.quest("wither", "Chefe: O Wither", 0, 16, icone="minecraft:nether_star",
            deps=["despertar"], forma="octagon", tamanho=2.0,
            descricao=["Monte o &8Wither&r (4 areias das almas em T e os 3 crânios em cima) e derrote-o.",
                       "",
                       "&cImportante:&r invoque longe da sua base! Ele destrói tudo em volta.",
                       "&7Dica: invoque no subsolo, num túnel apertado, para ele não fugir voando. Quando a vida dele cair pela metade, ele fica imune a flechas.&r"],
            tarefas=[c.t_matar("minecraft:wither", 1, "Derrotar o Wither")],
            recompensas=[c.r_item(fragmento(3, 4, 4)), c.r_skill("epicfight:death_harvest"), c.r_xp(20),
                         c.r_item("minecraft:diamond", 6)])

    c.quest("relatorio", "Relatório: Abismo e Fogo", 0, 19.5, icone="minecraft:amethyst_shard",
            deps=["wither"], forma="gear", tamanho=2.0,
            subtitulo="Fim do Ato 3",
            descricao=[f"{M}: \"Onze fragmentos. O Selo está quase completo... e mesmo assim ele continua pulsando.\"",
                       "",
                       "&o\"Quando o Wither caiu, os fragmentos brilharam e apontaram para cima. Para o céu. Existem dois mundos acima das nuvens, o &bEverbright&o e o &6Everdawn&o, onde os guardiões originais criaram o Selo.\"",
                       "",
                       "&o\"Lá estão as respostas. E, eu temo, os guardiões que nunca morreram.\"",
                       "",
                       "&dFim do Ato 3. O Ato 4 &7(Além do Céu)&d chega em breve.&r"],
            tarefas=[c.t_check("Entregar o relatório")],
            recompensas=[c.r_item("minecraft:netherite_ingot"), c.r_item("minecraft:diamond", 8),
                         c.r_item("minecraft:enchanted_golden_apple"), c.r_xp(25)])

    return {
        "id": qid("capitulo/ato3"),
        "group": "",
        "order_index": 2,
        "filename": "ato_3_abismo_e_fogo",
        "title": "Ato 3: Abismo e Fogo",
        "subtitle": ["Os fragmentos do Nether"],
        "icon": "minecraft:blaze_powder",
        "default_quest_shape": "",
        "default_hide_dependency_lines": False,
        "quests": c.quests,
    }



# ---------------------------------------------------------------- ATO 4

def ato4():
    c = Capitulo("ato4")
    M = "&6Mestre Vellan&r"
    EB, ED = "blue_skies:everbright", "blue_skies:everdawn"

    def coord(mundo):
        return f"&7Pegue a recompensa &festando no {mundo}&7: as coordenadas aparecem no chat.&r"

    def masmorra(chave, x, y, deps, titulo, mundo, dim, estrutura, chave_item, nome_chave,
                 boss_chave, boss_nome, boss_id, historia, dica, frag, skill, icone_boss):
        c.quest(chave, titulo, x, y, icone="minecraft:compass", deps=deps,
                descricao=[historia, "", coord(mundo)],
                tarefas=[c.t_check("Pedir a localização da masmorra")],
                recompensas=[c.r_localizar(estrutura, f"Coordenadas: {titulo}", dimensao=dim),
                             c.r_item(pocao("minecraft:healing"), 3)])
        c.quest(chave + "_achar", "Entrar na masmorra", x + 3, y, icone="minecraft:mossy_stone_bricks",
                deps=[chave],
                descricao=["Vá até as coordenadas e entre na masmorra.",
                           "&7Masmorras têm armadilhas e monstros. Leve tochas e comida.&r"],
                tarefas=[c.t_estrutura(estrutura, "Entrar na masmorra")],
                recompensas=[c.r_xp(5)])
        c.quest(chave + "_chave", nome_chave, x + 6, y, icone=chave_item, deps=[chave + "_achar"],
                descricao=["A sala do chefe fica trancada. Explore a masmorra e encontre a &fchave&r em um dos baús.",
                           "Depois, use a chave na &fpedra-chave&r da porta do chefe."],
                tarefas=[c.t_item(chave_item, titulo=f"Encontrar a {nome_chave}")],
                recompensas=[c.r_xp(5)])
        c.quest(boss_chave, f"Chefe: {boss_nome}", x + 9, y, icone=icone_boss, deps=[chave + "_chave"],
                forma="octagon", tamanho=1.5,
                descricao=[f"Derrote &c{boss_nome}&r.", "", dica],
                tarefas=[c.t_matar(boss_id, 1, f"Derrotar {boss_nome}")],
                recompensas=[c.r_item(fragmento(4, frag, 4)), c.r_skill(skill), c.r_xp(15),
                             c.r_item("minecraft:diamond", 5)])

    c.quest("ceu", "Além do Céu", 0, 0, forma="gear", tamanho=1.75,
            icone="blue_skies:zeal_lighter", deps=["@ato3/relatorio"],
            subtitulo="Os mundos acima das nuvens",
            descricao=[
                f"{M}: \"Encontrei nos arquivos mais antigos da Ordem: os guardiões do Selo não morreram. Eles se refugiaram em dois mundos acima das nuvens.\"",
                "",
                "&o\"O &bEverbright&o, de luz e gelo eterno, e o &6Everdawn&o, onde o sol nunca termina de nascer. Mas algo aconteceu com eles: os fragmentos que caíram por lá os enlouqueceram.\"",
                "",
                "&o\"Existe um &fGuardião do Portal&o que vive em uma casa no nosso mundo e sabe abrir o caminho. Leve este &fIsqueiro Zeal&o e os tijolos que separei.\"",
            ],
            tarefas=[c.t_check("Partir para além do céu")],
            recompensas=[c.r_mapa("casa_do_guardiao", "Mapa: Casa do Guardião do Portal"),
                         c.r_item("blue_skies:zeal_lighter"), c.r_item("blue_skies:turquoise_stonebrick", 16),
                         c.r_item("blue_skies:lunar_stonebrick", 16), c.r_xp(5)])

    c.quest("casa", "A Casa do Guardião", 3, 0, icone="minecraft:oak_door", deps=["ceu"],
            descricao=["Siga o mapa até a &fcasa do Guardião do Portal&r. Ela fica perto de vilas das planícies, em savanas, montanhas ou terras nevadas.",
                       "",
                       "&eComo abrir os portais:&r monte uma moldura do mesmo formato do portal do Nether (4 de largura por 5 de altura) e acenda com o &fIsqueiro Zeal&r (clique direito dentro da moldura).",
                       "• Moldura de &bTijolo de Pedra Turquesa&r: leva ao &bEverbright&r.",
                       "• Moldura de &fTijolo de Pedra Lunar&r: leva ao &6Everdawn&r.",
                       "",
                       "O Mestre mandou 16 tijolos de cada tipo, o suficiente para os dois portais."],
            tarefas=[c.t_estrutura("#terras_partidas:casa_do_guardiao", "Encontrar a casa do Guardião")],
            recompensas=[c.r_xp(5), c.r_item("minecraft:cooked_beef", 16)])

    c.quest("everbright", "Everbright", 6, -3, icone="minecraft:packed_ice", deps=["casa"],
            subtitulo="O mundo da luz e do gelo",
            descricao=["Atravesse o portal do &bEverbright&r.",
                       "", "&7Os minérios e madeiras daqui são diferentes. As ferramentas feitas com eles funcionam melhor neste mundo.&r"],
            tarefas=[c.t_dimensao(EB, "Entrar no Everbright")],
            recompensas=[c.r_xp(5), c.r_item(pocao("minecraft:long_night_vision"), 2)])

    c.quest("everdawn", "Everdawn", 6, 3, icone="minecraft:orange_terracotta", deps=["casa"],
            subtitulo="O mundo do amanhecer eterno",
            descricao=["Atravesse o portal do &6Everdawn&r.",
                       "", "&7Os minérios e madeiras daqui são diferentes. As ferramentas feitas com eles funcionam melhor neste mundo.&r"],
            tarefas=[c.t_dimensao(ED, "Entrar no Everdawn")],
            recompensas=[c.r_xp(5), c.r_item(pocao("minecraft:long_fire_resistance"), 2)])

    # ---- Everbright
    masmorra("eb_ofuscante", 9, -3, ["everbright"], "Masmorra Ofuscante do Everbright", "Everbright", EB,
             "blue_skies:everbright_blinding_dungeon", "blue_skies:blinding_key", "Chave Ofuscante",
             "summoner", "Summoner", "blue_skies:summoner",
             f"{M}: \"O primeiro guardião, o &fInvocador&r, se trancou numa masmorra de luz cegante. Ele chama criaturas para lutar por ele.\"",
             "&7Dica: ele invoca ajudantes sem parar. Derrube os ajudantes rápido e ataque o Summoner entre uma invocação e outra.&r",
             1, "epicfight:revelation", "minecraft:totem_of_undying")
    masmorra("eb_natureza", 9, -6, ["summoner"], "Masmorra da Natureza", "Everbright", EB,
             "blue_skies:nature_dungeon", "blue_skies:nature_key", "Chave da Natureza",
             "starlit_crusher", "Starlit Crusher", "blue_skies:starlit_crusher",
             f"{M}: \"O segundo guardião do Everbright virou uma árvore viva gigante, o &fEsmagador Estelar&r. Ele vive numa masmorra coberta de mato, nos pinheiros nevados.\"",
             "&7Dica: ele é lento mas bate muito forte. Fique sempre se movendo e ataque pelas costas.&r",
             2, "epicfight:forbidden_strength", "minecraft:oak_sapling")

    # ---- Everdawn
    masmorra("ed_ofuscante", 9, 3, ["everdawn"], "Masmorra Ofuscante do Everdawn", "Everdawn", ED,
             "blue_skies:everdawn_blinding_dungeon", "blue_skies:blinding_key", "Chave Ofuscante",
             "alchemist", "Alchemist", "blue_skies:alchemist",
             f"{M}: \"No Everdawn, o guardião &fAlquimista&r passou séculos fazendo poções com o poder do fragmento. Ele não é mais humano.\"",
             "&7Dica: ele joga poções que mudam o chão da arena. Leve leite para tirar efeitos ruins.&r",
             3, "epicfight:adaptive_skin", "minecraft:brewing_stand")
    masmorra("ed_veneno", 9, 6, ["alchemist"], "Masmorra do Veneno", "Everdawn", ED,
             "blue_skies:poison_dungeon", "blue_skies:poison_key", "Chave do Veneno",
             "arachnarch", "Arachnarch", "blue_skies:arachnarch",
             f"{M}: \"O último guardião do Everdawn virou uma aranha gigante, a &fArachnarch&r. Ela fez um ninho numa masmorra venenosa na floresta de bordos.\"",
             "&7Dica: leve muito leite e poções de cura. O veneno dela é o perigo maior, não as mordidas.&r",
             4, "epicfight:vengeance", "minecraft:spider_eye")

    c.quest("relatorio", "Relatório: Além do Céu", 21, 0, icone="minecraft:amethyst_shard",
            deps=["starlit_crusher", "arachnarch"], forma="gear", tamanho=2.0,
            subtitulo="Fim do Ato 4",
            descricao=[f"{M}: \"Quinze fragmentos. Os guardiões caídos agora descansam.\"",
                       "",
                       "&o\"Antes de morrer, o Alquimista sussurrou algo: o Selo só pode ser refeito onde foi quebrado. No &5Fim&o do mundo, onde o Dragão guarda o vazio.\"",
                       "",
                       "&o\"Use os olhos do Ender para achar a fortaleza escondida. A última batalha nos espera.\"",
                       "",
                       "&dFim do Ato 4. O Ato 5 &7(O Fim do Selo)&d chega em breve.&r"],
            tarefas=[c.t_check("Entregar o relatório")],
            recompensas=[c.r_item("minecraft:ender_eye", 12), c.r_item("minecraft:diamond", 10),
                         c.r_item("minecraft:enchanted_golden_apple", 2), c.r_xp(30)])

    return {
        "id": qid("capitulo/ato4"),
        "group": "",
        "order_index": 3,
        "filename": "ato_4_alem_do_ceu",
        "title": "Ato 4: Além do Céu",
        "subtitle": ["Os guardiões caídos"],
        "icon": "blue_skies:zeal_lighter",
        "default_quest_shape": "",
        "default_hide_dependency_lines": False,
        "quests": c.quests,
    }


# ---------------------------------------------------------------- arquivos

def escrever(caminho, dados):
    caminho = os.path.join(RAIZ, caminho)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(snbt(dados) + "\n")
    print("escrito:", os.path.relpath(caminho))


def main():
    escrever("data.snbt", {
        "version": 13,
        "default_reward_team": False,
        "default_consume_items": False,
        "default_autoclaim_rewards": "disabled",
        "default_quest_shape": "circle",
        "default_quest_disable_jei": False,
        "emergency_items_cooldown": 300,
        "drop_loot_crates": False,
        "loot_crate_no_drop": {"passive": 4000, "monster": 600, "boss": 0},
        "disable_gui": False,
        "grid_scale": 0.5,
        "pause_game": False,
        "lock_message": "",
        "progression_mode": "linear",
        "detection_delay": 20,
        "drop_book_on_death": False,
        "title": "Terras Partidas",
        "icon": "minecraft:amethyst_shard",
    })
    escrever("chapter_groups.snbt", {"chapter_groups": []})
    for capitulo in (ato1(), ato2(), ato3(), ato4()):
        escrever(f"chapters/{capitulo['filename']}.snbt", capitulo)


if __name__ == "__main__":
    main()

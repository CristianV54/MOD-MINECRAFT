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


def fragmento(numero):
    return item("minecraft:amethyst_shard", tag={
        **nome_lore(f"Fragmento do Selo ({numero}/3)", "light_purple",
                    ["Um pedaço do cristal que prendia o mal antigo.",
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
            q["dependencies"] = [qid(f"{self.chave}/quest/{d}") for d in deps]
        q.update(extra)
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
                       "", "&7Se morrer, a isca é gasta. Volte aqui: a missão &e\"Mais uma Isca\"&7 dá outra."],
            tarefas=[c.t_matar("meetyourfight:swampjaw", 1, "Derrotar Swampjaw")],
            recompensas=[c.r_item(fragmento(1)), c.r_xp(5), c.r_item("minecraft:diamond", 1)])

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
            recompensas=[c.r_item(fragmento(2)), c.r_xp(7), c.r_item("minecraft:diamond", 2)])

    c.quest("sino_extra", "Outro Sino", 20, 2, icone="meetyourfight:haunted_bell",
            deps=["sino"], forma="circle", tamanho=0.75, optional=True, can_repeat=True,
            descricao=["Perdeu a luta? Troque &f4 lingotes de ouro&r por outro Sino Assombrado."],
            tarefas=[c.t_item("minecraft:gold_ingot", 4, consumir=True)],
            recompensas=[c.r_item("meetyourfight:haunted_bell")])

    # ---- Chefe 3: Ferrous Wroughtnaut
    c.quest("camara", "A Câmara Forjada", 17.5, -3.5, icone="mowziesmobs:wrought_helmet",
            deps=["vila", "swampjaw"],
            subtitulo="Terceiro fragmento",
            descricao=[f"{M}: \"Os aldeões falam de um &fcavaleiro de metal&r que guarda uma câmara escondida. Nunca saiu de lá, nunca dormiu... e agora carrega um fragmento do Selo.\"",
                       "", "Encontre a &fCâmara Forjada&r. Ela fica escondida em cavernas e encostas de montanha: procure uma porta de pedra com tochas.",
                       "", "&7Dica: os mapas do Xaero ajudam a marcar o caminho (tecla &eY&7 para criar um ponto).&r"],
            tarefas=[c.t_estrutura("mowziesmobs:wrought_chamber", "Encontrar a Câmara Forjada")],
            recompensas=[c.r_xp(3), c.r_item(pocao("minecraft:strength"), 2)])

    c.quest("wroughtnaut", "Chefe: Cavaleiro Forjado", 20, -3.5, icone="mowziesmobs:wrought_axe",
            deps=["camara"], forma="octagon", tamanho=1.5,
            descricao=["Derrote o &cCavaleiro de Ferro Forjado&r (Ferrous Wroughtnaut).",
                       "", "&7Dica: a armadura dele é quase indestrutível pela frente. Espere ele errar um golpe, fique atrás dele e ataque as costas.&r"],
            tarefas=[c.t_matar("mowziesmobs:ferrous_wroughtnaut", 1, "Derrotar o Cavaleiro Forjado")],
            recompensas=[c.r_item(fragmento(3)), c.r_xp(7), c.r_item("minecraft:diamond", 2)])

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
    capitulo = ato1()
    escrever(f"chapters/{capitulo['filename']}.snbt", capitulo)


if __name__ == "__main__":
    main()

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


def snbt_mc(valor, nivel=0):
    """SNBT no formato padrão do Minecraft (com vírgulas), usado pelo Easy NPC."""
    tab = "  " * nivel
    if isinstance(valor, dict):
        if not valor:
            return "{}"
        itens = [f"{tab}  {k}:{snbt_mc(v, nivel + 1)}" for k, v in valor.items()]
        return "{\n" + ",\n".join(itens) + f"\n{tab}}}"
    if isinstance(valor, list):
        if not valor:
            return "[]"
        itens = [f"{tab}  {snbt_mc(v, nivel + 1)}" for v in valor]
        return "[\n" + ",\n".join(itens) + f"\n{tab}]"
    if isinstance(valor, bool):
        return "1b" if valor else "0b"
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


def livro_de_feiticos(feiticos, livro="irons_spellbooks:copper_spell_book", espacos=5):
    """Livro do Iron's Spells com feitiços já gravados (não se gastam: usam mana)."""
    return item(livro, tag={"ISB_Spells": {
        "data": [{"id": f, "index": i, "level": n, "locked": Raw("0b")} for i, (f, n) in enumerate(feiticos)],
        "maxSpells": espacos, "mustEquip": Raw("1b"), "spellWheel": Raw("1b")}})


def encantado(id_, encantamentos):
    return item(id_, tag={"Enchantments": [{"id": e, "lvl": Raw(f"{n}s")} for e, n in encantamentos]})


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

    def r_comando(self, comando, titulo=None, icone=None, auto=False):
        r = {"id": self._id("r"), "type": "command", "command": comando,
             "elevate_perms": True, "silent": True}
        if auto:
            r["auto"] = "enabled"   # dispara sozinha quando a missão completa
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

    def r_skill(self, skill, titulo=None):
        r = self.r_item(livro_skill(skill))
        if titulo:
            r["title"] = titulo
        return r

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


# ---------------------------------------------------------------- KITS DE CLASSE

PASTA_FUNCOES = os.path.join(RAIZ, "..", "..", "openloader", "data", "terras_partidas", "data", "terras_partidas", "functions")


def _item_para_comando(it):
    """Converte um item do gerador para o formato do /give (id + NBT)."""
    if isinstance(it, str):
        return it
    tag = it.get("tag")
    return it["id"] + (" ".join(l.strip() for l in snbt_mc(tag).splitlines()) if tag else "")


def escrever_kit(chave, nome, recompensas):
    """Gera terras_partidas:kit/<classe>: entrega o kit uma única vez por jogador."""
    import re as _re
    linhas = [f"# Kit da classe {_re.sub(r'&[0-9a-fk-or]', '', nome)}. Gerado por tools/gerar_missoes.py.",
              "tag @s add tp_kit_recebido"]
    for r in recompensas:
        if r.get("type") != "item":
            continue
        it, n = r["item"], r.get("count", 1)
        n = int(str(n).rstrip("L")) if not isinstance(n, int) else n
        cmd = _item_para_comando(it)
        idd = it if isinstance(it, str) else it["id"]
        if idd.endswith("_spell_book"):
            # direto no espaço do livro (Curios); se não der, vai para o inventário
            linhas.append(f"execute store success score @s tp_espera run curios replace spellbook 0 @s with {cmd}")
            linhas.append(f"execute unless score @s tp_espera matches 1 run give @s {cmd}")
            linhas.append("scoreboard players set @s tp_espera 0")
        else:
            linhas.append(f"give @s {cmd} {n}")
    linhas += ["playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1",
               'tellraw @s ["",{"text":"[Mestre Vellan] ","color":"gold"},{"text":"Seu kit de classe está no seu inventário.","color":"white"}]']
    if chave == "mago":
        linhas.append('tellraw @s ["",{"text":"[Mestre Vellan] ","color":"gold"},{"text":"Seu livro de feitiços já está equipado. Aperte ","color":"white"},{"text":"V","color":"yellow"},{"text":" para lançar e ","color":"white"},{"text":"Z","color":"yellow"},{"text":" para trocar de feitiço. Eles não acabam: só gastam mana.","color":"white"}]')
    os.makedirs(os.path.join(PASTA_FUNCOES, "kit"), exist_ok=True)
    with open(os.path.join(PASTA_FUNCOES, "kit", f"{chave}_dar.mcfunction"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    with open(os.path.join(PASTA_FUNCOES, "kit", f"{chave}.mcfunction"), "w", encoding="utf-8") as f:
        f.write(f"# Entrega o kit só uma vez (a missão e o Mestre Vellan chamam esta mesma função).\n"
                f"execute unless entity @s[tag=tp_kit_recebido] run function terras_partidas:kit/{chave}_dar\n")


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
                "• Clique em uma missão para ver os detalhes e concluir a tarefa.",
                "• Depois de concluída, pegue a recompensa.",
                "• Missões novas aparecem conforme você avança.",
                "",
                "&eCombate:&r este mundo usa o &cEpic Fight&r. Aperte &eR&r para alternar entre o modo normal e o modo de combate.",
                "As outras teclas ficam em &eOpções > Controles&r, na seção do Epic Fight.",
                "",
                "&eOutras teclas:&r &eK&r árvores de habilidades, &eJ&r movimentos do Epic Fight, &eV&r lança o feitiço escolhido, &eZ&r roda de feitiços (ou &eCtrl&r + rolar o mouse).",
                "&eOrganizar o inventário:&r use os botões ao lado do inventário e dos baús, ou aperte &eR&r com o inventário aberto.",
                "{@pagebreak}",
                "&eO Mestre Vellan:&r ele aparece &fna sua frente&r assim que você entra no mundo pela primeira vez.",
                "Clique nele com o botão direito para conversar e escolher sua classe. Ele também comenta cada etapa da história e dá dicas.",
                "&7Se você mudar de base, a missão \"Chamar o Mestre\" traz ele até você.&r",
            ],
            tarefas=[c.t_check("Li a carta do Mestre")],
            recompensas=[c.r_item("minecraft:bread", 8), c.r_item("minecraft:torch", 16),
                         c.r_skill("epicfight:roll", titulo="Livro de habilidade: Rolar (use com o botão direito para aprender o movimento)")])

    c.quest("chamar_mestre", "Chamar o Mestre", 0, 2.5, icone="minecraft:bell", deps=["chamado"],
            forma="circle", tamanho=0.75, optional=True, can_repeat=True,
            descricao=["Mudou de base ou perdeu o Mestre Vellan de vista?",
                       "Pegue a recompensa e ele aparece ao seu lado. Se ele estiver por perto, ele só muda de lugar."],
            tarefas=[c.t_check("Chamar o Mestre Vellan")],
            recompensas=[c.r_comando("/function terras_partidas:rechamar_vellan", titulo="Chamar o Mestre Vellan",
                                     icone="minecraft:bell")])

    c.quest("mais_forte", "Como Ficar Mais Forte", 0, -2.5, icone="minecraft:shield", deps=["chamado"],
            forma="circle", subtitulo="Leia se os monstros estão difíceis",
            descricao=[f"{M}: \"Os monstros daqui não são os de antigamente. Força bruta não basta: você precisa lutar do jeito certo.\"",
                       "",
                       "&e1. Modo de combate (tecla R)&r",
                       "Sem ele você bate como no Minecraft normal e não consegue esquivar. &cLute sempre no modo de combate.&r",
                       "• &eAlt esquerdo&r: esquiva (rolamento). Passe por dentro do golpe do inimigo.",
                       "• &eBotão direito&r: defende com a arma ou o escudo.",
                       "• Esquivar e defender gastam a &ebarra de fôlego&r. Não fique batendo sem parar: espere o inimigo errar e contra-ataque.",
                       "{@pagebreak}",
                       "&e2. Árvores de habilidades (tecla K)&r",
                       "Todo mundo tem três árvores, que sobem sozinhas enquanto você joga:",
                       "• &cCombate&r: sobe matando monstros (dano, crítico, roubo de vida).",
                       "• &7Mineração&r: sobe minerando (velocidade, alcance, sorte).",
                       "• &aVida&r: sobe comendo e levando dano (corações, armadura, velocidade).",
                       "Cada nível dá &e1 ponto&r. Abra o K de vez em quando e gaste os pontos!",
                       "A árvore da sua &eclasse&r ganha pontos matando monstros e derrotando chefes.",
                       "{@pagebreak}",
                       "&e3. Equipamento&r",
                       "• Escolha a classe: o &ekit&r vai direto para o inventário e já traz armadura e arma boas para o começo.",
                       "• Faça armadura de ferro assim que puder. Ela faz mais diferença que a arma.",
                       "",
                       "&e4. Cuidado com&r",
                       "• Monstros que &6brilham&r ou têm &6nome colorido&r: são versões de elite. Fuja deles no começo.",
                       "• A noite: os monstros mais fortes aparecem no escuro. Durma numa cama.",
                       "• Vida só se recupera com a &efome cheia&r: ande sempre com comida.",
                       "",
                       "&7Pegue a recompensa: 1 ponto extra nas árvores de Combate e Vida, e um escudo.&r"],
            tarefas=[c.t_check("Entendi")],
            recompensas=[c.r_item("minecraft:shield"), c.r_item("minecraft:cooked_beef", 12),
                         c.r_comando("/puffish_skills points add {p} terras_partidas:combate 1",
                                     titulo="+1 ponto na árvore de Combate", icone="minecraft:iron_sword"),
                         c.r_comando("/puffish_skills points add {p} terras_partidas:vida 1",
                                     titulo="+1 ponto na árvore de Vida", icone="minecraft:golden_apple")])

    # ---- Escolha de classe
    c.quest("caminho", "Escolha seu Caminho", 2.5, 0, forma="hexagon", tamanho=1.25,
            icone="minecraft:compass", deps=["chamado"],
            max_completable_dependents=1,
            subtitulo="Só dá para escolher uma vez",
            descricao=[
                f"{M}: \"Todo caçador tem um estilo. Qual é o seu?\"",
                "",
                "Escolha &cuma&r das cinco missões de classe ao lado. Cada uma dá um kit inicial diferente.",
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
         [c.r_item("epicfight:iron_longsword"), c.r_item("minecraft:chainmail_helmet"),
          c.r_item("minecraft:chainmail_chestplate"), c.r_item("minecraft:chainmail_leggings"),
          c.r_item("minecraft:chainmail_boots"), c.r_item(pocao("minecraft:strength"), 2),
          c.r_item("minecraft:cooked_beef", 12)]),
        ("tanque", "&9Tanque", -1, "minecraft:shield",
         "Você aguenta pancada. Lança e escudo (dá para usar os dois juntos), armadura de ferro completa e a técnica de &eAparar&r do Epic Fight.",
         [c.r_item("minecraft:shield"), c.r_item("minecraft:iron_helmet"), c.r_item("minecraft:iron_chestplate"),
          c.r_item("minecraft:iron_leggings"), c.r_item("minecraft:iron_boots"), c.r_item("epicfight:iron_spear"),
          c.r_item(livro_skill("epicfight:parrying")), c.r_item("minecraft:cooked_beef", 12)]),
        ("assassino", "&8Assassino", 0, "epicfight:iron_dagger",
         "Você é rápido. Duas adagas (uma em cada mão), poções de velocidade e o &ePasso&r, uma esquiva mais curta e ágil.",
         [c.r_item(encantado("epicfight:iron_dagger", [("minecraft:sharpness", 1)])),
          c.r_item(encantado("epicfight:iron_dagger", [("minecraft:sharpness", 1)])),
          c.r_item("minecraft:leather_helmet"), c.r_item("minecraft:chainmail_chestplate"), c.r_item("minecraft:leather_boots"),
          c.r_item(pocao("minecraft:swiftness"), 3), c.r_item(livro_skill("epicfight:step")),
          c.r_item("minecraft:ender_pearl", 4), c.r_item("minecraft:cooked_beef", 12)]),
        ("mago", "&5Mago", 1, "irons_spellbooks:copper_spell_book",
         "Você usa magia. Seu &flivro de feitiços&r já vem com 4 feitiços gravados, que &fnão são gastos&r: cada uso só gasta mana. "
         "O livro já chega &eequipado no espaço do livro&r: aperte &eV&r para lançar o feitiço escolhido e &eZ&r para abrir a roda de feitiços. "
         "Pergaminhos avulsos somem quando usados: grave-os no livro na &eMesa de Inscrição&r para usar sempre.",
         [c.r_item(livro_de_feiticos([("irons_spellbooks:firebolt", 2), ("irons_spellbooks:magic_missile", 2),
                                      ("irons_spellbooks:icicle", 1), ("irons_spellbooks:heal", 1)])),
          c.r_item("irons_spellbooks:wandering_magician_helmet"), c.r_item("irons_spellbooks:wandering_magician_chestplate"),
          c.r_item("irons_spellbooks:wandering_magician_leggings"), c.r_item("irons_spellbooks:wandering_magician_boots"),
          c.r_item("irons_spellbooks:inscription_table"),
          c.r_item(pergaminho("irons_spellbooks:shield")), c.r_item(pergaminho("irons_spellbooks:wisp")),
          c.r_item("minecraft:cooked_beef", 12)]),
        ("cacador", "&aCaçador", 2, "minecraft:bow",
         "Você ataca de longe. Arco, muitas flechas e uma adaga para quando o inimigo chegar perto.",
         [c.r_item(encantado("minecraft:bow", [("minecraft:power", 2)])), c.r_item("minecraft:arrow", 64),
          c.r_item("minecraft:arrow", 64), c.r_item("epicfight:iron_dagger"),
          c.r_item("minecraft:leather_helmet"), c.r_item("minecraft:leather_chestplate"),
          c.r_item("minecraft:leather_leggings"), c.r_item("minecraft:leather_boots"),
          c.r_item("minecraft:cooked_beef", 12)]),
    ]
    for chave, nome, dy, icone, texto, recs in classes:
        # O kit vai direto para o inventário (função com trava contra kit duplicado). As recompensas
        # da missão são automáticas, e o botão "Escolher" do Mestre Vellan chama a mesma função.
        escrever_kit(chave, nome, recs)
        recs = [c.r_comando(f"/execute as {{p}} at @s run function terras_partidas:kit/{chave}", titulo="Kit da classe (vai direto para o inventário)",
                            icone=icone, auto=True),
                c.r_comando(f"/puffish_skills category unlock {{p}} terras_partidas:{chave}",
                            titulo="Libera a árvore de habilidades da classe", icone="minecraft:enchanted_book", auto=True),
                c.r_comando(f"/tag {{p}} add {TAG_CLASSE}", titulo="Classe escolhida", icone="minecraft:name_tag", auto=True)]
        c.quest(chave, nome, 5, dy * 1.25, icone=icone, deps=["caminho"], forma="diamond",
                descricao=[f"{M}: \"Então você é um {nome}&r.\"", "", texto, "",
                           "&eÁrvore de habilidades:&r esta classe libera uma árvore só dela. Aperte &eK&r para abrir.",
                           "Você ganha pontos matando monstros e &f+1 ponto a cada chefe&r derrotado."],
                tarefas=[c.t_check(f"Eu escolho ser {nome}")], recompensas=recs)
    nomes_classes = [k for k, *_ in classes]

    # ---- Trilha de sobrevivência (em cima)
    c.quest("ferro", "Uma Picareta de Ferro", 7.5, -2.5, icone="minecraft:iron_pickaxe",
            deps=nomes_classes, dependency_requirement="one_completed", hide_dependency_lines=True,
            descricao=[f"{M}: \"Ninguém caça de mãos vazias. Comece por uma picareta decente.\"",
                       "", "Faça uma &fpicareta de ferro&r."],
            tarefas=[c.t_item("minecraft:iron_pickaxe")],
            recompensas=[c.r_xp(3), c.r_item("minecraft:iron_ingot", 4)])

    c.quest("mochila", "Uma Mochila de Verdade", 10, -3.5, icone="sophisticatedbackpacks:backpack",
            deps=["ferro"],
            descricao=["O inventário vai encher rápido. Faça uma &fmochila&r.",
                       "Depois, você poderá melhorá-la com cobre, ferro, ouro e outros materiais."],
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
            descricao=[f"{M}: \"As vilas são pontos seguros neste mundo. Lá você troca, descansa e se prepara para a jornada.\"",
                       "", "Encontre uma &fvila&r. Muitas delas têm um &bObelisco&r (Waystone), uma pedra que te teleporta entre lugares já visitados."],
            tarefas=[c.t_estrutura("#minecraft:village", "Encontrar uma vila")],
            recompensas=[c.r_xp(3), c.r_item("minecraft:emerald", 8)])

    # ---- Trilha de combate (embaixo)
    c.quest("treino", "Treino de Combate", 7.5, 2.5, icone="minecraft:iron_sword",
            deps=nomes_classes, dependency_requirement="one_completed", hide_dependency_lines=True,
            descricao=[f"{M}: \"Antes de enfrentar algo de verdade, aprenda a lutar.\"",
                       "", "No Epic Fight, &eesquivar&r e &edefender&r gasta a barra de fôlego. Não ataque sem parar: espere a abertura do inimigo.",
                       "", "Derrote &c10 zumbis&r."],
            tarefas=[c.t_matar("minecraft:zombie", 10, "Derrotar 10 zumbis")],
            recompensas=[c.r_xp(3), c.r_item("minecraft:golden_carrot", 2)])

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
                       "", "Pegue a &fIsca Fóssil&r na recompensa, prepare-se e use-a (clique direito) perto do pântano quando estiver pronto para chamar a criatura.",
                       "", "&7Equipamento recomendado: pedra ou ferro.&r"],
            tarefas=[c.t_check("Estou pronto")],
            recompensas=[c.r_item("meetyourfight:fossil_bait"), c.r_item(pocao("minecraft:healing"), 2)])

    c.quest("swampjaw", "Chefe: Swampjaw", 15, 2.5, icone="meetyourfight:fossil_bait",
            deps=["isca"], forma="octagon", tamanho=1.5,
            descricao=["Use a Isca Fóssil e derrote &cSwampjaw&r.",
                       "", "&dRecompensa especial:&r o livro de &eAscensão Fantasma&r (pulo duplo no ar).",
                       "", "&7Se morrer, a isca é gasta. Volte aqui: a missão &e\"Mais uma Isca\"&7 dá outra."],
            tarefas=[c.t_matar("meetyourfight:swampjaw", 1, "Derrotar Swampjaw")],
            recompensas=[c.r_item(fragmento(1, 1, 3)), c.r_skill("epicfight:phantom_ascent"), c.r_xp(5),
                         c.r_item("minecraft:diamond", 1)])

    c.quest("isca_extra", "Mais uma Isca", 15, 4.5, icone="meetyourfight:fossil_bait",
            deps=["isca"], forma="circle", tamanho=0.75, optional=True,
            can_repeat=True,
            descricao=["Perdeu a luta? Troque &f8 ossos&r por outra Isca Fóssil.", "Pode repetir quantas vezes precisar."],
            tarefas=[c.t_item("minecraft:bone", 8, consumir=True, titulo="Entregar 8 ossos")],
            recompensas=[c.r_item("meetyourfight:fossil_bait")])

    # ---- Chefe 2: Bellringer
    c.quest("sino", "O Sino Assombrado", 17.5, 0, icone="meetyourfight:haunted_bell",
            deps=["swampjaw", "ferro"],
            subtitulo="Segundo fragmento",
            descricao=[f"{M}: \"Muito bem. O segundo fragmento está preso a um espírito que toca um sino nas ruínas. Cada badalada atrai a morte.\"",
                       "", "Pegue o &fSino Assombrado&r. Tocá-lo invoca o &cBellringer&r.",
                       "", "&7Equipamento recomendado: ferro ou diamante. Ele é rápido: guarde a esquiva para quando ele avançar.&r"],
            tarefas=[c.t_item("minecraft:iron_chestplate", titulo="Obter um peitoral de ferro")],
            recompensas=[c.r_item("meetyourfight:haunted_bell"), c.r_item(pocao("minecraft:healing"), 3)])

    c.quest("bellringer", "Chefe: Bellringer", 20, 0, icone="meetyourfight:haunted_bell",
            deps=["sino"], forma="octagon", tamanho=1.5,
            descricao=["Toque o &fSino Assombrado&r (clique direito com ele na mão) para chamar o &cBellringer&r e derrote-o.", "", "&7Se morrer, o sino é gasto. A missão &e\"Outro Sino\"&7 dá outro.&r"],
            tarefas=[c.t_matar("meetyourfight:bellringer", 1, "Derrotar o Bellringer")],
            recompensas=[c.r_item(fragmento(1, 2, 3)), c.r_skill("epicfight:technician"), c.r_xp(7),
                         c.r_item("minecraft:diamond", 2)])

    c.quest("sino_extra", "Outro Sino", 20, 2, icone="meetyourfight:haunted_bell",
            deps=["sino"], forma="circle", tamanho=0.75, optional=True, can_repeat=True,
            descricao=["Perdeu a luta? Troque &f4 lingotes de ouro&r por outro Sino Assombrado."],
            tarefas=[c.t_item("minecraft:gold_ingot", 4, consumir=True, titulo="Entregar 4 lingotes de ouro")],
            recompensas=[c.r_item("meetyourfight:haunted_bell")])

    # ---- Chefe 3: Ferrous Wroughtnaut
    c.quest("rumores", "Rumores na Vila", 15, -4.5, icone="minecraft:filled_map",
            deps=["vila", "swampjaw"],
            subtitulo="Terceiro fragmento",
            descricao=[f"{M}: \"Os aldeões falam de um &fcavaleiro de metal&r que guarda uma câmara no subsolo. Nunca saiu de lá, nunca dormiu... e agora carrega um fragmento do Selo.\"",
                       "", "&o\"Um minerador desenhou este mapa antes de fugir. O X marca a entrada.\"",
                       "", "&7Segure o mapa na mão para ver o caminho. O mapa pode demorar alguns segundos para aparecer.&r"],
            tarefas=[c.t_check("Obter o mapa")],
            recompensas=[c.r_mapa("camara_forjada", "Mapa: Câmara Forjada"),
                         c.r_item(pocao("minecraft:night_vision"), 2)])

    c.quest("camara", "A Câmara Forjada", 17.5, -4.5, icone="mowziesmobs:wrought_helmet",
            deps=["rumores"],
            descricao=["Siga o mapa até o &fX vermelho&r. A Câmara fica &fno subsolo&r, quase sempre entre as alturas Y=20 e Y=50: cave para baixo quando chegar no ponto.",
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
                       "&o\"Mas sinto o Selo pulsando mais forte. Os outros fragmentos foram para lugares piores: o gelo eterno, as savanas queimadas, o labirinto de gelo e a Mesa da Fortuna, onde um espírito aposta almas.",
                       "&oVocê vai precisar ir longe. Leve isto: um planador, para atravessar o mundo pelos céus.\"",
                       "",
                       "&dFim do Ato 1. O Ato 2 &7(Terras Selvagens)&d já está liberado no livro.&r"],
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
                "• &5A Mesa da Fortuna&r, onde um espírito aposta almas.",
                "",
                "&o\"Use o planador para atravessar montanhas e vales. Ele gasta fôlego, então pouse antes que a barra acabe.\"",
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

    c.quest("waystone", "Seu Próprio Obelisco", 2.5, -3, icone="waystones:waystone",
            deps=["asas"], optional=True,
            descricao=["Faça um &bObelisco&r (Waystone) e coloque perto da sua base. Assim você volta de qualquer frente em segundos."],
            tarefas=[c.t_item("waystones:waystone")],
            recompensas=[c.r_item("waystones:warp_dust", 8), c.r_xp(3)])

    # ---- Frente 1: Gelo Eterno (Frostmaw)
    c.quest("gelo", "O Gelo Eterno", 4, 2.5, icone="minecraft:snowball", deps=["asas"],
            subtitulo="Frente do Gelo",
            descricao=[f"{M}: \"Nas terras nevadas, um caçador viu uma criatura gigante dormindo ao lado de um cristal de gelo. Ele não voltou para contar o resto.\"",
                       "", "&o\"Este mapa marca onde ele foi visto pela última vez.\"",
                       "", "&7Leve armadura, comida e tochas. É uma viagem longa.&r"],
            tarefas=[c.t_check("Obter o mapa do gelo")],
            recompensas=[c.r_mapa("covil_frostmaw", "Mapa: Covil do Frostmaw"), c.r_item("minecraft:cooked_salmon", 12)])

    c.quest("covil", "O Covil Congelado", 7, 2.5, icone="minecraft:packed_ice", deps=["gelo"],
            descricao=["Siga o mapa até o &fX vermelho&r, em um bioma de neve."],
            tarefas=[c.t_estrutura("mowziesmobs:frostmaw_spawn", "Encontrar o covil do Frostmaw")],
            recompensas=[c.r_xp(3)])

    c.quest("frostmaw", "Chefe: Frostmaw", 10, 2.5, icone="mowziesmobs:ice_crystal",
            deps=["covil"], forma="octagon", tamanho=1.5,
            descricao=["O &cFrostmaw&r está dormindo. Acorde-o com um golpe e prepare-se.",
                       "", "&7Dica: ele sopra gelo em linha reta e dá saltos que esmagam. Corra para os lados e ataque depois do salto.",
                       "&7Depois da luta, procure o &fCristal de Gelo&7 perto dele: é uma arma muito poderosa.&r"],
            tarefas=[c.t_matar("mowziesmobs:frostmaw", 1, "Derrotar o Frostmaw")],
            recompensas=[c.r_item(fragmento(2, 1, 4)), c.r_skill("epicfight:hypervitality"), c.r_xp(10),
                         c.r_item("minecraft:diamond", 3)])

    # ---- Frente 2: Savanas Queimadas (Umvuthi)
    c.quest("savana", "As Savanas Queimadas", 4, 5.5, icone="minecraft:acacia_sapling", deps=["asas"],
            subtitulo="Frente da Savana",
            descricao=[f"{M}: \"Nas savanas vive a tribo dos &6Umvuthana&r, guerreiros mascarados. Eles servem a &6Umvuthi, o Pássaro do Sol&r, e agora o fragmento brilha no peito dele.\"",
                       "", "&o\"Cuidado: eles atacam em bando e usam lanças e magia de cura.\""],
            tarefas=[c.t_check("Obter o mapa da savana")],
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
            tarefas=[c.t_check("Obter o mapa do mar")],
            recompensas=[c.r_mapa("labirinto_de_gelo", "Mapa: Labirinto de Gelo"), c.r_item("minecraft:oak_boat"),
                         c.r_item(pocao("minecraft:water_breathing"), 2)])

    c.quest("labirinto", "O Labirinto de Gelo", -7, 2.5, icone="minecraft:packed_ice", deps=["mar"],
            descricao=["Siga o mapa e entre no &3Labirinto de Gelo&r: o oceano congelado profundo, cheio de icebergs e navios presos no gelo."],
            tarefas=[{"id": "", "type": "biome", "biome": "#aquamirae:ice_maze", "title": "Entrar no Labirinto de Gelo"}],
            recompensas=[c.r_xp(3)])

    c.quest("corneta", "O Chifre de Concha", -10, 2.5, icone="aquamirae:shell_horn", deps=["labirinto"],
            descricao=[f"{M} &7(por carta)&r: \"Encontrei nos arquivos da Ordem: a capitã atende ao som de um &fChifre de Concha&r. Mandei um para você.\"",
                       "", "Use o Chifre de Concha &fperto da água, dentro do Labirinto de Gelo&r, para invocar a capitã.",
                       "", "&7Ela também aparece às vezes em baús dos navios congelados.&r"],
            tarefas=[c.t_check("Obter o Chifre de Concha")],
            recompensas=[c.r_item("aquamirae:shell_horn"), c.r_item(pocao("minecraft:healing"), 3)])

    c.quest("cornelia", "Chefe: Capitã Cornelia", -13, 2.5, icone="aquamirae:shell_horn",
            deps=["corneta"], forma="octagon", tamanho=1.5,
            descricao=["Toque o Chifre de Concha e derrote a &cCapitã Cornelia&r, que voltou como fantasma.", "", "&7Se perder, o chifre é gasto. A missão &e\"Outro Chifre\"&7 dá outro.&r",
                       "", "&7Dica: lute em terra firme ou em cima do gelo, nunca dentro da água.&r"],
            tarefas=[c.t_matar("aquamirae:captain_cornelia", 1, "Derrotar a Capitã Cornelia")],
            recompensas=[c.r_item(fragmento(2, 3, 4)), c.r_skill("epicfight:meteor_slam"), c.r_xp(10),
                         c.r_item("minecraft:diamond", 3)])

    c.quest("corneta_extra", "Outro Chifre", -13, 4.5, icone="aquamirae:shell_horn",
            deps=["corneta"], forma="circle", tamanho=0.75, optional=True, can_repeat=True,
            descricao=["Perdeu a luta? Troque &f6 lingotes de ouro&r por outro Chifre de Concha."],
            tarefas=[c.t_item("minecraft:gold_ingot", 6, consumir=True, titulo="Entregar 6 lingotes de ouro")],
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
            descricao=[f"{M}: \"Esta é a mais traiçoeira. &5Dame Fortuna&r é um espírito que aposta com almas e sorte. Ela ganhou um fragmento num jogo de cartas.\"",
                       "", "&o\"Só aceito te dar a ficha de aposta quando você estiver protegido. Volte com armadura de diamante.\"",
                       "", "&7Equipamento recomendado: diamante.&r"],
            tarefas=[c.t_item("minecraft:diamond_chestplate", titulo="Obter um peitoral de diamante")],
            recompensas=[c.r_item("meetyourfight:devils_ante"), c.r_item(pocao("minecraft:regeneration"), 2)])

    c.quest("dame_fortuna", "Chefe: Dame Fortuna", -7, 5.5, icone="meetyourfight:devils_ante",
            deps=["fortuna"], forma="octagon", tamanho=1.5,
            descricao=["Segure a &fAposta do Diabo&r e clique com o botão direito num lugar aberto para chamar &cDame Fortuna&r. Derrote-a.", "", "&7Se perder, a ficha é gasta. A missão &e\"Nova Aposta\"&7 dá outra.&r",
                       "", "&7Dica: ela troca de padrão de ataque como quem embaralha cartas. Observe antes de atacar.&r"],
            tarefas=[c.t_matar("meetyourfight:dame_fortuna", 1, "Derrotar Dame Fortuna")],
            recompensas=[c.r_item(fragmento(2, 4, 4)), c.r_skill("epicfight:stamina_pillager"), c.r_xp(10),
                         c.r_item("minecraft:diamond", 3)])

    c.quest("ante_extra", "Nova Aposta", -7, 7.5, icone="meetyourfight:devils_ante",
            deps=["fortuna"], forma="circle", tamanho=0.75, optional=True, can_repeat=True,
            descricao=["Perdeu a aposta? Troque &f2 diamantes&r por outra ficha."],
            tarefas=[c.t_item("minecraft:diamond", 2, consumir=True, titulo="Entregar 2 diamantes")],
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
                       "&dFim do Ato 2. O Ato 3 &7(Abismo e Fogo)&d já está liberado no livro.&r"],
            tarefas=[c.t_check("Entregar o relatório")],
            recompensas=[c.r_item("minecraft:obsidian", 10), c.r_item("minecraft:flint_and_steel"),
                         c.r_item(pocao("minecraft:fire_resistance"), 4), c.r_item("minecraft:diamond", 5),
                         c.r_xp(15)])

    # ---- Gabriel, o Guardião dos Dragões (homenagem a um amigo do autor do pacote)
    G = "&bGabriel&r"
    c.quest("gabriel", "O Guardião dos Dragões", 0, 11, icone="minecraft:shield",
            deps=["relatorio"], forma="hexagon", tamanho=1.25,
            subtitulo="Um velho amigo da Ordem",
            descricao=[f"{M}: \"Antes de você partir para o Nether, quero que conheça alguém.\"",
                       "",
                       "&o\"Os antigos guardiões do Selo voavam em dragões. Quando o Selo foi criado, eles esconderam os últimos ovos com a Ordem, e um só homem jurou protegê-los: o &bGabriel&o.\"",
                       "",
                       "&o\"Ele não entrega um ovo a qualquer um. Vou chamá-lo até você. Fale com ele e mostre que merece.\"",
                       "",
                       "Ao completar, o &bGabriel&r aparece do seu lado."],
            tarefas=[c.t_check("Chamar o Gabriel")],
            recompensas=[c.r_comando("/execute as {p} at @s run function terras_partidas:gabriel/aparecer",
                                     titulo="O Gabriel aparece", icone="minecraft:shield", auto=True)])

    c.quest("falar_gabriel", "Fale com o Gabriel", 0, 12, icone="minecraft:writable_book",
            deps=["gabriel"], forma="circle",
            descricao=["Clique no &bGabriel&r com o botão direito para conversar.",
                       "",
                       "Ele guarda os últimos ovos de dragão da Ordem e só entrega um a quem tem coragem de cuidar dele.",
                       "",
                       "Quando estiver pronto, aperte &e\"Estou pronto\"&r na conversa."],
            tarefas=[c.t_conquista("terras_partidas:falou_gabriel", titulo="Conversar com o Gabriel")])

    c.quest("chamar_gabriel", "Chamar o Gabriel", 2, 12, icone="minecraft:bell", deps=["gabriel"],
            forma="circle", tamanho=0.75, optional=True, can_repeat=True,
            descricao=["Perdeu o Gabriel de vista ou quer conversar com ele de novo?",
                       "Pegue a recompensa e ele aparece ao seu lado. Se ele estiver por perto, ele só muda de lugar."],
            tarefas=[c.t_check("Chamar o Gabriel")],
            recompensas=[c.r_comando("/execute as {p} at @s run function terras_partidas:rechamar_gabriel",
                                     titulo="Chamar o Gabriel", icone="minecraft:bell")])

    # ---- Ovo de dragão (recompensa do fim do Ato 2, entregue pelo Gabriel)
    c.quest("ovo", "O Presente de Gabriel", 0, 12.5, icone="dragonmounts:dragon_egg",
            deps=["falar_gabriel"], forma="hexagon", tamanho=1.5,
            max_completable_dependents=1,
            subtitulo="Escolha só um ovo",
            descricao=[f"{G}: \"Guardei estes ovos a vida inteira. Hoje um deles é seu.\"",
                       "",
                       "&o\"Um dragão não é uma arma. É um companheiro, e vai te seguir até o fogo se você cuidar dele. Escolha com calma: não existe segunda escolha.\"",
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
                           "&7O ovo funciona como areia: coloque em cima de um bloco firme.&r",
                           "",
                           f"&cImportante:&r o ambiente em volta decide se o ovo continua deste tipo. Até ele chocar, deixe-o perto de &f{habitat}&r. Os blocos que vieram junto servem para isso.",
                           "",
                           "&eDepois de chocar:&r alimente o filhote com &fcarne&r. Quando ele crescer, coloque a &fsela&r e monte."],
                tarefas=[c.t_check(f"Escolher o {nome}")],
                recompensas=[c.r_item(ovo_dragao(raca)), c.r_item(bloco, 8), c.r_item("minecraft:saddle"),
                             c.r_item("minecraft:cooked_beef", 32)])

    c.quest("primeiro_voo", "Primeiro Voo", 0, 17.5, icone="minecraft:saddle",
            deps=[k for k, *_ in ovos], dependency_requirement="one_completed", optional=True,
            forma="gear", tamanho=1.5,
            descricao=[f"{G}: \"Quando ele crescer, suba e voe. Não existe sensação igual. Eu ainda lembro do meu primeiro voo.\"",
                       "",
                       "&eControles do dragão:&r use as teclas de pular e agachar para subir e descer. Os controles de voo ficam em &eOpções > Controles&r, na seção do Dragon Mounts.",
                       "",
                       "Marque esta missão quando fizer o primeiro voo."],
            tarefas=[c.t_check("Voei no meu dragão!")],
            recompensas=[c.r_item("minecraft:golden_apple", 3), c.r_item("minecraft:cooked_beef", 32), c.r_xp(10),
                         c.r_comando(f"/tag {{p}} add {TAG_VOOU}", titulo="O Gabriel fica sabendo do seu voo",
                                     icone="minecraft:feather")])

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
                "&o\"Lá embaixo, três criaturas forjadas no fogo guardam três pedaços do Selo. O quarto se misturou à energia dos esqueletos wither e só aparecerá quando o Wither despertar.\"",
                "",
                "Construa um portal: uma moldura de obsidiana de 4 blocos de largura por 5 de altura, contando a moldura (o buraco do meio fica 2x3). Acenda com isqueiro e entre no Nether.",
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

    c.quest("blaze", "Varas de Blaze", -6, -3, icone="minecraft:blaze_rod", deps=["fortaleza"], optional=True,
            descricao=["Derrote blazes e junte &f8 varas de blaze&r.",
                       "&7Guarde algumas: elas vão ser importantes no fim da jornada.&r"],
            tarefas=[c.t_item("minecraft:blaze_rod", 8, titulo="Obter 8 varas de blaze")],
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
                       "", "&7Dica: ela é lenta, mas cada golpe é devastador. Fique fora do alcance dos socos e cuidado com as bombas de lava. Leve blocos para fazer plataformas e saiba por onde fugir antes de acordá-la.&r"],
            tarefas=[c.t_matar("cataclysm:netherite_monstrosity", 1, "Derrotar a Monstruosidade de Netherita")],
            recompensas=[c.r_item(fragmento(3, 1, 4)), c.r_skill("epicfight:endurance"), c.r_xp(12),
                         c.r_item("minecraft:diamond", 4)])

    # ---- Frente B: Arena Ardente (Ignis)
    c.quest("arena", "A Arena Ardente", 4, 3, icone="minecraft:magma_block", deps=["portal"],
            subtitulo="Segunda frente",
            descricao=[f"{M}: \"Um campeão de fogo chamado &6Ignis&r guarda uma arena nos desertos do Nether. Ele só aparece quando alguém coloca &fCinzas Flamejantes&r no &fAltar de Fogo&r, no centro da arena.\"",
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
            tarefas=[c.t_check("Obter as Cinzas Flamejantes")],
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
            tarefas=[c.t_item("minecraft:magma_cream", 8, consumir=True, titulo="Entregar 8 cremes de magma")],
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
                       "", "&7Dica: quando o olho vermelho dela brilhar, ela vai disparar um laser. Saia da linha de visão: atrás de um pilar ou de blocos que você colocar.&r"],
            tarefas=[c.t_matar("bosses_of_mass_destruction:gauntlet", 1, "Derrotar a Manopla do Nether")],
            recompensas=[c.r_item(fragmento(3, 3, 4)), c.r_skill("epicfight:emergency_escape"), c.r_xp(12),
                         c.r_item("minecraft:diamond", 4)])

    # ---- Chefe final: Wither
    c.quest("despertar", "O Que Despertou", 0, 13, icone="minecraft:wither_skeleton_skull",
            deps=["monstruosidade", "ignis", "gauntlet", "fortaleza"],
            subtitulo="O último fragmento do Nether",
            descricao=[f"{M}: \"O fragmento mais forte do Nether não corrompeu uma criatura comum. Ele se misturou à energia sombria dos &8esqueletos wither&r, e só aparece quando o &8Wither&r desperta.\"",
                       "",
                       "&o\"É perigoso, mas é a única forma de arrancar o último pedaço do Selo do Nether.\"", "", "&o\"Mais uma coisa. Os batedores acharam um nome gravado com fogo de alma nas paredes de uma fortaleza: &3Helvar&o. Não sei quem é. Mas não esqueça esse nome.\"",
                       "",
                       "Junte &f3 crânios de esqueleto wither&r (das fortalezas) e &f4 areias das almas&r."],
            tarefas=[c.t_item("minecraft:wither_skeleton_skull", 3, titulo="Obter 3 crânios de esqueleto wither"),
                     c.t_item("minecraft:soul_sand", 4, titulo="Obter 4 areias das almas")],
            recompensas=[c.r_item(pocao("minecraft:strong_healing"), 4), c.r_item(pocao("minecraft:strong_strength"), 2),
                         c.r_item("minecraft:golden_apple", 4)])

    c.quest("wither", "Chefe: O Wither", 0, 16, icone="minecraft:nether_star",
            deps=["despertar"], forma="octagon", tamanho=2.0,
            descricao=["Monte o &8Wither&r (4 areias das almas em T e os 3 crânios em cima) e derrote-o.",
                       "",
                       "&cImportante:&r invoque longe da sua base! Ele destrói tudo em volta.",
                       "&7Dica: invoque num lugar fechado no subsolo, para ele não fugir voando. Quando a vida dele cair pela metade, ele fica imune a flechas.&r"],
            tarefas=[c.t_matar("minecraft:wither", 1, "Derrotar o Wither")],
            recompensas=[c.r_item(fragmento(3, 4, 4)), c.r_skill("epicfight:death_harvest"), c.r_xp(20),
                         c.r_item("minecraft:diamond", 6)])

    c.quest("relatorio", "Relatório: Abismo e Fogo", 0, 19.5, icone="minecraft:amethyst_shard",
            deps=["wither"], forma="gear", tamanho=2.0,
            subtitulo="Fim do Ato 3",
            descricao=[f"{M}: \"Onze fragmentos. O Selo está quase completo... e mesmo assim ele continua pulsando.\"",
                       "",
                       "&o\"Quando o Wither caiu, os fragmentos brilharam e apontaram para cima. Para o céu. Existem dois mundos acima das nuvens, o &bEverbright&o e o &6Everdawn&o, onde os guardiões originais se refugiaram depois de criar o Selo.\"",
                       "",
                       "&o\"Lá estão as respostas. E, eu temo, os guardiões que criaram o Selo.\"",
                       "",
                       "&dFim do Ato 3. O Ato 4 &7(Além do Céu)&d já está liberado no livro.&r"],
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
                 boss_chave, boss_nome, boss_id, historia, dica, frag, skill, icone_boss, diamantes=5):
        aviso_chave = []
        if chave_item == "blue_skies:blinding_key":
            aviso_chave = ["", "&7No jogo, a chave desta masmorra se chama &fChave da Masmorra Ofuscante&7.&r"]
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
                           "Depois, use a chave correspondente na &fpedra-chave&r da porta do chefe."] + aviso_chave,
                tarefas=[c.t_item(chave_item, titulo=f"Encontrar a {nome_chave}")],
                recompensas=[c.r_xp(5)])
        c.quest(boss_chave, f"Chefe: {boss_nome}", x + 9, y, icone=icone_boss, deps=[chave + "_chave"],
                forma="octagon", tamanho=1.5,
                descricao=[f"Derrote &c{boss_nome}&r, um dos guardiões do Selo, corrompido pelo fragmento.", "", dica],
                tarefas=[c.t_matar(boss_id, 1, f"Derrotar {boss_nome}")],
                recompensas=[c.r_item(fragmento(4, frag, 4)), c.r_skill(skill), c.r_xp(15),
                             c.r_item("minecraft:diamond", diamantes)])

    c.quest("ceu", "Além do Céu", 0, 0, forma="gear", tamanho=1.75,
            icone="blue_skies:zeal_lighter", deps=["@ato3/relatorio"],
            subtitulo="Os mundos acima das nuvens",
            descricao=[
                f"{M}: \"Encontrei nos arquivos mais antigos da Ordem: seis dos sete guardiões do Selo não morreram. Eles se refugiaram em dois mundos acima das nuvens e sobreviveram por trezentos anos.\"",
                "",
                "&o\"O &bEverbright&o, de luz e gelo eterno, e o &6Everdawn&o, onde o sol nunca termina de nascer. Mas os fragmentos que caíram por lá os transformaram em monstros. Quatro deles estão lá em cima. Os outros dois, eu ainda não sei.\"",
                "",
                "&o\"Existe um &fGuardião do Portal&o que vive em uma casa no nosso mundo e sabe abrir o caminho. Leve este &fIsqueiro Zeal&o e os tijolos que separei.\"",
            ],
            tarefas=[c.t_check("Partir para além do céu")],
            recompensas=[c.r_mapa("casa_do_guardiao", "Mapa: Casa do Guardião do Portal"),
                         c.r_item("blue_skies:zeal_lighter"), c.r_item("blue_skies:turquoise_stonebrick", 16),
                         c.r_item("blue_skies:lunar_stonebrick", 16), c.r_xp(5)])

    c.quest("casa", "A Casa do Guardião", 3, 0, icone="minecraft:oak_door", deps=["ceu"],
            descricao=["Siga o mapa até a &fcasa do Guardião do Portal&r. Ela fica no mundo normal, geralmente perto de uma vila, em planícies, savanas, montanhas ou terras nevadas.",
                       "",
                       "&eComo abrir os portais:&r monte uma moldura do mesmo formato do portal do Nether (4 de largura por 5 de altura) e acenda com o &fIsqueiro Zeal&r (clique direito dentro da moldura).",
                       "• Moldura de &bTijolos de Pedra Turquesa&r: leva ao &bEverbright&r.",
                       "• Moldura de &fTijolos de Pedra Lunar&r: leva ao &6Everdawn&r.",
                       "",
                       "Os cantos da moldura precisam de tijolo: cada portal leva 14 blocos. O Mestre mandou 16 de cada tipo, então sobram 2 de reserva."],
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
    masmorra("eb_ofuscante", 9, -3, ["everbright"], "Masmorra do Invocador", "Everbright", EB,
             "blue_skies:everbright_blinding_dungeon", "blue_skies:blinding_key", "Chave da Masmorra do Invocador",
             "summoner", "Summoner", "blue_skies:summoner",
             f"{M}: \"O primeiro guardião, o &fSummoner&r (o Invocador), se trancou numa masmorra de luz cegante, a Masmorra Ofuscante do Everbright. Ele chama criaturas para lutar por ele.\"",
             "&7Dica: ele invoca ajudantes sem parar. Derrube os ajudantes rápido e ataque o Summoner entre uma invocação e outra.&r",
             1, "epicfight:revelation", "minecraft:totem_of_undying", diamantes=4)
    masmorra("eb_natureza", 9, -6, ["summoner"], "Masmorra da Natureza", "Everbright", EB,
             "blue_skies:nature_dungeon", "blue_skies:nature_key", "Chave da Masmorra da Natureza",
             "starlit_crusher", "Starlit Crusher", "blue_skies:starlit_crusher",
             f"{M}: \"O segundo guardião do Everbright virou uma árvore viva gigante, o &fStarlit Crusher&r (o Esmagador Estelar). Ele vive numa masmorra coberta de mato, nos pinheiros nevados.\"",
             "&7Dica: ele é lento mas bate muito forte. Fique sempre se movendo e ataque pelas costas.&r",
             2, "epicfight:forbidden_strength", "minecraft:oak_sapling", diamantes=4)

    # ---- Everdawn
    masmorra("ed_ofuscante", 9, 3, ["everdawn"], "Masmorra do Alquimista", "Everdawn", ED,
             "blue_skies:everdawn_blinding_dungeon", "blue_skies:blinding_key", "Chave da Masmorra do Alquimista",
             "alchemist", "Alchemist", "blue_skies:alchemist",
             f"{M}: \"No Everdawn, o guardião &fAlchemist&r (o Alquimista) passou séculos fazendo poções com o poder do fragmento, na Masmorra Ofuscante do Everdawn. Ele não é mais humano.\"",
             "&7Dica: ele joga poções que mudam o chão da arena. Leve leite: ele tira os efeitos ruins mais comuns.&r",
             3, "epicfight:adaptive_skin", "minecraft:brewing_stand")
    masmorra("ed_veneno", 9, 6, ["alchemist"], "Masmorra do Veneno", "Everdawn", ED,
             "blue_skies:poison_dungeon", "blue_skies:poison_key", "Chave da Masmorra do Veneno",
             "arachnarch", "Arachnarch", "blue_skies:arachnarch",
             f"{M}: \"O quarto e último guardião do Everdawn virou uma aranha gigante, a &fArachnarch&r (a Aracnarca). Ela fez um ninho numa masmorra venenosa na floresta de bordos.\"",
             "&7Dica: leve muito leite e poções de cura. O veneno dela é o perigo maior, não as mordidas.&r",
             4, "epicfight:vengeance", "minecraft:spider_eye")

    c.quest("relatorio", "Relatório: Além do Céu", 21, 0, icone="minecraft:amethyst_shard",
            deps=["starlit_crusher", "arachnarch"], forma="gear", tamanho=2.0,
            subtitulo="Fim do Ato 4",
            descricao=[f"{M}: \"Quinze fragmentos. Os quatro guardiões do céu foram derrotados e estão livres da corrupção.\"",
                       "",
                       "&o\"Antes de morrer, o Alquimista sussurrou algo: o Selo só pode ser refeito onde foi quebrado. No &5End&o, onde o Dragão guarda o vazio. Os dois últimos guardiões estão lá.\"", "", "&o\"E ele disse mais uma palavra antes de partir: &3Helvar&o. O mesmo nome da fortaleza do Nether.\"",
                       "",
                       "&o\"Use os olhos do Ender para achar a fortaleza escondida. A última batalha nos espera.\"",
                       "",
                       "&dFim do Ato 4. O Ato 5 &7(O Fim do Selo)&d já está liberado no livro.&r"],
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



# ---------------------------------------------------------------- ATO 5

def ato5():
    c = Capitulo("ato5")
    M = "&6Mestre Vellan&r"
    END, OW = "minecraft:the_end", "minecraft:overworld"

    def coord(onde):
        return f"&7Pegue a recompensa &f{onde}&7: as coordenadas aparecem no chat.&r"

    c.quest("fim", "O Fim do Selo", 0, 0, forma="gear", tamanho=1.75,
            icone="minecraft:ender_eye", deps=["@ato4/relatorio"],
            subtitulo="A última jornada",
            descricao=[
                f"{M}: \"Quinze fragmentos. Falta pouco.\"",
                "",
                "&o\"O Selo foi quebrado no &5End&o. O Dragão guarda o portal do outro lado, e os dois últimos guardiões corrompidos esperam por você no vazio.\"",
                "",
                "&o\"A Ordem achou uma fortaleza escondida no subsolo e mandou as coordenadas. Se quiser procurar outra, jogue um Olho do Ender para o alto e siga para onde ele voar.\"",
                "",
                coord("no mundo normal"),
            ],
            tarefas=[c.t_check("Começar a última jornada")],
            recompensas=[c.r_localizar("betterstrongholds:stronghold", "Coordenadas da fortaleza do End", dimensao=OW),
                         c.r_item("minecraft:ender_eye", 4), c.r_xp(5)])

    c.quest("fortaleza", "A Fortaleza Escondida", 3, 0, icone="minecraft:end_portal_frame", deps=["fim"],
            descricao=["Encontre a &ffortaleza&r e a sala do portal do End.",
                       "Coloque Olhos do Ender em todas as molduras para ativar o portal."],
            tarefas=[c.t_estrutura("betterstrongholds:stronghold", "Encontrar a fortaleza")],
            recompensas=[c.r_xp(5), c.r_item(pocao("minecraft:long_slow_falling"), 3)])

    c.quest("end", "O Vazio", 6, 0, icone="minecraft:end_stone", deps=["fortaleza"],
            descricao=["Atravesse o portal e entre no &5End&r.",
                       "", "&7Dica: leve blocos para construir, uma abóbora na cabeça se os endermen te incomodarem (com ela eles não te atacam quando você olha para eles, mas a visão fica menor) e muitas flechas para destruir os cristais.&r"],
            tarefas=[c.t_dimensao(END, "Entrar no End")],
            recompensas=[c.r_xp(5), c.r_item("minecraft:carved_pumpkin")])

    c.quest("dragao", "Chefe: Dragão do Ender", 9, 0, icone="minecraft:dragon_head",
            deps=["end"], forma="octagon", tamanho=1.75,
            descricao=["Destrua os cristais no topo das torres de obsidiana e derrote o &5Dragão do Ender&r.",
                       "", "&7Dica: quando ele pousar no centro, é a hora de atacar de perto. Cuidado com o sopro roxo no chão.&r"],
            tarefas=[c.t_matar("minecraft:ender_dragon", 1, "Derrotar o Dragão do Ender")],
            recompensas=[c.r_item(fragmento(5, 1, 4)), c.r_skill("epicfight:impact_guard"), c.r_xp(20),
                         c.r_item("minecraft:diamond", 6)])

    c.quest("elytra", "Asas do Fim", 12, -3, icone="minecraft:elytra", deps=["dragao"], optional=True,
            descricao=["&7Missão extra.&r Nas ilhas de fora existem cidades do End, e algumas têm navios com &fasas&r (élitros). Consiga um par."],
            tarefas=[c.t_item("minecraft:elytra")],
            recompensas=[c.r_item("minecraft:firework_rocket", 32), c.r_xp(10)])

    # ---- Cidadela Arruinada (Ender Guardian)
    c.quest("cidadela", "A Cidadela Arruinada", 12, 0, icone="minecraft:purpur_block", deps=["dragao"],
            subtitulo="Primeiro guardião do vazio",
            descricao=[f"{M}: \"Nas ilhas distantes do End existe uma cidadela em ruínas. O &fGuardião Ender&r vigia um altar no coração dela.\"",
                       "", "&7Para chegar às ilhas de fora, use o portal pequeno que aparece depois que o Dragão morre (jogue uma pérola do Ender nele).&r", "&7Esta frente e a do Monolito Negro podem ser feitas em qualquer ordem.&r",
                       "", coord("estando no End")],
            tarefas=[c.t_check("Pedir a localização da Cidadela")],
            recompensas=[c.r_localizar("cataclysm:ruined_citadel", "Coordenadas da Cidadela Arruinada", dimensao=END),
                         c.r_item("minecraft:ender_pearl", 8)])

    c.quest("cidadela_achar", "Dentro da Cidadela", 15, 0, icone="minecraft:end_stone_bricks", deps=["cidadela"],
            descricao=["Vá até as coordenadas e entre na &fCidadela Arruinada&r.",
                       "&7Cuidado com os Golens do Ender pelo caminho.&r"],
            tarefas=[c.t_estrutura("cataclysm:ruined_citadel", "Encontrar a Cidadela Arruinada")],
            recompensas=[c.r_xp(5), c.r_item(pocao("minecraft:strong_healing"), 3)])

    c.quest("ender_guardian", "Chefe: Guardião Ender", 18, 0, icone="minecraft:end_crystal",
            deps=["cidadela_achar"], forma="octagon", tamanho=1.5,
            descricao=["Chegue perto do &fAltar do Vazio&r no centro da cidadela. O &cGuardião Ender&r vai aparecer.",
                       "", "&7Dica: ele invoca runas do vazio no chão. Não fique parado em cima delas.&r"],
            tarefas=[c.t_matar("cataclysm:ender_guardian", 1, "Derrotar o Guardião Ender")],
            recompensas=[c.r_item(fragmento(5, 2, 4)), c.r_skill("epicfight:adrenaline_fiend"), c.r_xp(20),
                         c.r_item("minecraft:diamond", 6)])

    # ---- Arena de Obsidiana (Obsidilith)
    c.quest("arena", "O Monolito Negro", 12, 3, icone="minecraft:obsidian", deps=["dragao"],
            subtitulo="Segundo guardião do vazio",
            descricao=[f"{M}: \"Existe um monolito vivo de obsidiana, o &fObsidilith&r. Ele dorme numa arena de obsidiana. Para acordá-lo, coloque um &fOlho do Ender&r no altar da arena.\"",
                       "", "&7Esta frente e a da Cidadela Arruinada podem ser feitas em qualquer ordem.&r",
                       "", coord("estando no End")],
            tarefas=[c.t_check("Pedir a localização da Arena de Obsidiana")],
            recompensas=[c.r_localizar("bosses_of_mass_destruction:obsidilith_arena", "Coordenadas da Arena de Obsidiana", dimensao=END),
                         c.r_item("minecraft:ender_eye", 4)])

    c.quest("arena_achar", "A Arena de Obsidiana", 15, 3, icone="minecraft:crying_obsidian", deps=["arena"],
            descricao=["Vá até as coordenadas e encontre a &fArena de Obsidiana&r."],
            tarefas=[c.t_estrutura("bosses_of_mass_destruction:obsidilith_arena", "Encontrar a Arena de Obsidiana")],
            recompensas=[c.r_xp(5)])

    c.quest("obsidilith", "Chefe: Obsidilith", 18, 3, icone="minecraft:obsidian",
            deps=["arena_achar"], forma="octagon", tamanho=1.5,
            descricao=["Coloque um Olho do Ender no &faltar de obsidiana&r e derrote o &cObsidilith&r.",
                       "", "&7Dica: ele não se mexe, mas atira pilares e ondas de choque. Quando ele brilhar, se afaste.&r"],
            tarefas=[c.t_matar("bosses_of_mass_destruction:obsidilith", 1, "Derrotar o Obsidilith")],
            recompensas=[c.r_item(fragmento(5, 3, 4)), c.r_skill("epicfight:bonebreaker"), c.r_xp(20),
                         c.r_item("minecraft:diamond", 6)])

    # ---- Chefe final: The Harbinger
    c.quest("revelacao", "A Verdade sobre o Selo", 21, 1.5, icone="minecraft:nether_star",
            deps=["ender_guardian", "obsidilith"], forma="hexagon", tamanho=1.5,
            subtitulo="O coração do Selo",
            descricao=[f"{M}: \"Dezoito fragmentos... e o Selo ainda não fecha. Falta o núcleo, o coração que mantém todos os pedaços unidos.\"",
                       "",
                       "&o\"Agora eu entendo. O mal antigo nunca foi um monstro. Era uma máquina de guerra, o &cArauto&o, construída para destruir o mundo. Os guardiões não conseguiram destruí-la, então a desligaram. Depois descobriram que o núcleo dela conseguia conter um poder ainda pior, e o transformaram no coração do Selo: o décimo nono fragmento.\"",
                       "",
                       "&o\"Ela está numa fábrica antiga, enterrada fundo nas cavernas. Para despertá-la e arrancar o fragmento, é preciso o poder de uma &fEstrela do Nether&o. A mesma que você tirou do Wither.\"",
                       "",
                       "Tenha uma &fEstrela do Nether&r no inventário.",
                       "&7Se você já usou a estrela (num sinalizador, por exemplo), invoque outro Wither para conseguir uma nova. Os crânios vêm das fortalezas do Nether.&r",
                       "", coord("no mundo normal")],
            tarefas=[c.t_item("minecraft:nether_star", titulo="Obter uma Estrela do Nether")],
            recompensas=[c.r_localizar("cataclysm:ancient_factory", "Coordenadas da Fábrica Antiga", dimensao=OW),
                         c.r_item(pocao("minecraft:strong_healing"), 4), c.r_item(pocao("minecraft:strong_strength"), 2),
                         c.r_item("minecraft:enchanted_golden_apple", 2)])

    c.quest("fabrica", "A Fábrica Antiga", 24, 1.5, icone="minecraft:redstone_block", deps=["revelacao"],
            descricao=["Vá até as coordenadas. A &fFábrica Antiga&r fica no subsolo, em cavernas profundas.",
                       "&7Leve tochas e uma picareta boa.&r"],
            tarefas=[c.t_estrutura("cataclysm:ancient_factory", "Encontrar a Fábrica Antiga")],
            recompensas=[c.r_xp(5)])

    c.quest("harbinger", "Chefe Final: O Arauto", 27, 1.5, icone="minecraft:wither_skeleton_skull",
            deps=["fabrica"], forma="octagon", tamanho=2.25,
            descricao=["No centro da fábrica está o &cArauto&r, desligado.",
                       "Clique nele com a &fEstrela do Nether&r na mão para despertá-lo e derrote-o.",
                       "&cA estrela é gasta ao despertá-lo.&r Só desperte o Arauto quando estiver preparado. Se perder a luta, vai precisar de outra estrela (de outro Wither).",
                       "",
                       "&7Dica: ele dispara mísseis teleguiados e lasers. Use pilares como cobertura, e na segunda fase fique perto dele: os lasers são piores de longe.&r",
                       "",
                       "&5O núcleo dele guarda mais do que um fragmento.&r"],
            tarefas=[c.t_matar("cataclysm:the_harbinger", 1, "Derrotar o Arauto")],
            recompensas=[c.r_item(fragmento(5, 4, 4)), c.r_skill("epicfight:catharsis"), c.r_xp(30),
                         c.r_item("minecraft:netherite_ingot", 2)])

    NETHER = "minecraft:the_nether"
    c.quest("helvar_porta", "A Porta do Submundo", 28.5, 1.5, icone="minecraft:soul_lantern",
            deps=["harbinger"], forma="hexagon", tamanho=1.5, subtitulo="O verdadeiro mal antigo",
            descricao=[f"{M}: \"Eu estava errado. O Arauto nunca foi o mal antigo. Ele era o &fcarcereiro&o.\"",
                       "",
                       "&o\"Lembra do nome gravado na fortaleza? Muito antes do Selo existir, um cavaleiro vendeu a alma ao submundo em troca de poder: &3Helvar&o. Os sete guardiões não conseguiram matá-lo. Prenderam-no numa arena no fundo do Nether.\"", "", "&o\"O núcleo do Arauto era a única coisa capaz de conter a energia de Helvar. Por isso ele virou o coração do Selo: enquanto o núcleo estava no lugar, a porta continuava trancada. Quando você arrancou o fragmento, a prisão começou a ruir.\"",
                       "",
                       "&o\"Com o núcleo arrancado, a porta enfraquece a cada dia. Se ele sair sozinho, nada mais vai pará-lo. Você precisa entrar lá primeiro.\"",
                       "",
                       coord("estando no Nether")],
            tarefas=[c.t_check("Estou pronto")],
            recompensas=[c.r_localizar("block_factorys_bosses:underworld_arena", "Coordenadas da Arena do Submundo", dimensao=NETHER),
                         c.r_item(pocao("minecraft:long_fire_resistance"), 3),
                         c.r_item(pocao("minecraft:strong_healing"), 4),
                         c.r_item("minecraft:enchanted_golden_apple", 2)])

    c.quest("helvar_arena", "A Arena do Submundo", 28.5, 1.5, icone="minecraft:soul_sand", deps=["helvar_porta"],
            descricao=["Vá até as coordenadas, no &cNether&r. A arena fica &fenterrada&r, mais ou menos na altura Y=30, nos biomas Ermos do Nether ou Vale de Areia de Almas.",
                       "",
                       "&7Os corredores são guardados por &fEsqueletos das Almas&7 e &fCavaleiros Wither&7. Leve picareta para cavar até a entrada.&r",
                       "",
                       f"{M}: \"Quando chegar lá, pegue a recompensa. A Ordem guardou a &fchave da porta&o por trezentos anos, esperando este dia.\""],
            tarefas=[c.t_estrutura("block_factorys_bosses:underworld_arena", "Encontrar a Arena do Submundo")],
            recompensas=[c.r_item("block_factorys_bosses:underworld_arena_key"), c.r_xp(15),
                         c.r_item(pocao("minecraft:strong_strength"), 2), c.r_item(pocao("minecraft:strong_regeneration"), 2)])

    c.quest("helvar_chave", "Outra Chave da Arena", 28.5, 1.5, icone="minecraft:tripwire_hook", deps=["helvar_arena"],
            optional=True, can_repeat=True, tamanho=0.75,
            descricao=["Gastou a chave e perdeu a luta? Troque recursos por outra.",
                       "",
                       "&7Os Esqueletos das Almas e os Cavaleiros Wither da arena também deixam a chave, mas é raro.&r"],
            tarefas=[c.t_item("minecraft:gold_ingot", 8, consumir=True, titulo="Entregar 8 lingotes de ouro"), c.t_item("minecraft:soul_sand", 16, consumir=True, titulo="Entregar 16 areias das almas")],
            recompensas=[c.r_item("block_factorys_bosses:underworld_arena_key")])

    c.quest("helvar", "Chefe Final: Helvar, o Cavaleiro do Submundo", 28.5, 1.5, icone="block_factorys_bosses:knight_sword",
            deps=["helvar_arena"], forma="octagon", tamanho=2.5, subtitulo="O mal que o Selo prendia",
            descricao=["Use a chave na &fporta da arena&r. Lá dentro está &3Helvar&r.",
                       "",
                       "&eComo ele luta:&r",
                       "• Ele te nota e &fse apresenta&r antes de atacar. Aproveite para se preparar.",
                       "• Combos de espada e &fsaltos giratórios&r: esquive para o lado, não para trás.",
                       "• &fFendas&r se abrem no ar e disparam fogo. Não fique parado na frente delas.",
                       "• &cEle tem uma segunda fase.&r Quando ele cair, prepare-se: ele volta mais forte, com &ffogos-fátuos&r que explodem.",
                       "",
                       "&7Se ele cair de joelhos, é a sua chance: ataque com tudo.&r"],
            tarefas=[c.t_matar("block_factorys_bosses:underworld_knight", 1, "Derrotar Helvar")],
            recompensas=[c.r_xp(50), c.r_item("minecraft:nether_star"), c.r_item("minecraft:netherite_ingot", 2),
                         c.r_comando(f"/tag {{p}} add {TAG_HELVAR}", titulo="O Mestre Vellan sente a queda de Helvar",
                                     icone="minecraft:writable_book", auto=True)])

    c.quest("selo", "O Selo Restaurado", 30, 1.5, icone="minecraft:beacon",
            deps=["helvar"], forma="gear", tamanho=2.5,
            subtitulo="Fim da história",
            descricao=[f"{M}: \"Helvar caiu. Eu senti a porta do submundo tremer daqui.\"",
                       "",
                       "&o\"Os dezenove fragmentos estão com você. Venha até mim: está na hora de colocar o último pedaço no lugar e terminar o ritual que começamos há trezentos anos.\"",
                       "",
                       "&eComo terminar:&r volte ao &6Mestre Vellan&r (se ele estiver longe, use a missão &e\"Chamar o Mestre\"&r do Ato 1), clique nele com o botão direito e aperte &e\"Restaurar o Selo\"&r.",
                       "",
                       "&6&lObrigado por jogar SealCraft!&r",
                       "",
                       "&7Depois do final, os &fDesafios Lendários&7 e as &fCaçadas&7 continuam abertos para quem quer mais.&r"],
            tarefas=[c.t_conquista("terras_partidas:selo_restaurado", titulo="Restaurar o Selo com o Mestre Vellan")],
            recompensas=[c.r_item("minecraft:beacon"), c.r_item("minecraft:netherite_ingot", 4),
                         c.r_item("minecraft:enchanted_golden_apple", 4), c.r_item("minecraft:diamond_block", 8),
                         c.r_xp(50)])

    # ---- Desafios Lendários (pós-história, opcionais)
    c.quest("lendarios", "Desafios Lendários", 30, 6, icone="minecraft:dragon_egg", deps=["selo"],
            forma="hexagon", optional=True,
            descricao=["&7Para quem ainda quer mais.&r Dois monstros lendários esperam em lugares que a Ordem já conhece, além das feras antigas das Caçadas. Nenhum guarda fragmentos, só glória."],
            tarefas=[c.t_check("Aceitar os desafios")],
            recompensas=[c.r_xp(5)])

    c.quest("void_blossom_mapa", "A Flor do Vazio", 27, 8.5, icone="minecraft:spore_blossom", deps=["lendarios"],
            optional=True,
            descricao=["Nas cavernas verdes e úmidas cresce uma flor gigante e carnívora, a &cFlor do Vazio&r. A Ordem já localizou uma delas.",
                       "", coord("no mundo normal")],
            tarefas=[c.t_check("Pedir a localização")],
            recompensas=[c.r_localizar("bosses_of_mass_destruction:void_blossom", "Coordenadas da Flor do Vazio", dimensao=OW)])

    c.quest("void_blossom", "Lendário: Flor do Vazio", 27, 11, icone="minecraft:spore_blossom", deps=["void_blossom_mapa"],
            forma="octagon", tamanho=1.25, optional=True,
            descricao=["Derrote a &cFlor do Vazio&r.", "&7Dica: ela solta espinhos do chão. Fique se movendo.&r"],
            tarefas=[c.t_matar("bosses_of_mass_destruction:void_blossom", 1, "Derrotar a Flor do Vazio")],
            recompensas=[c.r_item("minecraft:diamond_block", 4), c.r_xp(25)])

    c.quest("leviathan_mapa", "A Cidade Afundada", 33, 8.5, icone="minecraft:prismarine_bricks", deps=["lendarios"],
            optional=True,
            descricao=["No fundo do oceano existe uma cidade afundada. No altar dela, um &cLeviatã&r espera ser chamado.",
                       "", "Use o &fSacrifício Abissal&r no &fAltar do Abismo&r da cidade para chamá-lo. &cO sacrifício é gasto ao chamar o Leviatã.&r",
                       "&7Ele é invencível fora da água. Leve poções de respiração aquática.&r",
                       "", coord("no mundo normal")],
            tarefas=[c.t_check("Pedir a localização")],
            recompensas=[c.r_localizar("cataclysm:sunken_city", "Coordenadas da Cidade Afundada", dimensao=OW),
                         c.r_item("cataclysm:abyssal_sacrifice"), c.r_item(pocao("minecraft:long_water_breathing"), 4)])

    c.quest("leviathan", "Lendário: O Leviatã", 33, 11, icone="minecraft:heart_of_the_sea", deps=["leviathan_mapa"],
            forma="octagon", tamanho=1.25, optional=True,
            descricao=["Derrote &co Leviatã&r."],
            tarefas=[c.t_matar("cataclysm:the_leviathan", 1, "Derrotar o Leviatã")],
            recompensas=[c.r_item("minecraft:diamond_block", 4), c.r_xp(25)])

    return {
        "id": qid("capitulo/ato5"),
        "group": "",
        "order_index": 4,
        "filename": "ato_5_o_fim_do_selo",
        "title": "Ato 5: O Fim do Selo",
        "subtitle": ["A última batalha"],
        "icon": "minecraft:ender_eye",
        "default_quest_shape": "",
        "default_hide_dependency_lines": False,
        "quests": c.quests,
    }



# ---------------------------------------------------------------- CAÇADAS (chefes do Bosses'Rise, opcionais)

def cacadas():
    c = Capitulo("cacadas")
    M = "&6Mestre Vellan&r"
    OW = "minecraft:overworld"
    c.quest("inicio", "Caçadas", 0, 0, forma="gear", tamanho=1.75, icone="minecraft:spyglass",
            deps=["@ato2/relatorio"], subtitulo="Nove feras antigas, sem fragmentos",
            descricao=[f"{M}: \"Nem todo monstro gigante deste mundo guarda um fragmento. Algumas feras são só antigas... e perigosas.\"",
                       "",
                       "&o\"Caçadores da Ordem já tentaram e não voltaram. Mas o que elas guardam vale o risco: armas que você não acha em nenhum outro lugar.\"",
                       "",
                       "&7Todas as caçadas são opcionais e podem ser feitas em qualquer ordem. Elas estão apresentadas em ordem aproximada de dificuldade. Cada fera deixa um tesouro próprio, e quem derrotar todas vira &6Mestre Caçador&7.&r"],
            tarefas=[c.t_check("Quero caçar")],
            recompensas=[c.r_item("minecraft:spyglass")])
    # (chave, nome, ícone, estrutura ou None, entidade, onde, descrição, o que deixa, recompensas do mapa, recomendação)
    feras = [
        ("sandworm", "Sirok, a Minhoca de Areia", "minecraft:sand", "block_factorys_bosses:sandworm_nest", "block_factorys_bosses:sandworm",
         "no &fDeserto&r", "Uma minhoca gigante que nada debaixo da areia e cospe veneno. Quando a areia começar a tremer, saia de perto: colunas de areia sobem do chão.",
         "a &fManopla de Sirok&r, que atira veneno", [c.r_item("minecraft:milk_bucket")], "Mais fácil: a partir do Ato 2"),
        ("escultor", "Tongbi, o Escultor", "minecraft:chiseled_stone_bricks", "mowziesmobs:monastery", "mowziesmobs:sculptor",
         "num &fmonastério no alto das montanhas&r", "Um mestre que molda a pedra. Ele te desafia a subir uma coluna de pedra até ele enquanto arremessa rochas. Se cair, você recomeça a subida.",
         "o &fCajado do Escultor&r e as roupas do &fGeomante&r", [c.r_item(pocao("minecraft:long_slow_falling"), 2)], "Fácil: a partir do Ato 2"),
        ("lich", "O Lich da Noite", "minecraft:soul_lantern", "bosses_of_mass_destruction:lich_tower", "bosses_of_mass_destruction:lich",
         "no alto da &fTorre do Lich&r", "Um feiticeiro morto-vivo que dispara bolas de fogo azuis e cometas, e se teletransporta pela sala. Não o perca de vista.",
         "a &fÂnima Antiga&r e diamantes", [c.r_item(pocao("minecraft:long_fire_resistance"), 2)], "Médio: a partir do Ato 3"),
        ("yeti", "Skor, o Yeti", "minecraft:packed_ice", "block_factorys_bosses:yeti_hideout", "block_factorys_bosses:yeti",
         "nas &fPlanícies Nevadas&r", "Um yeti enorme num esconderijo de gelo. Solta nevascas e prende você em cubos de gelo.",
         "a &fManopla de Skor&r, que congela o alvo e solta espinhos de gelo", [c.r_item(pocao("minecraft:strong_healing"), 2)], "Médio: a partir do Ato 3"),
        ("rosalyne", "Rosalyne, Lâmina do Crepúsculo", "meetyourfight:dusk_key", None, "meetyourfight:rosalyne",
         "onde você usar a &fChave do Crepúsculo&r", "Uma cavaleira de flores e espinhos, rápida e elegante. Use a chave (clique direito) num lugar aberto e ela aparece. A chave é gasta ao chamá-la.",
         "a &fFlor Violeta&r", [c.r_item("meetyourfight:dusk_key")], "Difícil: a partir do Ato 4"),
        ("dragao", "Ashlord, o Dragão Infernal", "minecraft:magma_block", "block_factorys_bosses:dragon_tower", "block_factorys_bosses:infernal_dragon",
         "em &fplanícies, selvas ou pântanos&r", "Um dragão de fogo no alto de uma torre, protegido por guardas esqueletos em chamas. Quando a vida dele baixa, ele muda para uma segunda forma ainda maior: afaste-se, beba uma poção e volte.",
         "&fossos de dragão&r para fabricar uma armadura de ossos de dragão", [c.r_item(pocao("minecraft:long_fire_resistance"), 4)], "Difícil: a partir do Ato 4"),
        ("remnant", "O Remanescente Antigo", "minecraft:suspicious_sand", "cataclysm:cursed_pyramid", "cataclysm:ancient_remnant",
         "numa &fpirâmide amaldiçoada no deserto&r", "Uma fera-faraó gigante enterrada na areia. Use o &fpincel&r na &fareia suspeita&r dentro da pirâmide para achar o &fColar do Deserto&r e acordá-la. &cA pirâmide costuma ficar longe: vá de dragão.&r",
         "a &fTempestade de Areia na Garrafa&r e metal antigo", [c.r_item("minecraft:brush")], "Muito difícil: a partir do Ato 5"),
        ("maledictus", "Maledictus", "minecraft:soul_lantern", "cataclysm:frosted_prison", "cataclysm:maledictus",
         "numa &fprisão congelada&r", "Um cavaleiro amaldiçoado selado no gelo. Dê energia de redstone à &fLápide Amaldiçoada&r (uma alavanca ou tocha de redstone ao lado) e clique nela com o botão direito.",
         "o &fLingote de Cursium&r", [c.r_item("minecraft:lever"), c.r_item("minecraft:redstone_torch", 2)], "Muito difícil: depois da história"),
        ("kraken", "Nerakyss, o Kraken", "minecraft:nautilus_shell", "block_factorys_bosses:kraken_ship", "block_factorys_bosses:kraken",
         "no &foceano profundo&r", "Um kraken colossal preso a um navio pirata afundado. Piratas, canhões e tentáculos que saem do chão. Leve blocos, comida e saiba por onde fugir.",
         "o &fDente do Kraken&r para fabricar um tridente que puxa os inimigos", [c.r_item(pocao("minecraft:long_water_breathing"), 4)], "Muito difícil: depois da história"),
    ]
    # Cada fera libera numa etapa da história e dá mais recompensa quanto mais difícil:
    # chave -> (dependência, níveis de XP, diamantes, fragmentos de netherita)
    etapa = {"sandworm": ("inicio", 10, 2, 1), "escultor": ("inicio", 10, 2, 1),
             "lich": ("@ato3/relatorio", 15, 3, 1), "yeti": ("@ato3/relatorio", 15, 3, 1),
             "rosalyne": ("@ato4/relatorio", 18, 3, 2), "dragao": ("@ato4/relatorio", 18, 4, 2),
             "remnant": ("@ato5/selo", 20, 4, 3), "maledictus": ("@ato5/selo", 20, 4, 3),
             "kraken": ("@ato5/selo", 20, 4, 3)}
    onde_fica = {"lich": "do local onde o Lich da Noite vive", "remnant": "do local onde o Remanescente Antigo está"}
    for chave, nome, icone, estrutura, entidade, onde, desc, premio, extra, rec in feras:
        curto = nome.split(',')[0]
        dep, xp, diamantes, sucata = etapa[chave]
        if estrutura:
            rec_mapa = [c.r_localizar(estrutura, f"Coordenadas: {curto}", dimensao=OW)] + extra
            local = onde_fica.get(chave, f"de onde {curto} mora")
            dica = f"&7Pegue a recompensa para ver no chat as coordenadas {local}.&r"
        else:
            rec_mapa = extra
            dica = "&7Pegue a recompensa para receber a chave.&r"
        c.quest(f"{chave}_mapa", f"Caçada: {curto}", 0, 0, icone=icone, deps=[dep], optional=True, subtitulo=rec,
                descricao=[f"&e{nome}&r", "", desc, "", f"Mora {onde}." if estrutura else f"Aparece {onde}.", f"&6{rec}&r", "", dica],
                tarefas=[c.t_check("Pedir a localização" if estrutura else "Quero a chave")],
                recompensas=rec_mapa)
        c.quest(chave, nome, 0, 0, icone=icone, deps=[f"{chave}_mapa"], forma="octagon", tamanho=1.5, optional=True,
                descricao=[f"Derrote &c{nome}&r.", "", f"Pode deixar {premio}."],
                tarefas=[c.t_matar(entidade, 1, f"Derrotar {curto}")],
                recompensas=[c.r_xp(xp), c.r_item("minecraft:diamond", diamantes), c.r_item("minecraft:netherite_scrap", sucata)])

    for n, (chave, *_resto) in enumerate(feras):
        lin, col = divmod(n, 3)
        for q in c.quests:
            if q["id"] == qid(f"cacadas/quest/{chave}_mapa"):
                q["x"], q["y"] = 2.5 + col * 4.0, lin * 2.0
            if q["id"] == qid(f"cacadas/quest/{chave}"):
                q["x"], q["y"] = 4.25 + col * 4.0, lin * 2.0
                q["hide_dependent_lines"] = True
    inicio = next(q for q in c.quests if q["id"] == qid("cacadas/quest/inicio"))
    inicio["x"], inicio["y"] = 0.0, 2.0
    inicio["hide_dependent_lines"] = True

    lamina = item("minecraft:netherite_sword", tag={
        "display": {"Name": json.dumps({"text": "Lâmina do Mestre Caçador", "color": "gold", "italic": False}, ensure_ascii=False),
                    "Lore": [json.dumps({"text": "Só quem derrubou todas as feras antigas a empunha.", "color": "gray"}, ensure_ascii=False)]},
        "Enchantments": [{"id": e, "lvl": Raw(f"{n}s")} for e, n in
                         [("minecraft:sharpness", 5), ("minecraft:looting", 3), ("minecraft:sweeping", 3),
                          ("minecraft:unbreaking", 3), ("minecraft:mending", 1)]]})
    c.quest("mestre", "Mestre Caçador", 0, 0, forma="gear", tamanho=2.0, icone="minecraft:netherite_sword",
            deps=[k for k, *_ in feras], optional=True, subtitulo="Todas as feras derrotadas",
            descricao=[f"{M}: \"Nove feras antigas. Nenhum caçador da Ordem jamais fez isso.\"",
                       "", "&o\"Esta lâmina esperou séculos por alguém como você.\"",
                       "", "&6Recompensa:&r a Lâmina do Mestre Caçador, 3 pontos de habilidade em cada árvore geral (Combate, Mineração e Vida; a árvore da classe não recebe) e o título &6[Mestre Caçador]&r ao lado do seu nome."],
            tarefas=[c.t_check("Receber o título")],
            recompensas=[c.r_item(lamina),
                         c.r_comando("/puffish_skills points add {p} terras_partidas:combate 3", titulo="+3 pontos em Combate", icone="minecraft:iron_sword"),
                         c.r_comando("/puffish_skills points add {p} terras_partidas:mineracao 3", titulo="+3 pontos em Mineração", icone="minecraft:iron_pickaxe"),
                         c.r_comando("/puffish_skills points add {p} terras_partidas:vida 3", titulo="+3 pontos em Vida", icone="minecraft:golden_apple"),
                         c.r_comando("/function terras_partidas:mestre_cacador", titulo="Título [Mestre Caçador]", icone="minecraft:name_tag"),
                         c.r_xp(50)])
    mestre = next(q for q in c.quests if q["id"] == qid("cacadas/quest/mestre"))
    mestre["x"], mestre["y"] = 14.75, 2.0
    return {
        "_manual": True,
        "id": qid("capitulo/cacadas"),
        "group": "",
        "order_index": 5,
        "filename": "cacadas",
        "title": "Caçadas",
        "subtitle": ["Feras antigas, opcionais"],
        "icon": "minecraft:spyglass",
        "default_quest_shape": "",
        "default_hide_dependency_lines": False,
        "quests": c.quests,
    }


# ---------------------------------------------------------------- MESTRE VELLAN (Easy NPC)

VELLAN_PRESET = "terras_partidas:easy_npc/preset/humanoid/mestre_vellan.npc.snbt"
CMD_CHAMAR_VELLAN = f"/easy_npc preset import_new data {VELLAN_PRESET} ~2 ~ ~"
CMD_REMOVER_VELLAN = '/kill @e[type=easy_npc:humanoid,name="Mestre Vellan",distance=..64]'


def tag_ato(n):
    return f"terras_partidas_ato{n}"


TAG_CLASSE = "terras_partidas_classe"
TAG_HELVAR = "terras_partidas_helvar"   # derrotou Helvar: o Mestre oferece o ritual final

# Classes oferecidas pelo Mestre Vellan na primeira conversa: (chave da missão, nome, prós, contras)
CLASSES_VELLAN = [
    ("guerreiro", "Guerreiro",
     "Equilibrado: bom dano, boa vida e armadura. A classe mais fácil para começar.",
     "Não se destaca em nada. Luta sempre de perto."),
    ("tanque", "Tanque",
     "Muita vida e armadura, difícil de derrubar. Começa sabendo aparar golpes com o escudo.",
     "Dano menor: as lutas contra chefes demoram mais."),
    ("assassino", "Assassino",
     "Rápido, com muitos acertos críticos e esquivas. Duas adagas e o passo rápido.",
     "Pouca vida: cada erro custa caro."),
    ("mago", "Mago",
     "Dano de longe com feitiços, inclusive cura. Começa com um livro com 4 feitiços que não são consumidos, mas gastam mana, roupa de mago e Mesa de Inscrição.",
     "Frágil de perto: a roupa de mago protege pouco e cada feitiço gasta mana."),
    ("cacador", "Caçador",
     "Ataca de longe com arco, é seguro contra chefes grandes e se move rápido.",
     "Precisa de flechas e sofre quando é cercado."),
]


def escolha_de_classe(botao, abrir):
    """Diálogos da primeira conversa: o jogador escolhe a classe numa tela, com prós e contras."""
    falas = [{
        "Buttons": [botao(nome, f"ver_{chave}", [abrir(f"classe_{chave}")]) for chave, nome, _, _ in CLASSES_VELLAN]
                   + [botao("Conte a história do Selo", "historia_inicio", [abrir("historia")])],
        "Label": "escolha", "Name": "Escolha seu caminho", "Priority": 1,
        "Texts": [{"Text": "Então você é o novo caçador, @initiator. Sou o Mestre Vellan, da Ordem dos Caçadores.\\n\\n"
                           "O Selo que prendia um mal antigo se partiu, e preciso de você para juntar os fragmentos.\\n\\n"
                           "Mas antes: que tipo de caçador você é? Escolha uma classe para ver os prós e os contras."}],
    }]
    ids = {"chamado": qid("ato1/quest/chamado"), "caminho": qid("ato1/quest/caminho")}
    for chave, nome, pros, contras in CLASSES_VELLAN:
        acoes = [{"Cmd": f"/ftbquests change_progress @initiator complete {ids['chamado']}", "PermLevel": 2, "Type": "COMMAND"},
                 {"Cmd": f"/ftbquests change_progress @initiator complete {ids['caminho']}", "PermLevel": 2, "Type": "COMMAND"},
                 {"Cmd": f"/ftbquests change_progress @initiator complete {qid(f'ato1/quest/{chave}')}", "PermLevel": 2, "Type": "COMMAND"},
                 {"Cmd": f"/puffish_skills category unlock @initiator terras_partidas:{chave}", "PermLevel": 2, "Type": "COMMAND"},
                 {"Cmd": f"/tag @initiator add {TAG_CLASSE}", "PermLevel": 2, "Type": "COMMAND"},
                 # O kit chega pela recompensa automática da missão da classe (completada acima): o Easy NPC
                 # bloqueia "function" em botões de NPC, então o botão não chama a função do kit direto.
                 {"Cmd": "/playsound minecraft:ui.toast.challenge_complete master @initiator ~ ~ ~ 1 1", "PermLevel": 2, "Type": "COMMAND"},
                 abrir("escolhida")]
        falas.append({
            "Buttons": [botao(f"Escolher {nome}", f"escolher_{chave}", acoes),
                        botao("Ver outra classe", f"voltar_{chave}", [abrir("escolha")])],
            "Label": f"classe_{chave}", "Name": nome, "Priority": -1,
            "Texts": [{"Text": f"{nome.upper()}\\n\\nPrós: {pros}\\n\\nContras: {contras}\\n\\n"
                               "A escolha é para sempre. Cada classe tem sua própria árvore de habilidades (tecla K), além das árvores de Combate, Mineração e Vida, que são de todo mundo."}],
        })
    falas.append({
        "Buttons": [botao("Abrir o livro de missões", "livro_escolhida",
                          [{"Type": "CLOSE_DIALOG"},
                           {"Cmd": "/ftbquests open_book", "ExecAsUser": Raw("1b"), "PermLevel": 0, "Type": "COMMAND"}])],
        "Label": "escolhida", "Name": "Caminho escolhido", "Priority": -1,
        "Texts": [{"Text": "Ótima escolha, @initiator.\\n\\n"
                           "Seu kit de classe já está no seu inventário. "
                           "Depois, siga as missões. Eu vou estar por aqui sempre que você quiser conversar."}],
    })
    return falas


def mestre_vellan():
    """Preset do Easy NPC: o Mestre muda o que fala conforme o ato do jogador (tags)."""
    B = Raw("1b")

    def botao(nome, label, acoes):
        return {"Actions": acoes, "Label": label, "Name": nome}

    def abrir(label):
        return {"Cmd": label, "Type": "OPEN_NAMED_DIALOG"}

    botoes = [
        botao("Abrir o livro de missões", "livro",
              [{"Type": "CLOSE_DIALOG"},
               {"Cmd": "/ftbquests open_book", "ExecAsUser": B, "PermLevel": 0, "Type": "COMMAND"}]),
        botao("Conte a história do Selo", "historia_btn", [abrir("historia")]),
        botao("Dicas de combate", "dicas_btn", [abrir("dicas")]),
        botao("Até mais, Mestre", "tchau", [{"Type": "CLOSE_DIALOG"},
                                             {"Msg": {"T": Raw("4b"), "Texts": ["Boa caçada, @initiator."]}, "Type": "MESSAGE"}]),
    ]
    voltar = [botao("Voltar", "voltar", [{"Type": "OPEN_DEFAULT_DIALOG"}])]

    def fala(label, nome, prioridade, texto, tag=None, com_botoes=True):
        d = {"Buttons": botoes if com_botoes else voltar, "Label": label, "Name": nome,
             "Priority": prioridade, "Texts": [{"Text": texto}]}
        if tag:
            d["Conditions"] = [{"Name": tag, "Type": "PLAYER_TAG"}]
        return d

    falas = [
        fala("inicio", "Bem-vindo", 2,
             "Bem-vindo à Ordem dos Caçadores, @initiator.\\n\\n"
             "O Selo se partiu e os fragmentos corromperam criaturas poderosas. Os três primeiros estão nesta região: "
             "algo enorme nos pântanos, um espírito que toca um sino, e um cavaleiro de metal numa câmara no subsolo.\\n\\n"
             "Seu kit já está no inventário, e suas primeiras missões estão no livro de missões. Quando quiser conversar, é só voltar aqui.",
             tag=TAG_CLASSE),
        fala("ato2", "Terras Selvagens", 3,
             "Três fragmentos, @initiator. Melhor do que qualquer caçador em anos.\\n\\n"
             "Os próximos estão longe: no gelo eterno, nas savanas queimadas, no mar congelado e com Dame Fortuna, o espírito que aposta almas. "
             "Use os mapas que eu te der e o planador para atravessar o mundo.",
             tag=tag_ato(1)),
        fala("ato3", "Abismo e Fogo", 4,
             "Sete fragmentos... e os que faltam caíram no Nether, @initiator.\\n\\n"
             "Use ouro na armadura para os piglins te deixarem em paz e leve muitas poções de resistência ao fogo. "
             "As missões do livro mostram as coordenadas de cada lugar no chat, quando você estiver no Nether.",
             tag=tag_ato(2)),
        fala("ato4", "Além do Céu", 5,
             "Onze fragmentos. E agora a verdade: os guardiões do Selo nunca morreram, @initiator.\\n\\n"
             "Eles vivem no Everbright e no Everdawn, acima das nuvens, mas os fragmentos os transformaram em monstros. "
             "Tijolo turquesa abre o caminho para o Everbright. Tijolo lunar, para o Everdawn.",
             tag=tag_ato(3)),
        fala("ato5", "O Fim do Selo", 6,
             "Quinze fragmentos, @initiator. O Selo só pode ser refeito onde foi quebrado: no End.\\n\\n"
             "Encontre a fortaleza escondida, derrote o Dragão e os guardiões do vazio. "
             "E não use a Estrela do Nether do Wither num sinalizador: você vai precisar dela para despertar o que guarda o último fragmento.",
             tag=tag_ato(4)),
        {"Buttons": [
            botao("Restaurar o Selo", "ritual_btn", [
                {"Cmd": "/advancement grant @initiator only terras_partidas:selo_restaurado", "PermLevel": 2, "Type": "COMMAND"},
                {"Cmd": "/tag @initiator add terras_partidas_fim", "PermLevel": 2, "Type": "COMMAND"},
                {"Cmd": "/playsound minecraft:block.beacon.activate master @initiator ~ ~ ~ 1 0.8", "PermLevel": 2, "Type": "COMMAND"},
                {"Cmd": "/playsound minecraft:ui.toast.challenge_complete master @initiator ~ ~ ~ 1 1", "PermLevel": 2, "Type": "COMMAND"},
                {"Cmd": '/title @initiator title {"text":"O Selo foi restaurado","color":"light_purple"}', "PermLevel": 2, "Type": "COMMAND"},
                abrir("restaurado")]),
            botoes[0], botoes[-1]],
         "Conditions": [{"Name": TAG_HELVAR, "Type": "PLAYER_TAG"}],
         "Label": "ritual", "Name": "O ritual", "Priority": 7,
         "Texts": [{"Text": "Você voltou, @initiator. Eu senti Helvar cair daqui.\\n\\n"
                            "Você reuniu os dezenove fragmentos. Eles brilham através do vínculo que a Ordem mantém com o Selo. O núcleo do Arauto é o coração: ele vai no centro, e os outros dezoito em volta dele.\\n\\n"
                            "Aproxime-se do cristal e aperte “Restaurar o Selo”. Eu termino o ritual que começamos há trezentos anos."}]},
        fala("restaurado", "O Selo Restaurado", -1,
             "O cristal brilhou mais forte do que qualquer coisa que eu já vi. Helvar foi puxado de volta para o submundo, e desta vez a porta ficou trancada para sempre.\\n\\n"
             "Os seis guardiões que os fragmentos corromperam finalmente estão livres. Trezentos anos atrás, sete guardiões criaram o Selo. Hoje, um único caçador o refez.\\n\\n"
             "Preciso te contar uma coisa. Eu sou o sétimo guardião. Fiquei neste mundo, escondido na Ordem, esperando alguém forte o bastante para terminar o que começamos.\\n\\n"
             "Obrigado, @initiator. Pegue sua recompensa no livro de missões.",
             com_botoes=False),
        fala("final", "O Selo Restaurado", 8,
             "@initiator... você conseguiu.\\n\\n"
             "Trezentos anos atrás, sete guardiões criaram o Selo. Você enfrentou os seis que os fragmentos corromperam: quatro acima das nuvens e dois no vazio. O sétimo guardião sou eu, e esperei três séculos por alguém como você. "
             "A Ordem nunca vai esquecer o seu nome.\\n\\n"
             "Se ainda quiser lutar, dizem que uma flor do vazio, um leviatã e as feras antigas das Caçadas ainda vagam pelo mundo...",
             tag="terras_partidas_fim"),
        fala("historia", "A história do Selo", -1,
             "Há trezentos anos, um mal antigo ameaçou o mundo. Sete guardiões o prenderam dentro de um cristal: o Selo.\\n\\n"
             "Na última lua cheia, o Selo se partiu. Os fragmentos caíram pelo mundo, e cada um corrompeu a criatura mais forte que encontrou.\\n\\n"
             "Junte todos os fragmentos e o Selo pode ser refeito. Falhe, e o mal desperta.",
             com_botoes=False),
        *escolha_de_classe(botao, abrir),
        fala("dicas", "Dicas de combate", -1,
             "Aperte R para entrar no modo de combate. Sem ele você não esquiva e bate fraco.\\n\\n"
             "Alt esquerdo esquiva, botão direito defende. Aperte K e gaste seus pontos nas árvores de Combate, Mineração e Vida.\\n\\n"
             "Esquivar e defender gasta a barra de fôlego. Não ataque sem parar: espere o inimigo errar e contra-ataque.\\n\\n"
             "Cada chefe derrotado te dá um livro de habilidade. Use o livro (clique direito) para aprender um movimento novo.",
             com_botoes=False),
    ]

    return {
        "PresetMetadata": {
            "author": "SealCraft",
            "category": "Quest",
            "description": "Mestre Vellan, da Ordem dos Caçadores. A fala muda conforme o ato do jogador.",
            "entityTypeId": "easy_npc:humanoid",
            "name": "Mestre Vellan",
            "variantType": "PROFESSOR_01",
            "version": "1.0.0",
        },
        "data": {
            "ActionData": {"ActionEventSet": {"ON_INTERACTION": [{"Type": "OPEN_DEFAULT_DIALOG"}]}},
            "CustomName": json.dumps({"color": "gold", "text": "Mestre Vellan"}, ensure_ascii=False),
            "DialogData": {"DialogDataSet": falas, "Type": "STANDARD"},
            "EasyNPCVersion": 3,
            "HandItems": [{"Count": B, "id": "minecraft:writable_book"}, {}],
            "Invulnerable": B,
            "ObjectiveData": {"ObjectiveDataSet": [{"Type": "LOOK_AT_PLAYER"}, {"Type": "LOOK_AT_RESET"}]},
            "PersistenceRequired": B,
            "VariantType": "PROFESSOR_01",
            "id": "easy_npc:humanoid",
        },
    }


# ---------------------------------------------------------------- GABRIEL (Easy NPC)
# Homenagem a um amigo do autor do pacote: o guardião dos últimos ovos de dragão da Ordem.

TAG_GABRIEL = "terras_partidas_gabriel"   # já disse "Estou pronto"
TAG_VOOU = "terras_partidas_voou"         # completou o Primeiro Voo


def gabriel():
    """Preset do Easy NPC: Gabriel, sério e corajoso. A fala muda depois do primeiro voo."""
    B = Raw("1b")

    def botao(nome, label, acoes):
        return {"Actions": acoes, "Label": label, "Name": nome}

    def abrir(label):
        return {"Cmd": label, "Type": "OPEN_NAMED_DIALOG"}

    def cmd(c):
        return {"Cmd": c, "PermLevel": 2, "Type": "COMMAND"}

    livro = botao("Abrir o livro de missões", "livro",
                  [{"Type": "CLOSE_DIALOG"},
                   {"Cmd": "/ftbquests open_book", "ExecAsUser": B, "PermLevel": 0, "Type": "COMMAND"}])
    pronto = botao("Estou pronto", "pronto_btn",
                   [cmd("/advancement grant @initiator only terras_partidas:falou_gabriel"),
                    cmd(f"/tag @initiator add {TAG_GABRIEL}"),
                    cmd("/playsound minecraft:entity.ender_dragon.growl neutral @initiator ~ ~ ~ 0.4 1.4"),
                    abrir("pronto")])
    dragoes = botao("Como cuidar de um dragão", "dragoes_btn", [abrir("dragoes")])
    historia = botao("Quem é você?", "quem_btn", [abrir("quem")])
    tchau = botao("Até mais, Gabriel", "tchau",
                  [{"Type": "CLOSE_DIALOG"},
                   {"Msg": {"T": Raw("4b"), "Texts": ["Mantenha a cabeça erguida, @initiator."]}, "Type": "MESSAGE"}])
    voltar = botao("Voltar", "voltar", [{"Type": "OPEN_DEFAULT_DIALOG"}])

    def fala(label, nome, prioridade, texto, botoes, tag=None):
        d = {"Buttons": botoes, "Label": label, "Name": nome, "Priority": prioridade, "Texts": [{"Text": texto}]}
        if tag:
            d["Conditions"] = [{"Name": tag, "Type": "PLAYER_TAG"}]
        return d

    falas = [
        fala("inicio", "Gabriel", 1,
             "Então você é o caçador de quem o Mestre Vellan tanto fala.\\n\\n"
             "Eu sou o Gabriel. Há anos guardo os últimos ovos de dragão da Ordem. Já vi caçadores fortes fugirem de um filhote chorando. "
             "Força não basta: um dragão precisa de alguém que fique quando o fogo chegar.\\n\\n"
             "Você derrotou sete criaturas corrompidas pelos fragmentos e não recuou. Isso eu respeito. Está pronto para essa responsabilidade?",
             [pronto, historia, dragoes, tchau]),
        fala("depois", "Gabriel", 2,
             "@initiator. Os ovos continuam seguros, e a sua escolha está no livro de missões.\\n\\n"
             "Se tiver dúvida sobre como cuidar do seu dragão, pergunte. Prefiro responder dez vezes a perder um filhote.",
             [livro, dragoes, historia, tchau], tag=TAG_GABRIEL),
        fala("voou", "Gabriel", 3,
             "Eu vi você no céu, @initiator.\\n\\n"
             "Faz muito tempo que um dragão da Ordem não voava. Os antigos guardiões ficariam orgulhosos, e eu também estou.\\n\\n"
             "Agora vá. O Nether espera, e você não está mais sozinho.",
             [livro, dragoes, historia, tchau], tag=TAG_VOOU),
        fala("pronto", "Estou pronto", -1,
             "Foi o que eu esperava ouvir.\\n\\n"
             "Abra o livro de missões, no capítulo do Ato 2, e escolha um dos quatro ovos: fogo, gelo, água ou floresta. "
             "Escolha com cuidado. Depois que um ovo for escolhido, os outros serão selados para sempre.\\n\\n"
             "Quando ele chocar, cuide dele como cuidaria de um irmão.",
             [livro, dragoes, tchau]),
        fala("dragoes", "Como cuidar de um dragão", -1,
             "Coloque o ovo em cima de um bloco firme e clique nele com o botão direito para ele começar a chocar.\\n\\n"
             "O lugar importa: até chocar, mantenha o ovo perto dos blocos do tipo dele (magma, gelo, prismarinho ou musgo) para ele continuar do tipo escolhido. Nunca leve um dragão de gelo para dentro do Nether: ele não sobrevive ao calor daquele mundo.\\n\\n"
             "Alimente o filhote com carne até ele crescer. Depois coloque a sela e monte. Pular sobe, agachar desce.",
             [voltar]),
        fala("quem", "Quem é você?", -1,
             "Meu pai serviu à Ordem, e o pai dele antes. Quando o Selo foi criado, minha família jurou guardar os ovos dos dragões dos guardiões.\\n\\n"
             "Eu nunca fui o mais forte da Ordem. Mas nunca saí do meu posto, nem quando os monstros cercaram a torre. "
             "Coragem é isso: ficar quando dá vontade de correr.",
             [voltar]),
    ]

    return {
        "PresetMetadata": {
            "author": "SealCraft",
            "category": "Quest",
            "description": "Gabriel, o Guardião dos Dragões. Entrega o ovo de dragão no fim do Ato 2.",
            "entityTypeId": "easy_npc:humanoid",
            "name": "Gabriel",
            "variantType": "KNIGHT_02",
            "version": "1.0.0",
        },
        "data": {
            "ActionData": {"ActionEventSet": {"ON_INTERACTION": [{"Type": "OPEN_DEFAULT_DIALOG"}]}},
            "CustomName": json.dumps({"color": "aqua", "bold": True, "text": "Gabriel"}, ensure_ascii=False),
            "DialogData": {"DialogDataSet": falas, "Type": "STANDARD"},
            "EasyNPCVersion": 3,
            "HandItems": [{"Count": B, "id": "minecraft:iron_sword"}, {"Count": B, "id": "minecraft:shield"}],
            "Invulnerable": B,
            "ObjectiveData": {"ObjectiveDataSet": [{"Type": "LOOK_AT_PLAYER"}, {"Type": "LOOK_AT_RESET"}]},
            "PersistenceRequired": B,
            "SkinData": {"Name": "KNIGHT_02"},
            "VariantType": "KNIGHT_02",
            "id": "easy_npc:humanoid",
        },
    }


# ---------------------------------------------------------------- arquivos

def escrever(caminho, dados):
    caminho = os.path.join(RAIZ, caminho)
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(snbt(dados) + "\n")
    print("escrito:", os.path.relpath(caminho))


def organizar(capitulo, dx=2.0, dy=1.5):
    """Reposiciona as missões da esquerda para a direita, em colunas por etapa.

    O começo do capítulo fica na ponta esquerda e cada coluna é uma etapa a mais.
    As missões de uma coluna seguem a ordem dos pais (média das posições deles),
    o que evita linhas cruzadas e deixa cada frente numa faixa própria.
    """
    qs = capitulo["quests"]
    ids = {q["id"] for q in qs}
    pais = {q["id"]: [d for d in q.get("dependencies", []) if d in ids] for q in qs}
    nivel = {}

    def calc(i):
        if i not in nivel:
            nivel[i] = 1 + max((calc(p) for p in pais[i]), default=-1)
        return nivel[i]

    for q in qs:
        calc(q["id"])
    ordem_gerada = {q["id"]: n for n, q in enumerate(qs)}
    colunas = {}
    for q in qs:
        colunas.setdefault(nivel[q["id"]], []).append(q["id"])
    pos = {}
    for n in sorted(colunas):
        col = colunas[n]
        if n > 0:
            col.sort(key=lambda i: (sum(pos[p] for p in pais[i]) / len(pais[i]) if pais[i] else 0, ordem_gerada[i]))
        for k, i in enumerate(col):
            pos[i] = k - (len(col) - 1) / 2
        # puxa cada missão para perto da média dos pais, sem deixar duas na mesma linha
        if n > 0:
            alvo = [sum(pos[p] for p in pais[i]) / len(pais[i]) if pais[i] else pos[i] for i in col]
            atual = []
            for k, i in enumerate(col):
                y = alvo[k] if not atual else max(alvo[k], atual[-1] + 1)
                atual.append(y)
            desvio = (sum(atual) - sum(alvo)) / len(atual)
            for k, i in enumerate(col):
                pos[i] = atual[k] - desvio
    # Ato longo (mais de 10 etapas) quebra de linha como texto num livro, mas só num ponto de
    # passagem: uma etapa com uma única missão, por onde toda a história passa. Assim nenhuma
    # linha de dependência atravessa a tela.
    ncol = max(nivel.values()) + 1
    inicio_faixa = [0]
    if ncol > 10:
        for col in range(1, ncol):
            ponto_de_passagem = len(colunas[col]) == 1
            # nenhuma ligação pode pular por cima do ponto de quebra
            sem_pulo = not any(nivel[i] > col and any(nivel[p] < col for p in pais[i]) for i in nivel)
            if ponto_de_passagem and sem_pulo and col - inicio_faixa[-1] >= 6 and ncol - col >= 3:
                inicio_faixa.append(col)
    faixa_de = {col: max(k for k, c0 in enumerate(inicio_faixa) if c0 <= col) for col in range(ncol)}
    topo = 0.0
    for f, c0 in enumerate(inicio_faixa):
        membros = [i for i in nivel if faixa_de[nivel[i]] == f]
        ymin = min(pos[i] for i in membros); ymax = max(pos[i] for i in membros)
        for i in membros:
            q = next(q for q in qs if q["id"] == i)
            q["x"] = float((nivel[i] - c0) * dx)
            q["y"] = round((topo + (pos[i] - ymin)) * dy * 2) / 2
        topo += (ymax - ymin) + 2.5
    for q in qs:
        if not pais[q["id"]]:
            q["size"] = 2.0
            q.setdefault("subtitle", "Comece aqui")


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
        "title": "SealCraft",
        "icon": "minecraft:amethyst_shard",
    })
    escrever("chapter_groups.snbt", {"chapter_groups": []})
    capitulos = {"ato1": ato1(), "ato2": ato2(), "ato3": ato3(), "ato4": ato4(), "ato5": ato5(), "cacadas": cacadas()}
    # Marca o jogador ao fim de cada ato: o diálogo do Mestre Vellan usa essas tags.
    marcos = [("ato1", "relatorio", tag_ato(1)), ("ato2", "relatorio", tag_ato(2)),
              ("ato3", "relatorio", tag_ato(3)), ("ato4", "relatorio", tag_ato(4)),
              ("ato5", "selo", "terras_partidas_fim")]
    for cap, chave, tag in marcos:
        alvo = qid(f"{cap}/quest/{chave}")
        quest = next(q for q in capitulos[cap]["quests"] if q["id"] == alvo)
        quest["rewards"].append({"id": qid(f"{cap}/quest/{chave}/recompensa/tag_progresso"), "type": "command",
                                 "command": f"/tag {{p}} add {tag}", "elevate_perms": True, "silent": True,
                                 "title": "O Mestre Vellan registra seu progresso", "icon": "minecraft:writable_book"})
    for cap, capitulo in capitulos.items():
        for q in capitulo["quests"]:
            if q.get("shape") == "octagon" and any(t["type"] == "kill" for t in q["tasks"]):
                q["rewards"].append({"id": qid(f"{q['id']}/recompensa/ponto_habilidade"), "type": "command",
                                     "command": "/function terras_partidas:ponto_de_habilidade",
                                     "elevate_perms": True, "silent": True,
                                     "title": "+1 ponto de habilidade", "icon": "minecraft:enchanted_book"})
    for capitulo in capitulos.values():
        if not capitulo.pop("_manual", False):
            organizar(capitulo)
        escrever(f"chapters/{capitulo['filename']}.snbt", capitulo)
    preset = os.path.join(RAIZ, "..", "..", "openloader", "data", "terras_partidas", "data",
                          "terras_partidas", "easy_npc", "preset", "humanoid", "mestre_vellan.npc.snbt")
    os.makedirs(os.path.dirname(preset), exist_ok=True)
    with open(preset, "w", encoding="utf-8") as f:
        f.write(snbt_mc(mestre_vellan()) + "\n")
    print("escrito:", os.path.relpath(preset))
    preset_g = os.path.join(os.path.dirname(preset), "gabriel.npc.snbt")
    with open(preset_g, "w", encoding="utf-8") as f:
        f.write(snbt_mc(gabriel()) + "\n")
    print("escrito:", os.path.relpath(preset_g))


if __name__ == "__main__":
    main()

# SealCraft

**SealCraft: RPG em Português.** Modpack brasileiro de RPG com combate estilo souls, chefes, dungeons e uma história contada em português.

- **Versão:** Minecraft 1.20.1 com Forge 47.4.29
- **Mods:** 116 no total (97 rodam no servidor e 19 só no jogador), mais 1 pacote de shaders e 1 pacote de animações
- **Objetivo:** ser mais leve que o DawnCraft (305 mods) e rodar bem com 6 GB de RAM
- **Publicação:** textos da página do CurseForge e do Modrinth em `PUBLICACAO.md`
- **Estado:** **história completa**, com 5 atos, 108 missões em português, 19 chefes de história, 2 desafios lendários e dragões. Ainda não foi jogada de ponta a ponta.

**Sobre o nome:** o nome do pacote é SealCraft. O identificador interno continua `terras_partidas` (datapack, funções, tags, árvores de habilidades) para não quebrar mundos e o progresso de quem já está jogando. O jogador não vê esse identificador.

## O que já foi testado

- Um servidor dedicado ligou com todos os mods de servidor em cerca de 35 segundos, gerou o mundo e desligou sem travar.
- As 108 missões carregam sem erro, e o servidor mantém os IDs delas (o progresso dos jogadores não se perde entre atualizações).
- Todos os itens, chefes e estruturas citados nas missões existem nos mods.
- Os 4 mapas do tesouro saem preenchidos, com o X no local certo. Na semente de teste: Câmara Forjada a 450 blocos, Frostmaw a 1.950, navio do Labirinto de Gelo a 1.910 e bosque do Umvuthi a 3.200.
- **Ainda não foi testado:** abrir o jogo no PC (lado do jogador) e jogar as missões de verdade.

## Mods por categoria

**Combate e classes**
Epic Fight, Iron's Spells 'n Spellbooks, Paragliders, Simply Swords, Epic Knights, Pufferfish's Skills (árvore de habilidades), Apotheosis (itens com raridade e atributos)

**Chefes e monstros**
L_Ender's Cataclysm, Bosses'Rise, Mowzie's Mobs, Bosses of Mass Destruction, Aquamirae, Meet Your Fight, Born in Chaos, Illage and Spillage, The Undead Revamped, Mutant Monsters, Alex's Mobs, Creeper Overhaul, Friends&Foes, Deeper and Darker

**Mundo, estruturas e dimensões**
Terralith, Blue Skies (2 dimensões novas), When Dungeons Arise, Dungeons and Taverns, Towns and Towers, Structory, pacote completo do YUNG's (dungeons, minas, fortalezas e templos melhores), Lootr

**História e missões**
FTB Quests (livro de missões), Easy NPC (personagens com diálogo para contar a história)

**Montarias**
Dragon Mounts: Legacy (8 tipos de dragão), Shellback do Aquamirae, Straddler do Alex's Mobs e os cavalos normais

**Facilidades**
JEI, Jade, Xaero's Minimap e World Map, Waystones, Sophisticated Backpacks e Sophisticated Storage (mochilas e baús que podem ser melhorados), Handcrafted (móveis e decoração), Corpse, AppleSkin, Guard Villagers, Farmer's Delight

**Desempenho e visual**
Embeddium, Oculus (shaders), FerriteCore, ModernFix, ImmediatelyFast, Entity Culling, Canary, Saturn, Krypton, Clumps, AI Improvements, AmbientSounds, Sound Physics Remastered

## Ato 1: O Chamado (pronto)

O livro de missões abre pelo botão do FTB Quests no inventário. O Ato 1 tem 23 missões:

1. **O Chamado**: carta do Mestre Vellan explicando a história e o combate do Epic Fight. Dá o livro da esquiva "Rolar".
2. **Escolha seu Caminho**: o jogador escolhe **uma** classe entre 5, e as outras ficam bloqueadas. O kit vai **direto para o inventário**, pela função `terras_partidas:kit/<classe>`. A função roda tanto pelo botão do Mestre Vellan quanto pela recompensa automática da missão, e tem uma trava (`tp_kit_recebido`) contra kit duplicado. Os kits:
   - **Guerreiro**: espada longa, armadura de malha completa e poções de força
   - **Tanque**: escudo, capacete, peitoral e calça de ferro, lança e a técnica Aparar
   - **Assassino**: duas adagas com Afiação I, armadura leve, 3 poções de velocidade, 4 pérolas do End e a esquiva Passo
   - **Mago**: livro de feitiços **já inscrito** com Bola de Fogo II, Míssil Mágico II, Estilhaço de Gelo e Cura, que chega **equipado no espaço do livro** (`curios replace spellbook`), roupa completa de mago andarilho, Mesa de Inscrição e pergaminhos extras. Os feitiços do livro não acabam, só gastam mana. Os pergaminhos soltos são de uso único, a não ser que sejam gravados no livro na Mesa de Inscrição.
   - **Caçador**: arco com Força II, 128 flechas, armadura de couro completa e adaga
3. **Trilha de sobrevivência**: ferramentas de ferro, mochila, dormir numa cama e achar uma vila.
4. **Trilha de combate**: derrotar 10 zumbis e 10 esqueletos.
5. **Os três chefes**, cada um guardando um Fragmento do Selo:
   - **Swampjaw** (Meet Your Fight): o Mestre entrega a Isca Fóssil, que invoca o chefe.
   - **Bellringer** (Meet Your Fight): exige um peitoral de ferro e dá o Sino Assombrado.
   - **Cavaleiro Forjado** (Mowzie's Mobs): o Mestre entrega um **mapa do tesouro** até a Câmara Forjada, no subsolo.

   Cada chefe também dá um livro de habilidade do Epic Fight: **Pulo Fantasma** (pulo duplo), **Técnico** e **Mestre da Espada**.
6. **Relatório ao Mestre**: fecha o ato e dá o planador (Paraglider) pra explorar o Ato 2.

Se o jogador perder a luta, as missões opcionais "Mais uma Isca" e "Outro Sino" trocam ossos ou ouro por outro item de invocação.

## Ato 2: Terras Selvagens (pronto)

Começa depois do relatório do Ato 1. São 26 missões (contando a linha do dragão) divididas em quatro frentes, que podem ser feitas em qualquer ordem. Em três delas o Mestre entrega um **mapa do tesouro** com o X no local do chefe, como no DawnCraft.

| Frente | Como chegar | Chefe | Habilidade ganha |
|---|---|---|---|
| Gelo Eterno | Mapa até o covil, num bioma de neve | Frostmaw (Mowzie's) | Hipervitalidade |
| Savanas Queimadas | Mapa até o bosque dos Umvuthana | Umvuthi (Mowzie's) | Salto Devastador |
| Mar Congelado | Mapa até o Labirinto de Gelo, depois a Concha-Corneta | Capitã Cornelia (Aquamirae) | Ataque Meteoro |
| Mesa da Fortuna | Peitoral de diamante dá a Aposta do Diabo | Dame Fortuna (Meet Your Fight) | Ladrão de Fôlego |

Também tem missões de apoio (mochila de ferro, mesa de encantamento, Waystone própria), uma missão extra contra a Mãe do Labirinto e missões repetíveis pra trocar recursos por outro item de invocação. O relatório final dá obsidiana e isqueiro, preparando o Nether do Ato 3.

**Ovo de dragão:** depois do relatório, o Mestre oferece um ovo e o jogador escolhe **um** entre Fogo, Gelo, Água e Floresta (mod Dragon Mounts: Legacy). Cada ovo vem com blocos do habitat dele, porque o ambiente em volta pode mudar o tipo do dragão, e com sela e carne. A missão final "Primeiro Voo" fecha a linha.

## Ato 3: Abismo e Fogo (pronto)

Começa depois do relatório do Ato 2, no Nether. São 18 missões. No Nether os mapas ficam ilegíveis por causa do teto, então as missões rodam um `/locate` e **mandam as coordenadas no chat** do jogador.

| Frente | Local | Chefe | Habilidade ganha |
|---|---|---|---|
| Forja das Almas | Coordenadas no chat | Monstruosidade de Netherita (Cataclysm) | Resistência |
| Arena Ardente | Coordenadas no chat, depois Cinzas Flamejantes no Altar de Fogo | Ignis (Cataclysm) | Berserker |
| Mão de Ferro | Coordenadas no chat | Manopla do Nether (BOMD) | Fuga de Emergência |
| Chefe final | 3 crânios de esqueleto wither + 4 areias das almas | Wither | Colheita da Morte |

Também tem a fortaleza (com coordenadas), varas de blaze e uma missão extra de netherita. O relatório final anuncia o Ato 4, nas dimensões do Blue Skies.

**Ajustes no mundo para o Ato 3** (no datapack): a Forja das Almas e a Arena Ardente ficam mais perto umas das outras, e a Arena pode nascer em mais biomas do Nether. Na semente de teste, as distâncias ficaram assim:
- **Forja:** caiu de 1.273 para 527 blocos.
- **Arena:** caiu de 1.318 para 782 blocos.
- **Manopla:** 463 blocos (não mudou).
- **Fortaleza:** 1.011 blocos (não mudou).

**Atenção:** o YUNG's Better Fortresses substitui a fortaleza normal. Por isso, missões que procuram fortaleza precisam usar `betterfortresses:fortress`, e não `minecraft:fortress`.

## Ato 4: Além do Céu (pronto)

Começa depois do relatório do Ato 3. São 21 missões nas duas dimensões do Blue Skies. Os quatro chefes são os guardiões originais do Selo, enlouquecidos pelos fragmentos.

**Como entrar:**
- O Mestre entrega um **mapa até a Casa do Guardião do Portal**, o **Isqueiro Zeal** e 16 tijolos de cada tipo.
- O portal tem a mesma moldura do portal do Nether. Pelo código do mod:
  - **Tijolo de Pedra Turquesa** leva ao **Everbright**.
  - **Tijolo de Pedra Lunar** leva ao **Everdawn**.

**Como funciona cada masmorra:** coordenadas no chat, entrar na masmorra, achar a chave num baú, usar a chave na pedra-chave e derrotar o chefe.

| Mundo | Masmorra | Chefe | Habilidade ganha |
|---|---|---|---|
| Everbright | Masmorra Ofuscante | Summoner | Revelação |
| Everbright | Masmorra da Natureza | Starlit Crusher | Força Proibida |
| Everdawn | Masmorra Ofuscante | Alchemist | Pele Adaptativa |
| Everdawn | Masmorra do Veneno | Arachnarch | Vingança |

O relatório final dá 12 olhos do Ender e anuncia o Ato 5, no End. Na semente de teste:
- **Casa do Guardião:** cerca de 1.060 blocos do spawn.
- **Masmorras:** 1.470, 742, 637 e 2.050 blocos dentro das dimensões.

Com o dragão do Ato 2 essas viagens ficam bem mais rápidas.

## Ato 5: O Fim do Selo (pronto)

Começa depois do relatório do Ato 4. São 20 missões: a jornada até o End, dois guardiões do vazio e o chefe final. Depois do final ficam dois desafios lendários opcionais.

| Etapa | Local | Chefe | Habilidade ganha |
|---|---|---|---|
| O Vazio | Fortaleza do End (coordenadas no chat) | Dragão do Ender | Guarda de Impacto |
| Primeiro guardião | Cidadela Arruinada no End (aparece perto do Altar do Vazio) | Guardião do Ender (Cataclysm) | Viciado em Adrenalina |
| Segundo guardião | Arena de Obsidiana no End (Olhos do Ender nos altares) | Obsidilith (BOMD) | Quebra-Ossos |
| Chefe final | Fábrica Antiga no subsolo (acorda com a Estrela do Nether do Wither) | O Arauto / The Harbinger (Cataclysm) | Catarse |
| Desafio lendário | Cavernas verdes | Void Blossom (BOMD) | - |
| Desafio lendário | Cidade Afundada no oceano (Sacrifício Abissal no Altar do Abismo) | O Leviatã (Cataclysm) | - |

Na semente de teste, as distâncias ficaram assim:
- **Fortaleza do End:** 1.488 blocos.
- **Cidadela:** 1.488 blocos, no End.
- **Arena de Obsidiana:** 2.154 blocos, no End.
- **Fábrica Antiga:** 1.329 blocos.
- **Flor do Vazio:** 910 blocos.
- **Cidade Afundada:** 5.543 blocos. É longe, mas é opcional e fica pra depois do final.

**Atenção:** o YUNG's Better Strongholds substitui a fortaleza do End. O ID certo é `betterstrongholds:stronghold`.

## Árvores de habilidades

A tecla **K** abre o **Pufferfish's Skills**, com uma aba para cada árvore.

### Árvores gerais (para todo mundo)

Liberadas desde o começo, para qualquer classe. Cada uma tem um nível próprio e sobe com uma atividade diferente. Cada nível dá 1 ponto, até o nível 20.

| Árvore | Como sobe | Ramos |
|---|---|---|
| **Combate** | Matando monstros | Golpes (dano, perfurar armadura, crítico), Agilidade (velocidade de ataque, alcance, fôlego), Sangue (repulsão, roubo de vida, impacto) |
| **Mineração** | Quebrando blocos. Minérios valem muito mais que pedra. | Picareta (velocidade de mineração), Alcance (alcance de blocos, subir degraus), Sorte (sorte e experiência extra) |
| **Vida** | Comendo e sobrevivendo a dano | Coração (vida, cura recebida), Couro (armadura e resistência), Viajante (velocidade, nado, subir degraus) |

- **Formato:** uma habilidade inicial e 3 ramos de 5 habilidades. A última de cada ramo custa 2 pontos.
- **Tamanho:** 16 habilidades e 19 pontos para completar cada árvore.

### Árvores das classes

Cada classe tem uma árvore própria, que fica trancada até o jogador escolher a classe no Ato 1.
- **Formato:** uma habilidade inicial e 3 ramos de 4 habilidades. A última de cada ramo custa 2 pontos e é mais forte.
- **Tamanho:** 13 habilidades e 16 pontos pra completar cada árvore.
- **Pontos:**
  - **Monstros:** matar dá experiência (XP que o monstro solta + vida máxima / 10). Cada nível vale 1 ponto, até o nível 20.
  - **Chefes:** cada chefe derrotado dá **+1 ponto**, num total de 21 chefes.
  - **Começo:** a árvore começa com 1 ponto, pra comprar a habilidade inicial.

| Classe | Habilidade inicial | Ramos |
|---|---|---|
| Guerreiro | +1 de dano | Força (dano, dano crítico), Vigor (vida, roubo de vida), Ritmo (velocidade de ataque, fôlego, crítico) |
| Tanque | +4 de vida | Couraça (armadura), Firmeza (resistência a empurrão e atordoamento), Vitalidade (vida, cura recebida) |
| Assassino | +5% de velocidade | Lâmina (chance e dano crítico), Sombra (esquiva, velocidade), Fôlego (fôlego máximo e recuperação) |
| Mago | +25 de mana | Poder (poder mágico), Fluxo (recuperação e mana máxima), Pressa (recarga e conjuração) |
| Caçador | +10% de dano de flecha | Pontaria (dano de flecha, crítico), Corda (puxar o arco, velocidade da flecha), Rastreador (velocidade, vida, esquiva) |

As árvores são geradas pelo script `tools/gerar_habilidades.py`, onde ficam todos os nomes e valores. O resultado vai pro datapack em `puffish_skills/`.

## Tradução dos mods (PT-BR)

O pacote de recursos `pack/config/openloader/resources/terras_partidas_ptbr/` traz **11.488 textos traduzidos em 76 mods**. Com o português que os próprios mods já tinham, **100% dos textos** do pacote estão em português. Ele inclui itens, mobs, chefes, conquistas, dicas e as telas do JEI, FTB Quests, mapas do Xaero, Waystones e mochilas.
- **Ativação:** o Open Loader carrega o pacote sozinho, como obrigatório e no topo da lista. O jogador não precisa ativar nada, só jogar com o Minecraft em português.
- **Só o que faltava:** cada arquivo traz só os textos que o mod não tinha em português. O que o mod já trazia continua valendo.
- **Mowzie's Mobs:** o `pt_br.json` do próprio mod está com erro de sintaxe e o Minecraft descarta o arquivo inteiro. O nosso arquivo leva as 230 traduções boas que existiam nele mais as que faltavam.
- **Ajustes por cima do mod:** `tools/traducao_ajustes.json` corrige nomes que vinham ruins no português do mod, como "Acendedor zeloso" virando "Isqueiro Zeal". Também deixa as chaves das masmorras iguais aos nomes usados nas missões.
- **Termos:** os nomes de itens do Minecraft seguem o português oficial do jogo. Os chefes com nome próprio ficam no original (Ignis, Frostmaw, Swampjaw...).
- **Telas técnicas:** também estão traduzidas, incluindo o editor de NPC, ModernFix, Entity Model/Texture Features, Fzzy Config e Structure Gel.
- **Como editar:** mude direto o `assets/<mod>/lang/pt_br.json` do pacote.

## Mestre Vellan no mundo

O Mestre Vellan é um NPC do Easy NPC que **aparece 3 blocos na frente do jogador** (ou 2, ou no lugar do próprio jogador, se tiver bloco no caminho; ver `functions/vellan/aparecer.mcfunction`) uns 3 segundos depois de ele entrar no mundo pela primeira vez, com o título "SealCraft" na tela. Uma conquista invisível (`terras_partidas:primeira_entrada`) dispara as funções em `functions/boas_vindas/`.
- **Escolha de classe:** a primeira conversa é a tela de escolha de classe. Cada classe tem uma página de prós e contras e um botão "Escolher" que:
  - marca como completas as missões "O Chamado", "Escolha seu Caminho" e a da classe;
  - libera a árvore de habilidades;
  - manda o jogador pegar o kit no livro de missões.
- **Pelo livro também funciona:** escolher a classe pelo livro de missões marca a mesma tag (`terras_partidas_classe`), então o Mestre pula a escolha.
- **Conversa:** clique direito nele. A fala muda conforme o ato do jogador, porque cada relatório de ato marca o jogador com a tag `terras_partidas_atoN` (e `terras_partidas_fim` no final).
- **Botões:** abrir o livro de missões, a história do Selo, dicas de combate e despedida.
- **Chamar de novo:** a missão repetível "Chamar o Mestre", no Ato 1, traz ele até o jogador. Se ele estiver perto, só muda de lugar.
- **Arquivos:**
  - **Preset:** `pack/config/openloader/data/terras_partidas/data/terras_partidas/easy_npc/preset/humanoid/mestre_vellan.npc.snbt`, gerado pelo script de missões.
  - **Funções:** `terras_partidas:chamar_vellan` e `terras_partidas:rechamar_vellan`, no mesmo datapack.
- **Por que a invocação passa por uma entidade auxiliar:** se o jogador invocar o preset direto, o Easy NPC trata como importação de um jogador comum e corta o diálogo com comandos e o "olhar pro jogador".
- **Configuração:** `pack/config/easy_npc/security.cfg` libera só o comando `ftbquests` para o botão do livro.

## Tela inicial e teclas

- **Tela inicial:** o pacote de recursos `pack/config/openloader/resources/sealcraft_visual/` troca o logo do Aquamirae (embaixo do "MINECRAFT") pelo logo **SEALCRAFT** e as frases amarelas por 36 frases em português. O logo e o ícone quadrado (`arte/`) são gerados por `tools/gerar_arte.py`.
- **Teclas padrão:** o mod Default Options aplica `pack/config/defaultoptions/keybindings.txt` só na primeira vez que o jogo abre, sem mexer no que o jogador mudar depois.
  - **Shaders:** recarregar fica sem tecla. Antes, o R recarregava os shaders junto com o modo de combate. **F7** liga e desliga.
  - **R:** modo de combate (Epic Fight).
  - **K:** árvores de habilidades.
  - **J:** tela de habilidades do Epic Fight.
  - **Magia:** **V** lança o feitiço escolhido, **Z** abre a roda de feitiços e **Ctrl + rolar o mouse** troca de feitiço. Antes, a roda ficava no R e o modificador no Alt, junto com o modo de combate e a esquiva.

## Chefe final: Helvar, o Cavaleiro do Submundo (Bosses'Rise)

O Arauto (do Cataclysm) era o **carcereiro**: o núcleo dele mantinha trancada a arena onde os sete guardiões prenderam **Helvar**, um cavaleiro que vendeu a alma ao submundo. Com o núcleo arrancado, o jogador precisa entrar antes que ele saia.

- **Missões, no fim do Ato 5:**
  1. A Porta do Submundo: dá as coordenadas da arena.
  2. A Arena do Submundo: a estrutura `block_factorys_bosses:underworld_arena`, no Nether, enterrada perto de Y 31. A recompensa é a **chave da porta**, que a Ordem guardou.
  3. Derrotar Helvar.
  4. O Selo Restaurado.
- **Por que a chave vem da missão:** no mod, a chave só cai com 3% de chance dos esqueletos da arena e 5% nos baús raros. O "gerador de desafio" que daria a chave só existe na versão 1.21 do mod. Sem a missão, o jogador ficaria uns 30 abates na sorte antes do chefe final. A missão repetível "Outra Chave da Arena" troca 8 lingotes de ouro e 16 areias das almas por outra chave.
- **Vida do Helvar:** o mod usa 280 por padrão, menos que o Arauto (390). O arquivo `pack/defaultconfigs/block_factorys_bosses-server.toml` sobe para **450 de vida e 12 de armadura**. O Forge copia esse arquivo para cada mundo novo.
- **O chefe:** uns 8 blocos de altura (colisão de 3 x 5,3). Ele se apresenta, faz combos de espada, abre fendas que disparam fogo e **finge que morre e volta** com fogos-fátuos.
- **Sem cerimônia própria:** derrotar o Helvar completa a missão e libera o fim da história.
- **Imagens:** `arte/chefes_bossesrise/` tem o Helvar, o Ashlord e o Kraken desenhados com o modelo e a textura originais do mod.

## Caçadas (capítulo opcional)

São 9 chefes fora da história, liberados depois do Ato 2 e em ordem de dificuldade. Cada um tem uma missão que mostra as coordenadas no chat (ou dá o item que invoca o chefe) e outra de derrotar, que dá XP, 4 diamantes, 1 fragmento de netherita e +1 ponto de habilidade.

| Chefe (vida) | Mod | Onde | Distância no teste | Recomendado | Deixa |
|---|---|---|---|---|---|
| Sirok, a Minhoca de Areia (200) | Bosses'Rise | desertos | ~2.500 | Ato 2 | Manopla de Sirok |
| Tongbi, o Escultor (140) | Mowzie's | monastério nas montanhas | ~3.200 | Ato 2 | Cajado do Escultor e roupas do Geomante |
| O Lich da Noite (300) | Bosses of Mass Destruction | Torre do Lich, biomas frios | ~1.800 | Ato 3 | Ânima Antiga |
| Skor, o Yeti (250) | Bosses'Rise | Planícies Nevadas | ~1.100 | Ato 3 | Manopla de Skor |
| Rosalyne, Lâmina do Crepúsculo (500) | Meet Your Fight | onde usar a Chave do Crepúsculo (a missão dá a chave) | - | Ato 4 | Flor Violeta |
| Ashlord, o Dragão Infernal (250 + 2ª forma) | Bosses'Rise | torre em planícies, selvas e pântanos | ~2.600 | Ato 4 | ossos de dragão |
| O Remanescente Antigo (450) | Cataclysm | Pirâmide Amaldiçoada (pincel na areia suspeita) | ~6.500 | Ato 5 | Tempestade de Areia na Garrafa |
| Maledictus (420) | Cataclysm | Prisão Congelada (redstone na Lápide Amaldiçoada) | ~2.200 | depois da história | lingote de Cursium |
| Nerakyss, o Kraken (500) | Bosses'Rise | navio no oceano profundo | ~2.500 | depois da história | dente do kraken |

- **Mestre Caçador:** quem derrotar os 9 ganha a Lâmina do Mestre Caçador (netherita com Afiação V, Saque III, Inquebrável III e Remendo), +3 pontos em cada árvore geral, 100 níveis de XP e o título `[Mestre Caçador]` no nome (função `terras_partidas:mestre_cacador`).
- **Torre do Lich:** o mod gera uma a cada 100 chunks (a mais próxima ficava a 3.800 blocos). O datapack muda para 48 chunks.
- **Monastério do Escultor:** só nascia em picos entre as alturas 120 e 200, e as montanhas do Terralith passam disso (ficava a 9.900 blocos). `pack/config/mowziesmobs-common.toml` aceita qualquer montanha entre 90 e 320.
- **Pirâmide Amaldiçoada:** continua longe (~6.500 blocos) mesmo com os desertos do Terralith na lista, porque a posição é decidida por uma regra interna do Cataclysm. A missão avisa para ir de dragão.
- **Desertos do Terralith:** a minhoca só nascia no deserto comum, que o Terralith deixa raro (a mais próxima ficava a 13.000 blocos). O datapack acrescenta os desertos do Terralith em `block_factorys_bosses/tags/worldgen/biome/sandworm_nest.json`.
- **Rolamento do mod:** o Bosses'Rise tem uma esquiva própria (tecla Z, a mesma da roda de feitiços, e um contador de "cargas" com duas setas verdes ao lado da barra de itens). O Epic Fight já tem esquiva (Alt), então o rolamento fica desligado (`defaultconfigs/block_factorys_bosses-server.toml`), a tecla fica sem uso e o contador fica escondido (`config/block_factorys_bosses-client.toml`).
- **Tradução:** os 308 textos do mod estão em `tools/traducao_ajustes.json` e no pacote PT-BR.

## Equilíbrio dos monstros

O script `tools/gerar_equilibrio.py` deixa o começo do jogo mais justo:
- **Monstros dos mods:** o Born in Chaos e o The Undead Revamped colocavam ~850 de peso de nascimento em **todos** os biomas, inclusive Nether e End, contra ~515 dos monstros normais. Só ~37% dos monstros eram os normais. O script sobrescreve os arquivos de nascimento dos dois mods no datapack: peso x 0,35 (de 851 para 298) e só no mundo normal.
- **Bomber (Undead Revamped):** a explosão dava 1000 de dano (morte na hora). Agora dá 24.
- **Mutantes:** de 5% para 1,5% do nascimento do monstro normal.
- **Apotheosis:** monstros com equipamento de elite de 7,5% para 4%, e chefes aleatórios mais raros (chance de 1,8% para 0,8% e no mínimo 10 minutos entre um e outro).
- **Missão "Como Ficar Mais Forte" (Ato 1):** explica o modo de combate, a esquiva, a defesa, as árvores de habilidades e o que evitar. Dá 1 ponto nas árvores de Combate e Vida e um escudo.

## Layout do livro de missões

As posições das missões são calculadas pelo gerador (`organizar()` em `tools/gerar_missoes.py`), sempre no mesmo padrão, como texto num livro:
- **Sentido:** o começo de cada ato fica em cima à esquerda, maior e com o subtítulo "Comece aqui", e a história segue para a direita. As missões de cada frente ficam numa linha própria.
- **Ato longo** (mais de 10 etapas, hoje só o Ato 5): quebra para a linha de baixo, mas só num ponto de passagem, uma etapa com uma única missão por onde toda a história passa. Assim nenhuma ligação atravessa a tela.
- **Caçadas:** posições próprias, numa grade de 3 por 3 com cada mapa ao lado da sua fera e o Mestre Caçador no fim. As linhas do início e das feras até o Mestre ficam escondidas.

## Visual: shaders e animações

- **Shaders:** o **Complementary Reimagined** já vem instalado e ligado num perfil novo. Ele deixa a água, o céu, as nuvens, as sombras e as luzes bem mais bonitos.
  - **Desligar:** aperte **F7**, ou vá em **Opções > Configurações de vídeo > Pacotes de shaders** e escolha "Desligado". Lá dá pra baixar a qualidade se o PC sofrer.
  - **Configuração:** `pack/config/oculus.properties` vem direto no pacote. Antes ela vinha pelo Default Options, mas o Oculus cria o arquivo antes e o shader ficava desligado.
- **Aviso de "recursos experimentais":** o Minecraft mostra esse aviso em todo mundo com geração de terreno de mods (Terralith, dimensões, estruturas). Não é erro. O mod Experimental Settings Disabler esconde o aviso.
- **Fresh Animations:** pacote de recursos que anima os monstros e animais normais (piscar, respirar, andar de verdade). Fica ativo por padrão (`pack/config/defaultoptions/options.txt`) e pode ser tirado em **Opções > Pacotes de recursos**.
- **Os dois são só do lado do jogador.** O servidor não baixa nenhum deles.

## A história

> Há trezentos anos, sete guardiões criaram o **Selo**, um cristal que prendia um mal antigo. O Selo se partiu, os fragmentos caíram pelo mundo e corromperam criaturas poderosas. O **Mestre Vellan**, da Ordem dos Caçadores, recruta o jogador para recuperar os 19 fragmentos.

A história vai se revelando ato por ato:
- **Atos 1 a 3:** o jogador recupera fragmentos no mundo normal e no Nether, até despertar o Wither.
- **Ato 4:** descobre que os guardiões originais nunca morreram, mas enlouqueceram nos mundos acima das nuvens.
- **Ato 5:** descobre que o mal antigo era uma máquina de guerra, o Arauto, cujo núcleo virou o último fragmento. Derrotar o Arauto completa o Selo.

| Ato | Missões | Fragmentos | Chefes |
|---|---|---|---|
| 1. O Chamado | 23 | 3 | Swampjaw, Bellringer, Cavaleiro Forjado |
| 2. Terras Selvagens | 26 | 4 | Frostmaw, Umvuthi, Capitã Cornelia, Dame Fortuna |
| 3. Abismo e Fogo | 18 | 4 | Monstruosidade de Netherita, Ignis, Manopla do Nether, Wither |
| 4. Além do Céu | 21 | 4 | Summoner, Starlit Crusher, Alchemist, Arachnarch |
| 5. O Fim do Selo | 20 | 4 | Dragão do Ender, Guardião do Ender, Obsidilith, O Arauto |

## Próximos passos

1. Jogar no PC de ponta a ponta e ajustar o que pesar, bugar ou ficar desequilibrado.
2. Colocar o Mestre Vellan no mundo como NPC (Easy NPC).
5. Configurar dificuldade, drops e o bloqueio de progressão.

## Para quem mexe no pacote

O pacote é gerenciado com o [packwiz](https://packwiz.infra.link/), e cada mod é um arquivo `.pw.toml` em `pack/mods/`.

Adicionar um mod pelo link do CurseForge:

```bash
cd pack && packwiz curseforge add https://www.curseforge.com/minecraft/mc-mods/NOME-DO-MOD
```

Gerar o arquivo `.zip` para importar no app do CurseForge:

```bash
cd pack && packwiz curseforge export
```

**Missões:** são geradas pelo script `tools/gerar_missoes.py`, onde ficam todos os textos. Para mudar uma missão, edite o script e rode:

```bash
python3 tools/gerar_missoes.py
```

Não edite as missões pelo modo de edição dentro do jogo: o script sobrescreve essas mudanças na próxima vez que rodar.

**Ajustes de mundo:** ficam no datapack `pack/config/openloader/data/terras_partidas/`, carregado pelo mod Open Loader. Ele libera as estruturas do Mowzie's Mobs (chefes) nos biomas do Terralith, define os mapas do tesouro (`loot_tables/mapas/`) que as missões entregam e aproxima as estruturas de chefe do Cataclysm no Nether.

**Todos os mods vêm do CurseForge** (desde a 0.16.0): o zip exportado só tem referências, sem nenhum `.jar` dentro, que é o que o CurseForge exige para aprovar um modpack. Alguns mods não são achados pelo nome no `packwiz curseforge add`. Nesse caso, use o link da página, por exemplo `https://www.curseforge.com/minecraft/mc-mods/illage-and-spillage-finally-ported`.

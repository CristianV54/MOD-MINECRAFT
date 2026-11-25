# Terras Partidas (nome provisório)

Modpack brasileiro de RPG com combate estilo souls, chefes, dungeons e uma história contada em português.

- **Versão:** Minecraft 1.20.1 com Forge 47.4.29
- **Mods:** 108 no total (89 rodam no servidor e 19 só no jogador)
- **Objetivo:** ser mais leve que o DawnCraft (305 mods) e rodar bem com 6 GB de RAM
- **Estado:** base de mods pronta e testada. As missões e a história ainda vão ser escritas.

## O que já foi testado

- Um servidor dedicado ligou com todos os mods de servidor em cerca de 35 segundos, gerou o mundo e desligou sem travar.
- **Ainda não foi testado:** abrir o jogo no PC (lado do jogador). Esse teste precisa ser feito em um computador com Minecraft.

## Mods por categoria

**Combate e classes**
Epic Fight, Iron's Spells 'n Spellbooks, Paragliders, Simply Swords, Epic Knights, Pufferfish's Skills (árvore de habilidades), Apotheosis (itens com raridade e atributos)

**Chefes e monstros**
L_Ender's Cataclysm, Mowzie's Mobs, Bosses of Mass Destruction, Aquamirae, Meet Your Fight, Born in Chaos, Illage and Spillage, The Undead Revamped, Mutant Monsters, Alex's Mobs, Creeper Overhaul, Friends&Foes, Deeper and Darker

**Mundo, estruturas e dimensões**
Terralith, Blue Skies (2 dimensões novas), When Dungeons Arise, Dungeons and Taverns, Towns and Towers, Structory, pacote completo do YUNG's (dungeons, minas, fortalezas e templos melhores), Lootr

**História e missões**
FTB Quests (livro de missões), Easy NPC (personagens com diálogo para contar a história)

**Facilidades**
JEI, Jade, Xaero's Minimap e World Map, Waystones, Sophisticated Backpacks, Corpse, AppleSkin, Guard Villagers, Farmer's Delight

**Desempenho e visual**
Embeddium, Oculus (shaders), FerriteCore, ModernFix, ImmediatelyFast, Entity Culling, Canary, Saturn, Krypton, Clumps, AI Improvements, AmbientSounds, Sound Physics Remastered

## Rascunho da história

> Há séculos, sete guardiões selaram um mal antigo dentro de um cristal: o **Selo**. O Selo se partiu, os fragmentos se espalharam pelo mundo e cada um corrompeu uma criatura poderosa. A **Ordem dos Caçadores** recruta você para recuperar os fragmentos antes que o mal desperte.

O **Mestre da Ordem**, um NPC criado com o Easy NPC, dá as missões principais. Cada ato termina com um chefe que guarda um fragmento do Selo. Recursos como bigorna, mesa de encantamento, Nether e End vão sendo liberados conforme a história avança, como o DawnCraft faz com o "Conhecimento".

| Ato | Tema | Chefes (mod de origem) |
|---|---|---|
| 1. O Chamado | Começo, cavernas e vilas | Ferrous Wroughtnaut (Mowzie's), Bellringer (Meet Your Fight), Lord Pumpkinhead (Born in Chaos) |
| 2. Terras Selvagens | Gelo, savana e mar | Frostmaw e Umvuthi (Mowzie's), Dame Fortuna (Meet Your Fight), Capitã Cornelia (Aquamirae) |
| 3. Abismo e Fogo | Nether e profundezas | Netherite Monstrosity e Ignis (Cataclysm), Nether Gauntlet e Night Lich (BOMD) |
| 4. Além do Céu | Dimensões do Blue Skies | Summoner, Alchemist, Starlit Crusher, Arachnarch (Blue Skies) |
| 5. O Fim do Selo | End e chefe final | Ender Guardian (Cataclysm), Obsidilith e Void Blossom (BOMD), Dragão do End, The Leviathan ou Harbinger (Cataclysm) |

**Classes (escolhidas na primeira missão):** Guerreiro, Tanque, Assassino, Mago e Caçador. Cada uma ganha um kit inicial e um ramo próprio na árvore de habilidades.

A ordem dos chefes e os nomes dos atos ainda são rascunho e podem mudar.

## Próximos passos

1. Testar no PC e ajustar o que pesar ou bugar.
2. Escrever as missões do Ato 1 em português (FTB Quests) e criar o Mestre da Ordem (Easy NPC).
3. Montar as classes e a árvore de habilidades.
4. Fazer a tradução PT-BR dos mods que não têm português.
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

**Observação:** 5 mods vêm do Modrinth (Illage and Spillage, Dungeons and Taverns, The Undead Revamped, Entity Culling e Pufferfish's Skills). O `.zip` exportado leva esses mods dentro. Isso não é problema para jogar com amigos, mas antes de publicar no CurseForge é preciso trocar esses mods pela versão do CurseForge ou conferir se eles estão liberados lá.

# Auditoria do Terras Partidas (versão 0.8.1)

Auditoria do caminho completo do jogador, do nascimento no mapa até o final do Ato 5. Foi feita num servidor dedicado com o pacote, num mundo novo com a semente `12345`.

## Como foi feita

Não dá pra abrir o Minecraft com tela neste ambiente, então ninguém "jogou" de verdade. A auditoria cobre tudo que dá pra verificar sem um jogador:

1. **Lógica das missões:** um script simula completar as missões em ordem, respeitando dependências e escolhas únicas, e vê se todas são alcançáveis.
2. **Itens:** cada item pedido por uma missão precisa ter receita ou fonte conhecida (monstro, chefe ou baú).
3. **Comandos:** os 26 comandos das recompensas foram executados no servidor como a missão faria, usando uma entidade no lugar do jogador.
4. **Mundo:** cada estrutura, bioma e dimensão citado foi localizado no mundo de teste a partir do spawn.
5. **Mecânicas dos chefes:** como cada chefe é invocado foi conferido lendo o código dos mods, e não por memória.

## Resultado

| Verificação | Resultado |
|---|---|
| Missões carregam no servidor | 109 de 109 |
| IDs se mantêm depois de o servidor salvar | 0 trocados |
| Missões alcançáveis numa jogada | 102. As 7 restantes são as alternativas de escolha única: 4 classes e 3 ovos de dragão. |
| Dependências quebradas | 0 |
| Itens, chefes, estruturas e biomas citados que existem nos mods | todos |
| Comandos de recompensa que funcionam | 26 de 26 |
| Mapas do tesouro preenchidos com o X certo | 5 de 5 |
| Livros de habilidade em categorias que podem ser aprendidas | 22 de 22 |
| Mestre Vellan aparece com diálogo completo | sim, e "chamar de novo" não duplica |

## O caminho, passo a passo (semente de teste)

| Etapa | Onde | Distância |
|---|---|---|
| Nascer | X 96, Z -32, em terra firme | - |
| Ato 1: vila | mundo normal | 275 blocos |
| Ato 1: Câmara Forjada | mundo normal, subsolo | 417 blocos |
| Ato 2: covil do Frostmaw | mundo normal | ~1.950 |
| Ato 2: navio no Labirinto de Gelo | mundo normal | ~1.910 |
| Ato 2: bosque do Umvuthi | mundo normal | ~3.200 |
| Ato 3: Forja das Almas | Nether | 527 |
| Ato 3: Arena Ardente | Nether | 782 |
| Ato 3: Arena da Manopla | Nether | 463 |
| Ato 3: fortaleza | Nether | ~1.011 |
| Ato 4: Casa do Guardião | mundo normal | ~1.060 |
| Ato 4: masmorras | Everbright e Everdawn | 637 a 2.050 |
| Ato 5: fortaleza do End | mundo normal | ~1.500 |
| Ato 5: Cidadela e Arena de Obsidiana | End | ~1.100 a ~2.150 |
| Ato 5: Fábrica Antiga (chefe final) | mundo normal, subsolo | ~700 a ~1.300 |
| Lendário: Flor do Vazio | mundo normal | ~640 a ~910 |
| Lendário: Cidade Afundada | oceano | ~5.500 |

Algumas estruturas variaram entre um teste e outro, por isso aparecem como faixa ou com "~".

## Problemas encontrados e corrigidos

**Corrigidos nesta auditoria:**
- **"Outra Corneta" (Ato 2):** pedia cristais de prismarinho, que só vêm de guardiões ou lanternas do mar. Agora pede 6 lingotes de ouro.
- **"Varas de Blaze" (Ato 3):** não levava a lugar nenhum e contava como pendente no capítulo. Agora é opcional.
- **Obsidilith (Ato 5):** o texto falava em "altares", mas a arena tem **um** altar. Corrigido.
- **Estrela do Nether (Ato 5):** se o jogador usasse a estrela num sinalizador, ficava sem saber como seguir. As missões agora explicam que é preciso invocar outro Wither.

**Corrigidos durante a criação dos atos**, encontrados pelos testes:
- **Fortalezas:** o YUNG's substitui a fortaleza do Nether e a do End. As missões usavam os IDs normais e nunca iam completar.
- **Labirinto de Gelo:** o bioma do Aquamirae não aparece com o Terralith. A missão agora aceita o grupo de biomas que a Concha-Corneta usa.
- **Chefes do Mowzie's:** quase não iam nascer nos biomas do Terralith. Um datapack libera.
- **Nether:** a Forja e a Arena estavam a mais de 1.200 blocos. A "semente" original da Arena travava a posição dela. Ajustado no datapack.
- **Portal do Blue Skies:** o texto dizia que a casa tinha dois portais. Pelo código, cada dimensão usa um tijolo diferente.
- **Progresso dos jogadores:** o FTB Quests trocava IDs que começam com 8 a F, o que apagaria o progresso a cada atualização.
- **Mestre Vellan:** invocado direto pelo jogador, ele perdia diálogo e comandos. Agora é invocado por uma entidade auxiliar.

## O que só um teste jogando de verdade vai mostrar

- **Desempenho no PC:** quanto o pacote pesa no lado do jogador (os 19 mods visuais e de interface não rodam no servidor).
- **Equilíbrio das lutas:** se os kits e recompensas bastam pra cada chefe, principalmente Ignis, Wither e o Arauto.
- **Telas:** o diálogo do Mestre Vellan e o botão que abre o livro de missões.
- **Portal do Blue Skies:** se a moldura 4x5 acende com o Isqueiro Zeal.
- **Dragão:** quanto tempo o ovo leva pra chocar e o filhote pra crescer.
- **Textos:** se as cores e as quebras de página das missões ficam boas na tela.

### Roteiro sugerido para o primeiro teste

1. Crie um mundo novo e pegue a recompensa de "O Chamado". O Mestre Vellan deve aparecer ao seu lado.
2. Clique nele e teste os 4 botões.
3. Escolha uma classe e confira o kit.
4. Use a Isca Fóssil e lute com o Swampjaw.
5. Pegue o mapa da Câmara Forjada e veja se o X aparece.
6. Anote o FPS e o uso de memória (F3).

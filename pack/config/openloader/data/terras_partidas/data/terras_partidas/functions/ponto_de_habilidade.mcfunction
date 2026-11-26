# +1 ponto de habilidade por chefe derrotado. Vai para todas as árvores,
# mas só a árvore da classe escolhida fica liberada para o jogador.
puffish_skills points add @s terras_partidas:guerreiro 1
puffish_skills points add @s terras_partidas:tanque 1
puffish_skills points add @s terras_partidas:assassino 1
puffish_skills points add @s terras_partidas:mago 1
puffish_skills points add @s terras_partidas:cacador 1
tellraw @s {"text":"+1 ponto de habilidade! Aperte K para abrir sua árvore de habilidades.","color":"gold"}

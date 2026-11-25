# Invoca o Mestre Vellan ao lado de quem rodou a função.
# Usa um marcador (entidade invisível) como origem para o Easy NPC tratar como importação do servidor
# e manter o diálogo, os botões e o "olhar para o jogador".
summon minecraft:marker ~ ~ ~ {Tags:["tp_vellan_spawn"]}
execute as @e[type=minecraft:marker,tag=tp_vellan_spawn,limit=1,sort=nearest] at @s run easy_npc preset import_new data terras_partidas:easy_npc/preset/humanoid/mestre_vellan.npc.snbt ~2 ~ ~
kill @e[type=minecraft:marker,tag=tp_vellan_spawn]

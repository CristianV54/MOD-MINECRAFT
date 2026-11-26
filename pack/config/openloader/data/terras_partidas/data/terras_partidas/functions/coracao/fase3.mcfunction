scoreboard players set @s tp_cs_fase 3
effect give @s minecraft:speed infinite 0 true
effect give @s minecraft:strength infinite 0 true
title @a[distance=..64] times 5 50 15
title @a[distance=..64] subtitle {"text":"Ele está desesperado. Não pare agora!","color":"gray"}
title @a[distance=..64] title {"text":"O Coração racha","color":"red"}
playsound minecraft:block.amethyst_cluster.break hostile @a[distance=..64] ~ ~ ~ 1 0.5
particle minecraft:dragon_breath ~ ~1 ~ 1.5 1 1.5 0.05 150

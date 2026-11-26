# Executado como o chefe, já na posição de destino (2 blocos atrás do jogador).
execute at @s run particle minecraft:portal ~ ~1 ~ 0.3 0.8 0.3 0.4 60
tp @s ~ ~ ~ facing entity @p
particle minecraft:reverse_portal ~ ~1 ~ 0.3 0.8 0.3 0.05 50
playsound minecraft:entity.enderman.teleport hostile @a[distance=..32] ~ ~ ~ 1 0.6
title @a[distance=..6] actionbar {"text":"O Coração apareceu atrás de você!","color":"light_purple"}

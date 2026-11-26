particle minecraft:sonic_boom ~ ~1 ~ 0 0 0 0 1
particle minecraft:explosion ~ ~0.5 ~ 2.5 0.3 2.5 0 12
playsound minecraft:entity.warden.sonic_boom hostile @a[distance=..32] ~ ~ ~ 1 1.2
execute as @a[distance=..5,gamemode=!creative,gamemode=!spectator] run damage @s 9 minecraft:magic by @e[type=minecraft:wither_skeleton,tag=coracao_selo,limit=1,sort=nearest]
effect give @a[distance=..5] minecraft:slowness 3 1

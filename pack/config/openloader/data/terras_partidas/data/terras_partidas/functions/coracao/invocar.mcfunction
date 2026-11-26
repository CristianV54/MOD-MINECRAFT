summon minecraft:wither_skeleton ~ ~ ~ {Tags:["coracao_selo"],CustomName:'{"text":"O Coração do Selo","color":"light_purple","bold":true}',CustomNameVisible:1b,PersistenceRequired:1b,Health:500f,Attributes:[{Name:"minecraft:generic.max_health",Base:500d},{Name:"minecraft:generic.armor",Base:10d},{Name:"minecraft:generic.armor_toughness",Base:4d},{Name:"minecraft:generic.attack_damage",Base:11d},{Name:"minecraft:generic.movement_speed",Base:0.29d},{Name:"minecraft:generic.knockback_resistance",Base:1d},{Name:"minecraft:generic.follow_range",Base:64d}],HandItems:[{id:"epicfight:netherite_longsword",Count:1b,tag:{Enchantments:[{id:"minecraft:fire_aspect",lvl:1s}]}},{}],HandDropChances:[0f,0f],ArmorItems:[{id:"minecraft:netherite_boots",Count:1b,tag:{Trim:{material:"minecraft:amethyst",pattern:"minecraft:ward"},AttributeModifiers:[]}},{id:"minecraft:netherite_leggings",Count:1b,tag:{Trim:{material:"minecraft:amethyst",pattern:"minecraft:ward"},AttributeModifiers:[]}},{id:"minecraft:netherite_chestplate",Count:1b,tag:{Trim:{material:"minecraft:amethyst",pattern:"minecraft:ward"},AttributeModifiers:[]}},{id:"minecraft:netherite_helmet",Count:1b,tag:{Trim:{material:"minecraft:amethyst",pattern:"minecraft:ward"},AttributeModifiers:[]}}],ArmorDropChances:[0f,0f,0f,0f]}
scoreboard players set @e[type=minecraft:wither_skeleton,tag=coracao_selo,distance=..1] tp_cs_fase 1
scoreboard players set @e[type=minecraft:wither_skeleton,tag=coracao_selo,distance=..1] tp_cs_ciclo 100
scoreboard players set #luta tp_cs_vida 1
scoreboard players set #ultimo tp_cs_vida 500
bossbar add terras_partidas:coracao {"text":"O Coração do Selo","color":"light_purple","bold":true}
bossbar set terras_partidas:coracao color purple
bossbar set terras_partidas:coracao style notched_10
bossbar set terras_partidas:coracao max 500
bossbar set terras_partidas:coracao value 500
particle minecraft:explosion_emitter ~ ~1 ~ 0 0 0 0 1
particle minecraft:dragon_breath ~ ~1 ~ 1 1 1 0.05 120
playsound minecraft:entity.wither.spawn hostile @a[distance=..64] ~ ~ ~ 1 1.2
title @a[distance=..64] times 10 50 15
title @a[distance=..64] subtitle {"text":"O mal que o Selo prendia","color":"gray"}
title @a[distance=..64] title {"text":"O Coração do Selo","color":"light_purple","bold":true}

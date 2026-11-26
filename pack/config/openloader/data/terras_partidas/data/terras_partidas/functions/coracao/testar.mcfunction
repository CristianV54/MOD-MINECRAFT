# Para testar sem jogar até o Ato 5 (precisa de cheats): /function terras_partidas:coracao/testar
advancement revoke @s only terras_partidas:selo_restaurado
item replace entity @s armor.head with minecraft:netherite_helmet{Enchantments:[{id:"minecraft:protection",lvl:4s}]}
item replace entity @s armor.chest with minecraft:netherite_chestplate{Enchantments:[{id:"minecraft:protection",lvl:4s}]}
item replace entity @s armor.legs with minecraft:netherite_leggings{Enchantments:[{id:"minecraft:protection",lvl:4s}]}
item replace entity @s armor.feet with minecraft:netherite_boots{Enchantments:[{id:"minecraft:protection",lvl:4s}]}
give @s minecraft:netherite_sword{Enchantments:[{id:"minecraft:sharpness",lvl:5s}]}
give @s minecraft:golden_apple 8
give @s minecraft:cooked_beef 16
tellraw @s {"text":"Teste do chefe final: o Coração do Selo desperta em 5 segundos.","color":"yellow"}
function terras_partidas:coracao/despertar

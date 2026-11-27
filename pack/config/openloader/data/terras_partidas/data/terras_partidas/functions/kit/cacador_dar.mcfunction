# Kit da classe Caçador. Gerado por tools/gerar_missoes.py.
tag @s add tp_kit_recebido
give @s minecraft:bow{ Enchantments:[ { id:"minecraft:power", lvl:2s } ] } 1
give @s minecraft:arrow 64
give @s minecraft:arrow 64
give @s epicfight:iron_dagger 1
give @s minecraft:leather_helmet 1
give @s minecraft:leather_chestplate 1
give @s minecraft:leather_leggings 1
give @s minecraft:leather_boots 1
give @s minecraft:cooked_beef 12
playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1
tellraw @s ["",{"text":"[Mestre Vellan] ","color":"gold"},{"text":"Seu kit de classe está no seu inventário.","color":"white"}]

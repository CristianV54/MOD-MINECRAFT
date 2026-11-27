# Kit da classe Mago. Gerado por tools/gerar_missoes.py.
tag @s add tp_kit_recebido
execute store success score @s tp_espera run curios replace spellbook 0 @s with irons_spellbooks:copper_spell_book{ ISB_Spells:{ data:[ { id:"irons_spellbooks:firebolt", index:0, level:2, locked:0b }, { id:"irons_spellbooks:magic_missile", index:1, level:2, locked:0b }, { id:"irons_spellbooks:icicle", index:2, level:1, locked:0b }, { id:"irons_spellbooks:heal", index:3, level:1, locked:0b } ], maxSpells:5, mustEquip:1b, spellWheel:1b } }
execute unless score @s tp_espera matches 1 run give @s irons_spellbooks:copper_spell_book{ ISB_Spells:{ data:[ { id:"irons_spellbooks:firebolt", index:0, level:2, locked:0b }, { id:"irons_spellbooks:magic_missile", index:1, level:2, locked:0b }, { id:"irons_spellbooks:icicle", index:2, level:1, locked:0b }, { id:"irons_spellbooks:heal", index:3, level:1, locked:0b } ], maxSpells:5, mustEquip:1b, spellWheel:1b } }
scoreboard players set @s tp_espera 0
give @s irons_spellbooks:wandering_magician_helmet 1
give @s irons_spellbooks:wandering_magician_chestplate 1
give @s irons_spellbooks:wandering_magician_leggings 1
give @s irons_spellbooks:wandering_magician_boots 1
give @s irons_spellbooks:inscription_table 1
give @s irons_spellbooks:scroll{ ISB_Spells:{ data:[ { id:"irons_spellbooks:shield", index:0, level:1, locked:1b } ], maxSpells:1, mustEquip:0b, spellWheel:0b } } 1
give @s irons_spellbooks:scroll{ ISB_Spells:{ data:[ { id:"irons_spellbooks:wisp", index:0, level:1, locked:1b } ], maxSpells:1, mustEquip:0b, spellWheel:0b } } 1
give @s minecraft:cooked_beef 12
playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1
tellraw @s ["",{"text":"[Mestre Vellan] ","color":"gold"},{"text":"Seu kit de classe está no seu inventário.","color":"white"}]
tellraw @s ["",{"text":"[Mestre Vellan] ","color":"gold"},{"text":"Seu livro de feitiços já está equipado. Aperte ","color":"white"},{"text":"V","color":"yellow"},{"text":" para lançar e ","color":"white"},{"text":"Z","color":"yellow"},{"text":" para trocar de feitiço. Eles não acabam: só gastam mana.","color":"white"}]

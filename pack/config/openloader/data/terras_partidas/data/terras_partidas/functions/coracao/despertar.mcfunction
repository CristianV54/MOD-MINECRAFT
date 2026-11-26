# Chamado pela recompensa automática da missão do Arauto (ou pela missão de chamar de novo).
# Não faz nada se o jogador já derrotou o Coração.
execute unless entity @s[advancements={terras_partidas:selo_restaurado=true}] unless entity @s[tag=tp_cs_despertar] unless entity @e[type=minecraft:wither_skeleton,tag=coracao_selo] run function terras_partidas:coracao/despertar_iniciar

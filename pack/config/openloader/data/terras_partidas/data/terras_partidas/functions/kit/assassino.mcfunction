# Entrega o kit só uma vez (a missão e o Mestre Vellan chamam esta mesma função).
execute unless entity @s[tag=tp_kit_recebido] run function terras_partidas:kit/assassino_dar

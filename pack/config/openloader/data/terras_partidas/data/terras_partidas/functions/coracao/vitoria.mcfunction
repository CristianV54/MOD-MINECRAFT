# Conquista (quem matou) ou reserva da vigia. Vale para todos que estavam na luta.
scoreboard players set #luta tp_cs_vida 0
bossbar remove terras_partidas:coracao
kill @e[type=minecraft:zombie,tag=sombra_selo]
tag @s add tp_cs_lutador
advancement grant @a[tag=tp_cs_lutador] only terras_partidas:selo_restaurado
scoreboard players set @a[tag=tp_cs_lutador] tp_cs_t 0
tag @a[tag=tp_cs_lutador] add tp_cs_vitoria
tag @a remove tp_cs_lutador

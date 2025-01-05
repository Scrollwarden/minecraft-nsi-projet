'''
Ce fichier contiens les paramètres de BLOCKY DUNGEONS 
modifiables à la disposition du joueur.
'''
import mcpi.block as block

SKIP_MONOLOGUE = False

DUNGEON_SIZE = 10
ROOM_SIZE = 21 # ce nombre doit être IMPAIR

WALL_BLOCK = block.COBBLESTONE
FLOOR_BLOCK = block.STONE_BRICK
ROOF_BLOCK = block.STONE
WOOD_BLOCK = block.WOOD_PLANKS


# DANGER ZONE : MODIFIER LES PARAMÈTRES SUIVANTS PEUT CAUSER DES BUGS (cf README.md)
ROOM_WIDTH = ROOM_SIZE
ROOM_DEPTH = ROOM_SIZE
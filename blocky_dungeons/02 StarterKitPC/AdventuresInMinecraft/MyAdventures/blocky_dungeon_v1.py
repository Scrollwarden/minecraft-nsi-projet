'''
Generate a random dungeon
'''

import mcpi.minecraft as minecraft
import mcpi.block as block
import mcpi.entity as entity
import random
import time

from dungeons_settings import *

mc = minecraft.Minecraft.create()

ENTITY_BOSS_LIST = (entity.WITHER_SKELETON, entity.ILLUSIONER, entity.ENDERMAN, entity.EVOKER)
ENTITY_MONSTER_LVL1_LIST = (entity.ZOMBIE, entity.SKELETON, entity.SLIME, entity.SPIDER)
ENTITY_MONSTER_LVL2_LIST = (entity.CAVE_SPIDER, entity.STRAY, entity.HUSK, entity.SILVERFISH, entity.MAGMA_CUBE)
ENTITY_MONSTER_LVL3_LIST = (entity.VEX, entity.VINDICATOR, entity.BLAZE)

class Room:
    '''
    Une salle du donjon.
    Les salles mesurent au minimum 15×15×6 blocs. Des valeurs inférieures peuvent causer des générations étranges.
    
    INPUT
    - pos (tuple[int, int, int]) : coordonnées du centre de la salle
    - width (int) : largeur de la salle
    - height (int) : hauteur de la salle (plafond)
    - depth (int) : profondeur de la salle
    - entrance (tuple[int, int, int]) : coordonnées de l'entrée de la salle par laquelle elle a été générée. Précisée car cette porte DOIS exister. Elle DOIT IMPERATIVEMENT être l'une des 4 coordonnées possibles.
    - is_spawn (bool) : indique si la salle est la salle de départ du donjon.
    '''
    ROOM_THEMES = ('winter', 'hell', 'forest')
    ROOM_TYPES = ('normal', 'normal', 'normal', 'bridge', 'bridge', 'boss') # kewords repeated for probabilities
    ROOM_TAGS = ('monster', 'trap', 'treasure', 'locked', 'one exit')
    ROOM_LEVELS = (1, 2, 3)

    def __init__(self, pos, width, height, depth, entrance, is_spawn=False):
        self.center = pos
        self.width = width
        self.height = height
        self.depth = depth
        self.generation_points = [] # les endroits à partir desquels d'autres salles seront générées

        self.pos_entrance = entrance
        
        x, y, z = self.center
        self.pos_doors = [
            (x+width//2, y, z),
            (x-width//2, y, z),
            (x, y, z+depth//2),
            (x, y, z-depth//2)
        ]
        self.pos_doors.remove(self.pos_entrance)
        self.pos_stuff = (
            (x, y+1, z),
            (x+width//2-5, y+1, z+depth//2-5),
            (x-width//2+5, y+1, z+depth//2-5),
            (x+width//2-5, y+1, z-depth//2+5),
            (x-width//2+5, y+1, z-depth//2+5)
        )

        self.theme = random.choice(self.ROOM_THEMES)
        self.type = 'spawn' if is_spawn else random.choice(self.ROOM_TYPES)
        self.tags = 'special' if self.type in ('boss', 'spawn') else random.sample(self.ROOM_TAGS, random.randint(1, 3))
        self.level = random.choice(self.ROOM_LEVELS)
        self.orientation = None # l'orientation n'a d'importance que pour bridge
        if self.type == 'bridge':
            if self.pos_entrance[0] == x:
                self.orientation = 'z'
            elif self.pos_entrance[2] == z:
                self.orientation = 'x'
            else:
                print('entrance was incorrect, selected x for orientation.')
                self.orientation = 'x'

        self.liquid_block = block.ICE if self.theme == 'winter' else block.LAVA if self.theme == 'hell' else block.WATER
    
    def yield_generation_point(self):
        """
        Renvoie un point de la pièce à partir duquel une autre pièce se générer.
        Sous forme de tuple ((x, y, z), 'direction')

        ATTENTION : Ce tuple donne la position de la porte pour la nouvelle pièce, pas la porte de la pièce actuelle.
        """
        for point in self.generation_points:
            if point[0] < self.center[0]:
                yield ((point[0]-1, point[1], point[2]), '+x')
            elif point[0] > self.center[0]:
                yield ((point[0]+1, point[1], point[2]), '-x')
            elif point[2] < self.center[2]:
                yield ((point[0], point[1], point[2]-1), '+z')
            elif point[2] > self.center[2]:
                yield ((point[0], point[1], point[2]+1), '-z')

    def generate(self):
        """Créé la salle"""
        self.clear_area()
        self.generate_floor()
        self.generate_walls()
        self.generate_roof()
        if 'treasure' in self.tags:
            self.generate_treasures()
        if 'trap' in self.tags:
            self.generate_traps()
        if 'monster' in self.tags or self.type == 'boss':
            self.summon_monsters()
        self.generate_enhancements()
        self.generate_doors()
        # mc.player.setPos(*self.pos_entrance)
        print('room generated.')

    def clear_area(self):
        """Vide l'espace où la pièce va être créée"""
        x, y, z = self.center
        mc.setBlocks(x-self.width//2, y, z-self.depth//2,
                     x+self.width//2, y+self.height, z+self.depth//2,
                     block.AIR)
        
    def place_ground_safe(self, x, y, z):
        """Génère une zone de blocs pour servir de bases aux objets potentiellement générés au dessus des lacs"""
        mc.setBlocks(x-1, y, z-1, x+1, y, z+1, block.STONE_BRICK)
        mc.setBlocks(x-1, y-10, z-1, x+1, y-1, z+1, block.MOSS_STONE)
        
    def generate_roof(self):
        """Génère le plafond de la pièce"""
        x, y, z = self.center
        mc.setBlocks(x-self.width//2, y+self.height, z-self.depth//2,
                     x+self.width//2, y+self.height+1, z+self.depth//2,
                     ROOF_BLOCK)

    def generate_floor(self):
        """Génère le sol de la pièce"""
        x, y, z = self.center
        if self.type == "bridge":
            mc.setBlocks(x-self.width//2, y-2, z-self.depth//2,
                         x+self.width//2, y, z+self.depth//2,
                         block.AIR)
            mc.setBlocks(x-self.width//2, y-2, z-self.depth//2,
                         x+self.width//2, y-1, z+self.depth//2,
                         self.liquid_block)
            bridge_block = block.STONE if self.theme == 'hell' else WOOD_BLOCK
            i, j, k = self.pos_entrance
            if self.orientation == 'x':
                mc.setBlocks(*self.pos_doors[0],
                             i, j, k+1,
                             bridge_block)
            else:
                mc.setBlocks(*self.pos_doors[2],
                             i+1, j, k,
                             bridge_block)
        elif self.type == 'normal':
            mc.setBlocks(x-self.width//2, y-11, z-self.depth//2,
                         x+self.width//2, y, z+self.depth//2,
                         FLOOR_BLOCK)
            for quart in range(4):
                if random.randint(0, 100) < 20:
                    self.generate_lake(quart)
        else:
            mc.setBlocks(x-self.width//2, y, z-self.depth//2,
                         x+self.width//2, y, z+self.depth//2,
                         FLOOR_BLOCK)
            if self.type == 'spawn':
                mc.setBlock(x, y, z, block.GLOWSTONE_BLOCK)
            
    def generate_lake(self, quart):
        """Génère un lac sur le quart <quart> du sol"""
        x, y, z = self.center

        liquid = self.liquid_block if random.randint(1, 100) < 25 else block.AIR
        # probabilité d'avoir une fosse très profonde plutôt qu'un lac

        if quart == 0:
            mc.setBlocks(x-self.width//2, y-10, z-self.depth//2,
                         x-2, y, z-2,
                         block.AIR)
            mc.setBlocks(x-self.width//2, y-2, z-self.depth//2,
                         x-2, y-1, z-2,
                         liquid)
        elif quart == 1:
            mc.setBlocks(x-self.width//2, y-10, z+self.depth//2,
                         x-2, y, z+2,
                         block.AIR)
            mc.setBlocks(x-self.width//2, y-2, z+self.depth//2,
                         x-2, y-1, z+2,
                         liquid)
        elif quart == 2:
            mc.setBlocks(x+self.width//2, y-10, z-self.depth//2,
                         x+2, y, z-2,
                         block.AIR)
            mc.setBlocks(x+self.width//2, y-2, z-self.depth//2,
                         x+2, y-1, z-2,
                         liquid)
        elif quart == 3:
            mc.setBlocks(x+self.width//2, y-10, z+self.depth//2,
                         x+2, y, z+2,
                         block.AIR)
            mc.setBlocks(x+self.width//2, y-2, z+self.depth//2,
                         x+2, y-1, z+2,
                         liquid)
        
    def generate_walls(self):
        """Génère les murs de la pièce"""
        x, y, z = self.center
        mc.setBlocks(x-self.width//2, y-10, z-self.depth//2,
                     x+self.width//2, y+self.height, z-self.depth//2,
                     WALL_BLOCK)
        mc.setBlocks(x-self.width//2, y-10, z-self.depth//2,
                     x-self.width//2, y+self.height, z+self.depth//2,
                     WALL_BLOCK)
        mc.setBlocks(x+self.width//2, y-10, z-self.depth//2,
                     x+self.width//2, y+self.height, z+self.depth//2,
                     WALL_BLOCK)
        mc.setBlocks(x-self.width//2, y-10, z+self.depth//2,
                     x+self.width//2, y+self.height, z+self.depth//2,
                     WALL_BLOCK)
        
    def generate_doors(self):
        """Génère les portes de la pièce"""
        print('Started door generation')
        if self.type == 'spawn':
            self.place_door(*self.pos_entrance)
        else:
            self.place_door(*self.pos_entrance, is_entrance=True)
        if self.type == "bridge":
            if self.orientation == 'x':
                self.place_door(*self.pos_doors[0])
            else:
                self.place_door(*self.pos_doors[2])
        elif 'one exit' in self.tags:
            self.place_door(*self.pos_doors[random.randint(0, 2)])
        elif self.type == 'spawn':
            for door in self.pos_doors:
                self.place_door(*door)
        else:
            for door in self.pos_doors:
                if random.randint(1, 100) < 50:
                    self.place_door(*door)
            
    def place_door(self, x, y, z, is_entrance=False):
        """
        Place une double porte dans le mur
        """
        self.generation_points.append((x, y, z))
        print('door opened')
        if z == self.center[2]:
            # orienté z
            mc.setBlocks(x, y+1, z, x, y+2, z+1, block.AIR)
            if not is_entrance:
                if 'locked' in self.tags:
                    mc.setBlock(x, y+1, z, block.DOOR_IRON.id, 2) # left close
                    mc.setBlock(x, y+2, z, block.DOOR_IRON.id, 10)
                    mc.setBlock(x, y+1, z+1, block.DOOR_IRON.id, 2)
                    mc.setBlock(x, y+2, z+1, block.DOOR_IRON.id, 10)
                else:
                    mc.setBlock(x, y+1, z, block.DOOR_WOOD.id, 2) # left close
                    mc.setBlock(x, y+2, z, block.DOOR_WOOD.id, 10)
                    mc.setBlock(x, y+1, z+1, block.DOOR_WOOD.id, 2)
                    mc.setBlock(x, y+2, z+1, block.DOOR_WOOD.id, 10)
        else:
            # orienté x
            mc.setBlocks(x, y+1, z, x+1, y+2, z, block.AIR)
            if not is_entrance:
                if 'locked' in self.tags:
                    mc.setBlock(x, y+1, z, block.DOOR_IRON.id, 1) # left close
                    mc.setBlock(x, y+2, z, block.DOOR_IRON.id, 9)
                    mc.setBlock(x+1, y+1, z, block.DOOR_IRON.id, 1)
                    mc.setBlock(x+1, y+2, z, block.DOOR_IRON.id, 9)
                else:
                    mc.setBlock(x, y+1, z, block.DOOR_WOOD.id, 1) # left close
                    mc.setBlock(x, y+2, z, block.DOOR_WOOD.id, 9)
                    mc.setBlock(x+1, y+1, z, block.DOOR_WOOD.id, 1)
                    mc.setBlock(x+1, y+2, z, block.DOOR_WOOD.id, 9)

    def generate_treasures(self):
        """Génère des trésors dans la pièce"""
        block_treasure_list = (block.GOLD_BLOCK, block.DIAMOND_BLOCK, block.EMERALD_ORE)
        for place in self.pos_stuff:
            x, y, z = place
            if not ((x, y-1, z) == self.center and self.type == 'bridge'): # pas de coffre au milieu du pont
                if random.randint(0, 100) < 50:
                    self.place_chest_with_stuff(x, y, z)
                elif random.randint(0, 100) < 75:
                    mc.setBlock(x, y, z, random.choice(block_treasure_list))
                    self.place_ground_safe(x, y-1, z)

    def place_chest_with_stuff(self, x, y ,z):
        """
        DOESN'T WORK ENTIERLY BECAUSE MCPI
        
        Place un coffre avec des trésors dedans.
        """
        # pas de méthode permettant de remplir le coffre. Pas de hopper ni spawn item pour les remplir en trichant un peu.
        mc.setBlock(x, y, z, block.CHEST)
        self.place_ground_safe(x, y-1, z)

    def generate_traps(self):
        """
        DOESN'T WORK ENTIERLY BECAUSE MCPI

        Génère des pièges dans la pièce
        """
        trap_list = ('cobweb', 'pit', 'pit', 'lava fall', 'lava fall') # reduced probability for cobweb because worst one.
        # abandonné : anvil (no entity falling anvil), tnt floor (no block pressure plate), tnt chest (no trapped chest), shulker (mc.spawnEntity doesn't work)
        type_piege = random.sample(trap_list, random.randint(1, 2))
        if 'cobweb' in type_piege:
            self.place_cobweb_trap()
        if 'pit' in type_piege:
            self.place_pit_trap()
        if 'lava fall' in type_piege:
            self.place_lavafall_trap()

    def place_cobweb_trap(self):
        """
        DOESN'T WORK ENTIERLY BECAUSE MCPI

        Place des toiles d'araignées dans la pièce (le piège le plus insuportable)
        """
        # spawnEntity ne fonctionne pas...
        x, y, z = self.center
        x -= self.width//2-1
        y += 1
        z -= self.depth//2-1
        for i in range(self.width-1):
            for j in range(self.depth-1):
                for k in range(self.height-1):
                    if random.randint(0, 100) < 25:
                        mc.setBlock(x+i, y+k, z+j, block.COBWEB)
        # mc.spawnEntity(x, y+2*(self.height//3), z, entity.CAVE_SPIDER)

    def place_pit_trap(self):
        """Place des trous dans la pièce, devant les portes"""
        for door in self.pos_doors:
            x, y, z = door
            if x < self.center[0]:
                mc.setBlocks(x+1, y, z, x+1, y-5, z+1, block.AIR)
                mc.setBlocks(x+1, y-6, z, x+1, y-6, z+1, block.NETHERRACK)
                mc.setBlocks(x+1, y-5, z, x+1, y-5, z+1, block.FIRE)
            elif x > self.center[0]:
                mc.setBlocks(x-1, y, z, x-1, y-5, z+1, block.AIR)
                mc.setBlocks(x-1, y-6, z, x-1, y-6, z+1, block.NETHERRACK)
                mc.setBlocks(x-1, y-5, z, x-1, y-5, z+1, block.FIRE)
            elif z < self.center[2]:
                mc.setBlocks(x, y, z+1, x+1, y-5, z+1, block.AIR)
                mc.setBlocks(x, y-6, z+1, x+1, y-6, z+1, block.NETHERRACK)
                mc.setBlocks(x, y-5, z+1, x+1, y-5, z+1, block.FIRE)
            elif z > self.center[2]:
                mc.setBlocks(x, y, z-1, x+1, y-5, z-1, block.AIR)
                mc.setBlocks(x, y-6, z-1, x+1, y-6, z-1, block.NETHERRACK)
                mc.setBlocks(x, y-5, z-1, x+1, y-5, z-1, block.FIRE)

    def place_lavafall_trap(self):
        """pose des chutes de lave dans la pièce devant les portes"""
        for door in self.pos_doors:
            x, y, z = door
            if x < self.center[0]:
                mc.setBlocks(x+1, y+self.height, z, x+1, y+self.height, z+1, block.LAVA)
                time.sleep(1.5) # pour laisser à la lave le temps de s'écouler
                mc.setBlocks(x+1, y+self.height, z, x+1, y+self.height, z+1, ROOF_BLOCK)
            elif x > self.center[0]:
                mc.setBlocks(x-1, y+self.height, z, x-1, y+self.height, z+1, block.LAVA)
                time.sleep(1.5)
                mc.setBlocks(x-1, y+self.height, z, x-1, y+self.height, z+1, ROOF_BLOCK)
            elif z < self.center[2]:
                mc.setBlocks(x, y+self.height, z+1, x+1, y+self.height, z+1, block.LAVA)
                time.sleep(1.5)
                mc.setBlocks(x, y+self.height, z+1, x+1, y+self.height, z+1, ROOF_BLOCK)
            elif z > self.center[2]:
                mc.setBlocks(x, y+self.height, z-1, x+1, y+self.height, z-1, block.LAVA)
                time.sleep(1.5)
                mc.setBlocks(x, y+self.height, z-1, x+1, y+self.height, z-1, ROOF_BLOCK)
    
    def generate_enhancements(self):
        """place des décorations dans la pièce"""
        decor_functions_list = (self.place_fire, self.place_pillar, self.place_cuve, self.place_fall)

        if self.type == 'boss':
            x, y, z = self.center
            self.place_boss_fall(x, y, z)
        if self.type == 'spawn' or self.type == 'boss':
            generate_deco = random.choice(decor_functions_list)
            for place in self.pos_stuff:
                x, y, z = place
                if (x, y-1, z) != self.center:
                    generate_deco(x, y, z)
        else:
            for place in self.pos_stuff:
                x, y, z = place
                if True: #if mc.getBlock(x, y, z) == block.AIR.id: # bridge crash source
                    if random.randint(0, 100) < 50:
                        if self.type == 'normal':
                            generate_deco = random.choice(decor_functions_list)
                        else:
                            generate_deco = self.place_fall
                        generate_deco(x, y, z)
        if 'locked' in self.tags:
            x, y, z = self.pos_stuff[random.randint(1, 4)] # centre exclu
            mc.setBlocks(x, y+self.height-1, z, x, y+self.height+1, z, ROOF_BLOCK) # pour boucher les chutes de liquide
            self.place_ground_safe(x, y-1, z)
            mc.setBlock(x, y, z, block.TORCH_REDSTONE.id, 5) # permet d'ouvrir une porte en fer

    def place_boss_fall(self, x, y, z):
        """place des chutes de liquide autour du centre de la salle"""
        mc.setBlocks(x- self.width//3, y-1, z+self.depth//3,
                        x+ self.width//3, y+self.height+1, z+self.depth//3,
                        self.liquid_block)
        mc.setBlocks(x-2, y, z+self.depth//3,
                        x+2, y+self.height+1, z+self.depth//3,
                        block.AIR)
        mc.setBlocks(x- self.width//3, y-1, z-self.depth//3,
                        x+ self.width//3, y+self.height+1, z-self.depth//3,
                        self.liquid_block)
        mc.setBlocks(x-2, y, z-self.depth//3,
                        x+2, y+self.height+1, z-self.depth//3,
                        block.AIR)
        mc.setBlocks(x+self.width//3, y-1, z- self.depth//3,
                        x+self.width//3, y+self.height+1, z+ self.depth//3,
                        self.liquid_block)
        mc.setBlocks(x+self.width//3, y, z-2,
                        x+self.width//3, y+self.height+1, z+2,
                        block.AIR)
        mc.setBlocks(x-self.width//3, y-1, z- self.depth//3,
                        x-self.width//3, y+self.height+1, z+ self.depth//3,
                        self.liquid_block)
        mc.setBlocks(x-self.width//3, y, z-2,
                        x-self.width//3, y+self.height+1, z+2,
                        block.AIR)

    def place_fire(self, x, y, z):
        """créé un pilier-flambeau avec du feu en haut"""
        self.place_ground_safe(x, y-1, z)
        mc.setBlock(x+1, y, z, block.STAIRS_COBBLESTONE.id, 1)
        mc.setBlock(x-1, y, z, block.STAIRS_COBBLESTONE.id, 0)
        mc.setBlock(x, y, z+1, block.STAIRS_COBBLESTONE.id, 3)
        mc.setBlock(x, y, z-1, block.STAIRS_COBBLESTONE.id, 2)
        mc.setBlock(x, y+1, z, block.STONE_BRICK, 3)
        mc.setBlock(x, y+2, z, block.NETHERRACK)
        mc.setBlock(x+1, y+2, z, block.STAIRS_COBBLESTONE.id, 5)
        mc.setBlock(x-1, y+2, z, block.STAIRS_COBBLESTONE.id, 4)
        mc.setBlock(x, y+2, z+1, block.STAIRS_COBBLESTONE.id, 7)
        mc.setBlock(x, y+2, z-1, block.STAIRS_COBBLESTONE.id, 6)
        mc.setBlock(x, y+3, z, block.FIRE)

    def place_pillar(self, x, y, z):
        """place un pilier de soutien du sol au plafond"""
        self.place_ground_safe(x, y-1, z)
        mc.setBlock(x+1, y, z, block.STAIRS_SANDSTONE.id, 1)
        mc.setBlock(x-1, y, z, block.STAIRS_SANDSTONE.id, 0)
        mc.setBlock(x, y, z+1, block.STAIRS_SANDSTONE.id, 3)
        mc.setBlock(x, y, z-1, block.STAIRS_SANDSTONE.id, 2)
        for i in range(self.height-2):
            mc.setBlock(x, y+1+i, z, block.NETHER_BRICK)
        mc.setBlock(x+1, y+self.height//2, z, block.TORCH.id, 1)
        mc.setBlock(x-1, y+self.height//2, z, block.TORCH.id, 2)
        mc.setBlock(x, y+self.height//2, z+1, block.TORCH.id, 3)
        mc.setBlock(x, y+self.height//2, z-1, block.TORCH.id, 4)
        mc.setBlock(x+1, y+self.height-2, z, block.STAIRS_SANDSTONE.id, 5)
        mc.setBlock(x-1, y+self.height-2, z, block.STAIRS_SANDSTONE.id, 4)
        mc.setBlock(x, y+self.height-2, z+1, block.STAIRS_SANDSTONE.id, 7)
        mc.setBlock(x, y+self.height-2, z-1, block.STAIRS_SANDSTONE.id, 6)

    def place_cuve(self, x, y, z):
        """place une cuve de liquide"""
        self.place_ground_safe(x, y-1, z)
        mc.setBlock(x+1, y, z, block.STAIRS_COBBLESTONE.id, 1)
        mc.setBlock(x-1, y, z, block.STAIRS_COBBLESTONE.id, 0)
        mc.setBlock(x, y, z+1, block.STAIRS_COBBLESTONE.id, 3)
        mc.setBlock(x, y, z-1, block.STAIRS_COBBLESTONE.id, 2)
        mc.setBlock(x, y, z, self.liquid_block)
        mc.setBlock(x, y-1, z, block.GLOWSTONE_BLOCK)

    def place_fall(self, x, y, z):
        """place une chute de liquide"""
        if not (self.type == 'bridge' and (x, y-1, z) == self.center):
            mc.setBlocks(x, y-1, z, x, y+self.height-1, z, block.AIR)
            mc.setBlock(x, y+self.height-1, z, self.liquid_block)
            if self.theme == 'winter':
                mc.setBlocks(x, y-11, z, x, y+self.height-1, z, self.liquid_block)

    def summon_monsters(self):
        """
        DOESN'T WORK BECAUSE MCPI

        Fait apparaître des monstres dans la pièce
        """
        # spawnEntity ne fonctionne pas...
        x, y, z = self.center
        y += 1

        if self.type == 'boss':
            monster = random.choice(ENTITY_BOSS_LIST)
            nb = 1
        elif self.level == 1:
            monster = random.choice(ENTITY_MONSTER_LVL1_LIST)
            nb = 4
        elif self.level == 2:
            monster = random.choice(ENTITY_MONSTER_LVL2_LIST)
            nb = 3
        elif self.level == 3:
            monster = random.choice(ENTITY_MONSTER_LVL3_LIST)
            nb = 2
        
        for _ in range(nb):
            # mc.spawnEntity(x, y, z, monster)
            pass
        print(f'{nb} {monster.name} would have spawned if mcpi was working.')


class Dungeon:
    '''
    Le donjon génère plusieurs salles liées entre-elles.
    Ces salles finissent soit en cul-e-sac soit en sortie.
    Il est possible qu'un donjon n'ai aucune sortie.
    Dans ce cas, vous êtes condamnés à y périr.

    INPUTS
    - x, y, z : coordonnées du centre de la salle d'apparition
    - average_size : taille moyenne du donjon
    '''
    SPAWN_ROOM_SIZE = ROOM_SIZE # la salle d'apparition est toujours carrée

    def __init__(self, x, y, z, average_size=10):
        self.x = x
        self.y = y
        self.z = z
        self.average_size = average_size
        self.generated_rooms = []
        
    def generate(self):
        """Créé le donjon"""
        spawn_room = self.generate_spawn_room()
        self.generate_random_rooms(spawn_room, 0)
        print('DONE : Dungeon generated.')
    
    def generate_random_rooms(self, current_room:Room, nb_rooms):
        """
        Génère de manière récursive des salles aléatoirement jusqu'à atteindre le nombre de salles souhaité.
        """
        if nb_rooms >= self.average_size:
            print('The room is an exit room')
            self.turn_to_end_room(current_room)
            return None # on arrête le programme
        
        for door in current_room.yield_generation_point():
            door_direction = door[1]
            door_pos = door[0]
            new_room_size = ROOM_SIZE # pour l'instant toutes les salles sont pareilles (c'est plus facile pour avoir les portes au bon endroit)
            if door_direction == '-x':
                new_room_center = (door_pos[0] + new_room_size//2, door_pos[1], door_pos[2])
            elif door_direction == '+x':
                new_room_center = (door_pos[0] - new_room_size//2, door_pos[1], door_pos[2])
            elif door_direction == '-z':
                new_room_center = (door_pos[0], door_pos[1], door_pos[2] + new_room_size//2)
            elif door_direction == '+z':
                new_room_center = (door_pos[0], door_pos[1], door_pos[2] - new_room_size//2)
            else:
                raise ValueError("Direction de porte invalide")
            
            # print(self.generated_rooms, new_room_center)
            if not new_room_center in self.generated_rooms:
                new_room = Room(new_room_center, new_room_size, random.randint(6, 10), new_room_size, door_pos)
                print('Generating room', new_room.type.upper(), new_room.tags, 'with theme', new_room.theme)
                new_room.generate()
                self.generated_rooms.append(new_room.center)
                nb_rooms += 1
                self.generate_random_rooms(new_room, nb_rooms+1)
            else:
                print('Room not generated : place already taken')

    def turn_to_end_room(self, last_room:Room):
        """Transforme la pièce en cul-de-sac et laisse potentiellement une porte ouverte vers l'extérieur."""
        for door in last_room.yield_generation_point():
            x, y, z = door[0]
            door_direction = door[1]
            if random.randint(0, 100) < 75:
                # on vérifie la présence de blocs de pierre pour savoir s'il y a accès à une salle ou à l'extérieur
                if door_direction == '-x' and not mc.getBlock(x, y, z) == FLOOR_BLOCK.id:
                    mc.setBlocks(x-1, y, z, x-1, y+2, z+1, block.STONE_BRICK)
                elif door_direction == '+x' and not mc.getBlock(x, y, z) == FLOOR_BLOCK.id:
                    mc.setBlocks(x+1, y, z, x+1, y+2, z+1, block.STONE_BRICK)
                elif door_direction == '-z' and not mc.getBlock(x, y, z) == FLOOR_BLOCK.id:
                    mc.setBlocks(x, y, z-1, x+1, y+2, z-1, block.STONE_BRICK)
                elif door_direction == '+z' and not mc.getBlock(x, y, z) == FLOOR_BLOCK.id:
                    mc.setBlocks(x, y, z+1, x+1, y+2, z+1, block.STONE_BRICK)
        
    def generate_spawn_room(self):
        """
        Salle d'apparition. Le joueur se trouve au milieu au début.
        """
        size = self.SPAWN_ROOM_SIZE
        spawn_room = Room((self.x, self.y, self.z), size, 6, size, (self.x-size//2, self.y, self.z), is_spawn=True)
        print('Generating spawn room', spawn_room.type.upper(), spawn_room.tags, 'with theme', spawn_room.theme)
        spawn_room.generate()
        self.generated_rooms.append(spawn_room.center)
        return spawn_room



def evil_monologue():
    """
    Tout bon donjon commence par un bon vieux monologue typique du maître du donjon qui se moque de ses victimes, pas vrai ?
    """
    print('staring monologue')
    mc.postToChat("(evil deep voice) Vous voila. pauvre mortel. enferme dans mon terrible donjon !")
    time.sleep(7)
    mc.postToChat("(evil Gandalf voice) Vous. n'en. sortirez. PAAAS !")
    time.sleep(6.5)
    mc.postToChat("(evil laugh) MUAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAH !")
    time.sleep(15)
    mc.postToChat("(evil deep voice) Et vous savez pourquoi vous etes enferme ici, entoure de dangers ?")
    time.sleep(8)
    mc.postToChat(f"Parce que c'est rigolo ! C'est fun. C'est amusant. les donjons et les aventuriers qui risquent leur vie.")
    time.sleep(7)
    mc.postToChat("Amusez-vous bien MUAHAHAHAHAHA.")
    time.sleep(35)
    mc.postToChat("Vous etes toujours vivant ??")
    time.sleep(7)
    mc.postToChat("D'ailleurs. vous savez ce qu'il y a de bien avec ce monde ?")
    time.sleep(8)
    mc.postToChat("Les aventuriers comme vous reapparaissent apres leur mort.")
    time.sleep(6.5)
    mc.postToChat("Ce qui me permet de les tuer plein de fois et de pleins de facons differentes.")
    time.sleep(35)
    mc.postToChat("Au fait. desole pour les salles vides hein.")
    time.sleep(6.5)
    mc.postToChat("Il y a eu une greve des monstres recemment.")
    time.sleep(6.5)
    mc.postToChat("Ils exigent des garanties lors de blessures ou mort causees par les pieges du donjon ...")
    time.sleep(6.5)
    mc.postToChat("Quand meme. les propres pieges de mon donjon ! Ils pourraient faire attention a ou ils marchent.")
    time.sleep(15)
    mc.postToChat("Tiens. ca me fait penser que vous devez trouver les pieges un peu redondants.")
    time.sleep(6.5)
    mc.postToChat("Je suis d'accord. J'ai eu pleeiinns d'idees tres amusantes. mais...")
    time.sleep(6.5)
    mc.postToChat("Vous etes arrives avant que je finisse.")
    time.sleep(7)
    mc.postToChat("Dommage pour vous.")
    time.sleep(45)
    mc.postToChat("Vous. Vous etes pas bien bavard hein ?")
    time.sleep(7)
    mc.postToChat("J'en ai connu des qui criaient a la moindre occasion.")
    time.sleep(10)
    mc.postToChat("Enfin. vous au moins vous visitez. Ca fait plaisir de voir qu'on respecte mon travail.")
    time.sleep(7)
    mc.postToChat("La plupart des autres se suicident ou meurent betement sans avoir vu la moitie des salles.")
    time.sleep(6.5)
    mc.postToChat("Il y en a meme un qui est mort juste devant la sortie. Quel dommage MUAHAHAAHA.")
    time.sleep(8)
    mc.postToChat("Euh... Je veux dire. non. bien sur que non il n'y a pas de sortie.")
    time.sleep(35)
    mc.postToChat("Oh. je ne sais pas si vous avez ouvert un coffre ?")
    time.sleep(6.5)
    mc.postToChat("Vous etes decu hein ?")
    time.sleep(6.5)
    mc.postToChat("Vos collegues aventuriers ont tout pris.")
    time.sleep(6.5)
    mc.postToChat("Ca coute cher de refournir le donjon a chaque fois.")
    time.sleep(6.5)
    mc.postToChat("Et cette annee on est en budget limite.")
    time.sleep(7)
    mc.postToChat("C'est bien triste.")

def test_room():
    """programme de test des salles"""
    x, y, z = mc.player.getTilePos()
    y -= 1
    room = Room((x, y, z), 20, 8, 20, (x-10, y, z))
    room.generate()
    mc.setBlock(x, y, z, block.BEDROCK)

def main():
    """programme principal. Génère un donjon là où se trouve le joueur."""
    x, y, z = mc.player.getTilePos()
    y -= 1
    mc.postToChat('[INFO] The dungeon is generating. Please wait (it can take some time).')
    dungeon = Dungeon(x, y, z, DUNGEON_SIZE)
    dungeon.generate()
    mc.player.setPos(x, y+1, z)
    if not SKIP_MONOLOGUE:
        evil_monologue()

main()
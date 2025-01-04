'''
Generate a random dungeon
'''

import mcpi.minecraft as minecraft
import mcpi.block as block
import mcpi.entity as entity
import random

mc = minecraft.Minecraft.create()

WALL_BLOCK = block.COBBLESTONE
FLOOR_BLOCK = block.STONE_BRICK
ROOF_BLOCK = block.STONE
WOOD_BLOCK = block.WOOD_PLANKS

ENTITY_BOSS_LIST = (entity.WITHER_SKELETON, entity.ILLUSIONER, entity.ENDERMAN, entity.EVOKER)
ENTITY_MONSTER_LVL1_LIST = (entity.ZOMBIE, entity.SKELETON, entity.SLIME, entity.SPIDER)
ENTITY_MONSTER_LVL2_LIST = (entity.CAVE_SPIDER, entity.STRAY, entity.HUSK, entity.SILVERFISH, entity.MAGMA_CUBE)
ENTITY_MONSTER_LVL3_LIST = (entity.VEX, entity.VINDICATOR, entity.BLAZE)

class Room:
    '''
    Une salle du donjon.
    Les salles mesurent au minimum 10×10×6 blocs.
    
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

        self.theme = random.choice(Room.ROOM_THEMES)
        self.type = 'spawn' if is_spawn else random.choice(Room.ROOM_TYPES)
        self.tags = 'special' if self.type in ('boss', 'spawn') else random.sample(Room.ROOM_TAGS, random.randint(1, 3))
        self.level = random.choice(self.ROOM_LEVELS)
        self.orientation = None # l'orientation n'a d'importance que pour bridge
        if self.type == 'bridge':
            if self.pos_entrance[0] == x:
                self.orientation = 'x'
            elif self.pos_entrance[2] == z:
                self.orientation = 'z'
            print('orientation is', self.orientation, f'(door is at {self.pos_entrance})')

        self.liquid_block = block.ICE if self.theme == 'winter' else block.LAVA if self.theme == 'hell' else block.WATER

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
        if 'monster' in self.tags:
            self.summon_monsters()
        self.generate_enhancements()
        self.generate_doors()

    def clear_area(self):
        """Vide l'espace où la pièce va être créée"""
        x, y, z = self.center
        mc.setBlocks(x-self.width//2, y, z-self.depth//2,
                     x+self.width//2, y+self.height, z+self.depth//2,
                     block.AIR)
        
    def generate_roof(self):
        """Génère le plafond de la pièce"""
        x, y, z = self.center
        mc.setBlocks(x-self.width//2, y+self.height, z-self.depth//2,
                     x+self.width//2, y+self.height+1, z+self.depth//2,
                     ROOF_BLOCK)

    def generate_floor(self):
        """Génère le sol de la pièce"""
        print('started generating floor')
        x, y, z = self.center
        if self.type == "bridge":
            mc.setBlocks(x-self.width//2, y-2, z-self.depth//2,
                         x+self.width//2, y, z+self.depth//2,
                         block.AIR)
            mc.setBlocks(x-self.width//2, y-2, z-self.depth//2,
                         x+self.width//2, y-1, z+self.depth//2,
                         self.liquid_block)
            print('filled ground with liquid')
            bridge_block = block.STONE if self.theme == 'hell' else WOOD_BLOCK
            if self.orientation == 'x':
                mc.setBlocks(*self.pos_doors[0],
                             *self.pos_entrance[:2], self.pos_entrance[2]+1, # tout ça pour changer z de 1
                             bridge_block)
                print('created x bridge')
            else:
                mc.setBlocks(*self.pos_doors[2],
                             *self.pos_entrance[1:], self.pos_entrance[0]+1, # tout ça pour changer x de 1
                             bridge_block)
                print('created z bridge')
        elif self.type == 'normal':
            mc.setBlocks(x-self.width//2, y, z-self.depth//2,
                     x+self.width//2, y, z+self.depth//2,
                        FLOOR_BLOCK)
            for quart in range(4):
                if random.randint(0, 100) < 5:
                    self.generate_lake(quart)
        else:
            mc.setBlocks(x-self.width//2, y, z-self.depth//2,
                     x+self.width//2, y, z+self.depth//2,
                        FLOOR_BLOCK)
            
    def generate_lake(self, quart):
        """Génère un lac sur le quart <quart> du sol"""
        x, y, z = self.center

        if quart == 0:
            mc.setBlocks(x-self.width//2, y-2, z-self.depth//2,
                         x-2, y, z-2,
                         block.AIR)
            mc.setBlocks(x-self.width//2, y-2, z-self.depth//2,
                         x-2, y-1, z-2,
                         self.liquid_block)
        elif quart == 1:
            mc.setBlocks(x-self.width//2, y-2, z+self.depth//2,
                         x-2, y-1, z+2,
                         block.AIR)
            mc.setBlocks(x-self.width//2, y-2, z+self.depth//2,
                         x-2, y, z+2,
                         self.liquid_block)
        elif quart == 2:
            mc.setBlocks(x+self.width//2, y-2, z-self.depth//2,
                         x+2, y, z-2,
                         block.AIR)
            mc.setBlocks(x+self.width//2, y-2, z-self.depth//2,
                         x+2, y-1, z-2,
                         self.liquid_block)
        elif quart == 3:
            mc.setBlocks(x+self.width//2, y-2, z+self.depth//2,
                         x+2, y, z+2,
                         block.AIR)
            mc.setBlocks(x+self.width//2, y-2, z+self.depth//2,
                         x+2, y-1, z+2,
                         self.liquid_block)
        
    def generate_walls(self):
        """Génère les murs de la pièce"""
        x, y, z = self.center
        mc.setBlocks(x-self.width//2, y, z-self.depth//2,
                     x+self.width//2, y+self.height, z-self.depth//2,
                     WALL_BLOCK)
        mc.setBlocks(x-self.width//2, y, z-self.depth//2,
                     x-self.width//2, y+self.height, z+self.depth//2,
                     WALL_BLOCK)
        mc.setBlocks(x+self.width//2, y, z-self.depth//2,
                     x+self.width//2, y+self.height, z+self.depth//2,
                     WALL_BLOCK)
        mc.setBlocks(x-self.width//2, y, z+self.depth//2,
                     x+self.width//2, y+self.height, z+self.depth//2,
                     WALL_BLOCK)
        
    def generate_doors(self):
        """Génère les portes de la pièce"""
        print('Started door generation')
        self.place_door(*self.pos_entrance)
        print('Entrance placed. Started exit generation')
        if self.type == "bridge":
            if self.orientation == 'x':
                print('placing x door for bridge')
                self.place_door(*self.pos_doors[0])
                print('placing done')
            else:
                print('placing z door for bridge')
                self.place_door(*self.pos_doors[2])
                print('placing done')
        elif 'one exit' in self.tags:
            self.place_door(*self.pos_doors[random.randint(0, 2)])
        else:
            for door in self.pos_doors:
                if random.randint(1, 100) < 50:
                    self.place_door(*door)
            
    def place_door(self, x, y, z):
        """
        DOESN'T WORK ENTIERLY BECAUSE MCPI

        Place une double porte dans le mur
        """
        print('door opened')
        if z == self.center[2]:
            mc.setBlocks(x, y+1, z, x, y+2, z+1, block.AIR)
            # pour l'instant la porte se casse après avoir été posée pour une raison inconnue
            # if 'locked' in self.tags:
            #     mc.setBlock(x, y+1, z, block.DOOR_IRON)
            #     mc.setBlock(x, y+1, z+1, block.DOOR_IRON)
            # else:
            #     mc.setBlock(x, y+1, z, block.DOOR_WOOD)
            #     mc.setBlock(x, y+1, z+1, block.DOOR_WOOD)
        else:
            mc.setBlocks(x, y+1, z, x+1, y+2, z, block.AIR)
            # pour l'instant la porte se casse après avoir été posée pour une raison inconnue
            # if 'locked' in self.tags:
            #     mc.setBlock(x, y+1, z, block.DOOR_IRON)
            #     mc.setBlock(x+1, y+1, z, block.DOOR_IRON)
            # else:
            #     mc.setBlock(x, y+1, z, block.DOOR_WOOD)
            #     mc.setBlock(x+1, y+1, z, block.DOOR_WOOD)
        
        # ici il faudra peut-être faire un appel à une suite de génération en donnant la porte créée comme nouvelle porte d'entrée
        # ce serait mieux que cet appel ai lieu hors de cette fonction mais ça va être compliqué. Peut-être un return ?

    def generate_treasures(self):
        """Génère des trésors dans la pièce"""
        print('started placing treasures')
        block_treasure_list = (block.GOLD_BLOCK, block.DIAMOND_BLOCK, block.EMERALD_ORE)
        for place in self.pos_stuff:
            x, y, z = place
            if random.randint(0, 100) < 50:
                self.place_chest_with_stuff(x, y, z)
            elif random.randint(0, 100) < 75:
                mc.setBlock(x, y, z, random.choice(block_treasure_list))

    def place_chest_with_stuff(self, x, y ,z):
        """
        DOESN'T WORK ENTIERLY BECAUSE MCPI
        
        Place un coffre avec des trésors dedans.
        """
        # pas de méthode permettant de remplir le coffre. Pas de hopper ni spawn item pour les remplir en trichant un peu.
        mc.setBlock(x, y, z, block.CHEST)

    def generate_traps(self):
        """Génère des pièges dans la pièce"""
        print('started placing traps')
        trap_list = ('cobweb', 'pit', 'lava fall', 'shulker')
        # abandonné : anvil (no entity falling anvil), tnt floor (no block pressure plate), tnt chest (no trapped chest)
        type_piege = random.sample(trap_list, random.randint(1, 2))
        print('traps are', type_piege)
        if 'cobweb' in type_piege:
            self.place_cobweb_trap()
        if 'pit' in type_piege:
            self.place_pit_trap()
        if 'lava fall' in type_piege:
            self.place_lavafall_trap()
        if 'shulker' in type_piege:
            self.place_shulker_trap()
        print('ended trap generation')

    def place_cobweb_trap(self):
        """
        DOESN'T WORK ENTIERLY BECAUSE MCPI

        Place des toiles d'araignées dans la pièce
        """
        # spawnEntity ne fonctionne pas...
        x, y, z = self.center
        x -= self.width//2+1
        y += 1
        z -= self.depth//2+1
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
        print('placing lavafall traps')
        for door in self.pos_doors:
            x, y, z = door
            if x < self.center[0]:
                mc.setBlocks(x+1, y+self.height, z, x+1, y+self.height, z+1, block.LAVA_FLOWING)
            elif x > self.center[0]:
                mc.setBlocks(x-1, y+self.height, z, x-1, y+self.height, z+1, block.LAVA_FLOWING)
            elif z < self.center[2]:
                mc.setBlocks(x, y+self.height, z+1, x+1, y+self.height, z+1, block.LAVA_FLOWING)
            elif z > self.center[2]:
                mc.setBlocks(x, y+self.height, z-1, x+1, y+self.height, z-1, block.LAVA_FLOWING)
        print('done')

    def place_shulker_trap(self):
        """
        DOESN'T WORK BECAUSE MCPI

        pose des shulkers dans la pièce
        """
        # spawnEntity ne fonctionne pas...
        for place in self.pos_stuff:
            x, y, z = place
            if mc.getBlock(x, y, z) == block.AIR.id:
                # mc.spawnEntity(x, y, z, entity.SHULKER)
                pass
    
    def generate_enhancements(self):
        """place des décorations dans la pièce"""
        print('started enhancements generation')
        decor_functions_list = (self.place_fire, self.place_pillar, self.place_cuve, self.place_fall)

        if self.type == 'boss':
            generate_deco = random.choice(decor_functions_list)
            x = self.center[0] - self.width//2
            y = self.center[1]
            z = self.center[2] - self.depth//2
            for i in range(self.width):
                if i%8 == 0:
                    generate_deco(x+i, y, z+4)
                    generate_deco(x+i, y, z-4)
            for i in range(self.depth):
                if i%8 == 0:
                    generate_deco(x+4, y, z+i)
                    generate_deco(x-4, y, z+i)
        elif self.type == 'spawn':
            generate_deco = random.choice(decor_functions_list)
            for place in self.pos_stuff:
                x, y, z = place
                if (x, y-1, z) != self.center:
                    generate_deco(x, y, z)
        else:
            print('generation for bridge and normal')
            for place in self.pos_stuff:
                x, y, z = place
                print('selected place')
                if self.type == 'normal' and mc.getBlock(x, y, z) == block.AIR.id or self.type == 'bridge': # removing line for bridge because seem to cause crash
                    print('checked for air')
                    if random.randint(0, 100) < 50:
                        print('random is true')
                        if self.type == 'normal':
                            generate_deco = random.choice(decor_functions_list)
                        else:
                            print('choosed fall because bridge')
                            generate_deco = self.place_fall
                        generate_deco(x, y, z)
                else:
                    print('block found. Place is alerady taken')
        print('ended enhancements generation')

    def place_fire(self, x, y, z):
        """créé un pilier avec du feu en haut"""
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
        """place un pilier du sol au plafond"""
        for i in range(self.height):
            mc.setBlock(x, y+i, z, block.NETHER_BRICK)
        mc.setBlock(x+1, y+self.height//2, z, block.TORCH.id, 1)
        mc.setBlock(x-1, y+self.height//2, z, block.TORCH.id, 2)
        mc.setBlock(x, y+self.height//2, z+1, block.TORCH.id, 3)
        mc.setBlock(x, y+self.height//2, z-1, block.TORCH.id, 4)

    def place_cuve(self, x, y, z):
        """place une cuve de liquide"""
        mc.setBlock(x+1, y, z, block.STAIRS_COBBLESTONE.id, 1)
        mc.setBlock(x-1, y, z, block.STAIRS_COBBLESTONE.id, 0)
        mc.setBlock(x, y, z+1, block.STAIRS_COBBLESTONE.id, 3)
        mc.setBlock(x, y, z-1, block.STAIRS_COBBLESTONE.id, 2)
        mc.setBlock(x, y, z, self.liquid_block)

    def place_fall(self, x, y, z):
        """place une chute de liquide"""
        print('placing fall')
        mc.setBlocks(x, y-1, z, x, y+self.height, z, block.AIR)
        mc.setBlock(x, y+self.height, z, self.liquid_block)
        if self.theme == 'winter':
            mc.setBlocks(x, y-1, z, x, y+self.height, z, self.liquid_block)
        print('ended placing fall')

    def summon_monsters(self):
        """
        DOESN'T WORK BECAUSE MCPI

        Fait apparaître des monstres dans la pièce
        """
        print('started monster summoning')
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


class Dungeon:
    '''
    Le donjon génère plusieurs salles liées entre-elles
    '''
    def __init__(self, x, y, z, width, height, depth):
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.height = height
        self.depth = depth
        
    def generate(self):
        """Créé le donjon"""
        pass
        
    def choose_random_room(self):
        """Choisit une salle aléatoire"""
        pass

    def generate_spawn_room(self):
        """
        Salle d'apparition. Le joueur se trouve au milieu au début.
        - 4 portes possibles
        - minimum 1 porte existante
        """
        mc.setBlocks(self.x - self.width//2, self.y, self.z - self.depth//2,
                     self.x + self.width//2 -1, self.y+7, self.z + self.depth // 2 -1, 
                     WALL_BLOCK)
        mc.setBlocks(self.x - self.width//2 +1, self.y, self.z - self.depth//2 +1,
                     self.x + self.width//2, self.y+7, self.z + self.depth // 2, 
                     block.AIR)
        
def test():
    """programme de test"""
    x, y, z = mc.player.getTilePos()
    y -= 1
    room = Room((x, y, z), 20, 8, 20, (x-10, y, z))
    print('type', room.type.upper(), room.tags)
    room.generate()

test()
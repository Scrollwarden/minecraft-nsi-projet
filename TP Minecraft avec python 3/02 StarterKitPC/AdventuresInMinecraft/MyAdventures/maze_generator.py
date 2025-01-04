import mcpi.minecraft as minecraft
import mcpi.block as block

mc = minecraft.Minecraft.create()

h, w = 41, 41

def print_map(map):
    for i in range(len(map)):
        for j in range(len(map[i])):
            print(map[i][j], end='')
        print()


digger_pos = (h//2, w//2)

import random

def put_walls(pos, move, map_walls, map_path):
    if move == "u" or move == "d":
        if map_path[pos[0]][pos[1]-1] == 1:
            map_walls[pos[0]][pos[1]-1] = 1
        if map_path[pos[0]][pos[1]+1] == 1:
            map_walls[pos[0]][pos[1]+1] = 1
    else:
        if map_path[pos[0]+1][pos[1]] == 1:
            map_walls[pos[0]+1][pos[1]] = 1
        if map_path[pos[0]-1][pos[1]] == 1:
            map_walls[pos[0]-1][pos[1]] = 1
    map_walls[pos[0]][pos[1]] = 1
    
def get_move(pos, map_walls, map_path, map_digg):
        
    d=["u", "d", "l", "r"]
    while len(d) > 0:
        random.shuffle(d)
        move = d.pop()

        move_count = random.randint(1,4)

        i=0
        while i < move_count:
            new_pos = pos
            if move == "u":
                new_pos = (pos[0]-1, pos[1])
            elif move == "d":
                new_pos = (pos[0]+1, pos[1])
            elif move == "l":
                new_pos = (pos[0], pos[1]-1)
            elif move == "r":
                new_pos = (pos[0], pos[1]+1)

            if not map_walls[new_pos[0]][new_pos[1]]:
                put_walls(pos, move, map_walls, map_path)
                map_path[pos[0]][pos[1]] = 0
                map_digg[pos[0]][pos[1]] = i
            elif i==1:
                # change direction
                break
            else:
                # shorted than move_count but ok
                pass
            i+=1
            
        if i == 0:
            continue

        return new_pos
        
    return None

def generate_main_path():
    map_walls = [[0 for i in range(h)] for j in range(w)]
    map_path  = [[1 for i in range(h)] for j in range(w)]
    map_digg  = [[0 for i in range(h)] for j in range(w)]
    
    pos = digger_pos

    out_of_map = False
    i=1
    while not out_of_map:
        pos = get_move(pos, map_walls, map_path, map_digg)
            
        if pos is None:
            print("Out of moves")
            #map_walls = [[0 for i in range(h)] for j in range(w)]
            map_path  = [[1 for i in range(h)] for j in range(w)]
            print_map(map_path)
            pos = digger_pos
            i+=1

        if pos[0] >= w-1 or pos[0]<=0 or pos[1] >= h-1 or pos[1] <= 0:
            out_of_map = True
            print("Out of map")
    
    return map_digg, map_walls

map_digg, map_walls = generate_main_path()
print_map(map_digg)
print()
print_map(map_walls)


def build_map(map_digg):
    x, y, z = mc.player.getTilePos()
    for i in range(w):
        for j in range(h):
            mc.setBlocks(x+i, y, z+j, x+i, y+7, z+j, block.COBBLESTONE)
            if map_digg[i][j] != 0:
                mc.setBlocks(x+i, y, z+j, x+i, y+7, z+j, block.AIR)

build_map(map_digg)
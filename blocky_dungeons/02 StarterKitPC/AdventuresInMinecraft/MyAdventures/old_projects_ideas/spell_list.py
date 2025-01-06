'''
This programm contain all the spells the player can cast.
Players can cast using the command !cast <spell_name>.
!cast help will display all the spells.
Players can't cast if they don't have a book and certan items.
All items are consumed when casting, except the book.

PROJET ABANDONNÉ SUITE AU DISFONCTIONNEMENT DE PLUSIEURS MÉTHODES DE MCPI.
'''

import mcpi.minecraft as minecraft
import mcpi.block as block
import mcpi.entity as entity
import mcpi.event as event
import time

# Connect to Minecraft
mc = minecraft.Minecraft.create()


def spell_help(page=1):
    """
    Spell : Sent to the wizard's mind all knowledge about spells

    Requirement : book
    """
    mc.postToChat(" ")
    if page == 1:
        mc.postToChat("THE WIZARD'S 5 COMMANDMENTS")
        mc.postToChat("    -")
        mc.postToChat("1. Always have a book on you. NEVER. FORGET. YOUR. BOOK.")
        mc.postToChat("2. Don't waste spell resources.")
        mc.postToChat("3. Always check if you have what you need before casting.")
        mc.postToChat("4. Never forget the 'help' spell. And precise the page.")
        mc.postToChat("5. Never cast a spell at 15:14 the 13 day of the month.")
    elif page == 2:
        mc.postToChat("THE 6 SPELLS FOR THOSE WHO KNOW")
        mc.postToChat("    -")
        mc.postToChat("- !cast shield :")
        mc.postToChat("    Generate a glass shield around you.")
        mc.postToChat("    Consume glass block, nether quartz.")
        mc.postToChat("- !cast wall :")
        mc.postToChat("    Rise a stone wall in the direction you're looking.")
        mc.postToChat("    Consume stone block, nether quartz.")
        mc.postToChat("- !cast trap :")
        mc.postToChat("    Create a box of cobweb in front of you.")
        mc.postToChat("    Consume cobweb, slimeball.")
        mc.postToChat("- !cast rise_death :")
        mc.postToChat("    Summon the undeads. You can't controle them.")
        mc.postToChat("    Consume bone, jack o'lantern.")
        mc.postToChat("- !cast platform :")
        mc.postToChat("    Create a platform of stone where you are looking.")
        mc.postToChat("    Consume stone block, feather.")
        mc.postToChat("- !cast fire_circle :")
        mc.postToChat("    Set a fire circle around you.")
        mc.postToChat("    Consume blaze power, coal.")
    elif page == 3:
        mc.postToChat("THE 7 SPELLS FOR THE GREAT TRUE WIZARDS")
    elif page == 4:
        mc.postToChat("THE 2 FORBIDEN SPELLS BORN IN DEEP NETHER")
    mc.postToChat(f"<{page}>------------------------<4>")

def spell_shield():
    """
    Spell : Generate a shield around the wizard. Easily breakable but still able to protect from projectiles.
    
    Requierments : book, glass block, nether quartz
    """
    x, y, z = mc.player.getTilePos()

    mc.setBlocks(x-2, y, z-2, x+2, y+2, z+2, block.GLASS)
    mc.setBlocks(x-1, y, z-1, x+1, y+1, z+1, block.AIR)

def spell_wall():
    """
    Spell : Rise a wall of 15 stones per 2 in the direction the wizard is looking.
    
    Requierments : book, stone block, nether quartz
    """
    x, y, z = mc.player.getTilePos()
    rotation = mc.player.getRotation()
    if 0 < rotation < 90:
        mc.setBlocks(x, y, z-1, x, y+2, z-15, block.STONE)
    elif 90 < rotation < 180:
        mc.setBlocks(x+1, y, z, x+15, y+2, z, block.STONE)
    elif 180 < rotation < 270:
        mc.setBlocks(x, y, z+1, x, y+2, z+15, block.STONE)
    elif 270 < rotation < 360:
        mc.setBlocks(x-1, y, z, x-15, y+2, z, block.STONE)

def spell_fireball():
    """
    Spell : Shoot a fireball in the direction the wizard is looking.
    
    Requierments : book, fireball, feather, golden sword
    """
    x, y, z = mc.player.getTilePos()
    mc.spawnEntity(x, y, z, entity.FIREBALL)

def spell_raise_death():
    """
    Spell : Summon skeletons 20 blocks in the direction the wizard is facing.

    Requierments : book, bone, jack o lantern
    """
    pass

def spell_heal():
    """
    Spell : Heal the wizard for 10pv.
    
    Requierments : book, redstone, bone, golden carrot
    """
    pass

def spell_teleport():
    """
    Spell : Teleport the wizard on the first obstacle in the direction he is looking.

    Requierments : book, ender pearl, feather, ender eye
    """
    pass

def spell_trap():
    """
    Spell : Fill the area in front of the wizard with cobwebs

    Requierments : book, cobweb, slime ball
    """
    pass

def spell_plateform():
    """
    Spell : Create a stone plateform 20 blocks in front of the wizard or on the first obstacle in sight.

    Requierments : book, stone block, ender eye
    """
    pass

def spell_fire_circle():
    """
    Spell : Create a circle of fire 10 blocks around the wizard.

    Requierments : book, blaze powder, coal
    """
    pass

def spell_lightning():
    """
    Spell : Strike lightning on the first obstacle in sight.
    
    Requierments : book, nether star, golden sword, diamond
    """
    pass

def spell_decay():
    """
    Spell : Inflict 5 damages and poison to all entities in 10 blocks radius.
    
    Requierments : book, rotten flesh, spider eye, zombi head
    """
    pass

def spell_invisibility():
    """
    Spell : Make the wizard invisible for 2 minutes.

    Requierments : book, glass block, ender eye, diamond
    """
    pass

def spell_fear():
    """
    Spell : All entities in a radius of 10 meters around the players try to escape him. 5 seconds duration.

    Requierments : book, netherwart, skull, iron ingot
    """
    pass

def spell_fly():
    """
    Spell : Make the wizard fly for 2 minutes.

    Requierments : book, feather, nether star, paper, ghast tear
    """
    pass


# main loop
"""
Check the chat and call the asked spell if the last message is '!cast <spell>'
"""

all_spells = {
    'shield': spell_shield,
    'wall': spell_wall,
    'trap': spell_trap,
    'heal': spell_heal,
    'fireball': spell_fireball,
    'fear': spell_fear,
    'decay': spell_decay,
    'invisibility': spell_invisibility,
    'fly': spell_fly,
    'lightning': spell_lightning,
    'teleport': spell_teleport,
    'raise_death': spell_raise_death,
    'help': spell_help,
    'fire_circle': spell_fire_circle,
    'platform': spell_plateform
}

while True:
    #events = mc.events.pollChatPosts()
    last_message = open("../Bukkit/server.log", mode='r', encoding='latin 1').readlines()[-1]
    splited_prompt = last_message.split(" ") # message is [date] [type] [user] [content ([!cast] [spell_name])]
    if len(splited_prompt) >= 4:
        mc.postToChat("Eligible as spell cast :")
        mc.postToChat(splited_prompt)
        wizard = splited_prompt[2]
        command = splited_prompt[3]
        if command == "!cast":
            spell = splited_prompt[4]
            mc.postToChat(f"spell is {spell}")
            if spell in all_spells.keys():
                if True: # will check if the player has the requierments for the spell
                    all_spells[spell]()
                    mc.postToChat(" ") # avoid the program to trigger the same spell multiple times
                    mc.postToChat("Spell casted")
                else:
                    mc.postToChat("You don't have the items needed for this spell.")
            else:
                mc.postToChat("This spell does not exist.")
    time.sleep(1)


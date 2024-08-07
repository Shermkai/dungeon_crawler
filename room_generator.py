import zmq
import random

# Lists that room generation pulls from to insert into templates
adjectives = ['dark', 'smelly', 'mossy', 'overgrown', 'cold', 'humid', 'decrepit', 'crumbling', 'volcanic',
              'frozen', 'cluttered', 'hot', 'pleasant', 'horrifying', 'dirty', 'pristine', 'carpeted', 'quaint',
              'extravagant', 'dry', 'silent', 'echoey', 'mushy', 'dripping', 'beautiful', 'haunting', 'grassy',
              'mystical', 'arcane']
materials = ['stone', 'wood', 'ceramic', 'steel', 'slime', 'magma', 'dirt', 'meteorite', 'glass', 'clay',
             'organic matter', 'ice', 'cheese', 'crystal']
feelings = ['dread', 'fear', 'joy', 'sadness', 'anger', 'laughter', 'melancholy', 'rage', 'hope', 'anxiety',
            'nostalgia', 'jumpiness', 'nothingness', 'disgust', 'intrigue', 'pride', 'inspiration',
            'disappointment', 'misery', 'annoyance', 'jealousy']
room_types = ['jail', 'chapel', 'bedroom', 'forge', 'bathhouse', 'stable', 'garden', 'schoolroom',
              'storage chamber', 'fridge', 'painter\'s studio', 'workshop', 'child\'s area', 'crypt',
              'corridor', 'kitchen', 'dining room', 'ballroom', 'morgue', 'laboratory', 'recreational area',
              'museum']
clutter = ['cobwebs', 'ingots', 'bones', 'trash piles', 'art supplies', 'strange animal hairs']
items = ['idol', 'diamond', 'torch']
monsters = ['slime', 'skeleton']
door_position = ['north', 'east', 'south', 'west']


def generate_room(is_first_half):
    """Generates a description for the current room by pulling keywords from lists"""

    item = ""
    monster_block = ""
    monster = 'NONE'
    first_template_val = random.random()
    second_template_val = random.random()

    if is_first_half:
        if first_template_val < 0.33:
            description = ("You enter a(n) " + random.choice(adjectives) + " room, its aging walls made of " +
                           random.choice(materials) + ". Immediately upon entry, you are overcome with an intense " +
                           "feeling of " + random.choice(feelings) + ", for the room appears to be a(n) " +
                           random.choice(room_types) + ".")
        elif 0.33 <= first_template_val < 0.66:
            description = ("A site of pure " + random.choice(feelings) + " lies before you. Countless " +
                           random.choice(clutter) + " choke the space, almost obscuring the " +
                           random.choice(materials) + " flooring. The " + random.choice(adjectives) +
                           " nature of the room overwhelms you, revealing that it is undoubtedly a " +
                           random.choice(room_types) + ".")
        else:
            description = ("This " + random.choice(room_types) + " harbors nothing but pure " +
                           random.choice(feelings) + ". While seemingly normal on the surface, " +
                           random.choice(materials) + " coats the walls, floors, and ceiling, only heightening " +
                           "whatever you feel in the moment. " + "To make present matters even more abnormal, " +
                           "a swarm of " + random.choice(clutter) + " floods the tabletops and ground.")
    else:
        # Generate a random monster 25% of the time
        if random.random() > 0.75:
            monster = random.choice(monsters)
            monster_block = " and a " + monster

        item = random.choice(items)

        if second_template_val < 0.33:
            description = ("Inside, you are greeted by a(n) " + item + monster_block +
                           ". There is a door to the " + random.choice(door_position) + " made of " +
                           random.choice(materials) + ". What do you do...?")
        elif 0.33 <= second_template_val < 0.66:
            description = ("Deeper within, your eye catches a glimpse of a(n) " + item + monster_block +
                           ". You also spot the glint of a doorknob to the " + random.choice(door_position) +
                           " attached to a slab of " + random.choice(materials) + ". What do you do...?")
        else:
            description = ("Amongst a sea of futility, you do manage to find a(n) " + item + monster_block +
                           ". Your only way out of this place other than backtracking is through the " +
                           random.choice(materials) + " door that barricades the room from the " +
                           random.choice(door_position) + ". What do you do...?")

    return description, item, monster


print("[RG] Initialized room_generator.py")

# Set up ZeroMQ
context = zmq.Context()           # Set up environment to create sockets
socket = context.socket(zmq.REP)  # Create reply socket
socket.bind("tcp://*:5555")       # This is where the socket will listen on the network port

item_reply = "NONE"  # Stores the item that the room picks so that it may be sent back separately

# Await and deal with requests from client
while True:
    message = socket.recv()  # Message from client
    print(f"[RG] Received from client: {message.decode()}")

    if len(message) > 0:
        if message.decode() == 'Q':
            break

        if message.decode() == 'RM1':     # Room message part 1
            description_reply, item_reply, monster_reply = generate_room(True)
            print("[RG] Sent to client:", description_reply)
            socket.send_string(description_reply)
        elif message.decode() == 'RM2':   # Room message part 2
            description_reply, item_reply, monster_reply = generate_room(False)
            print("[RG] Sent to client:", description_reply)
            socket.send_string(description_reply)
        elif message.decode() == 'ITEM':  # Room item
            print("[RG] Sent to client:", item_reply)
            socket.send_string(item_reply)
        elif message.decode() == 'MONSTER':
            print("[RG] Sent to client:", monster_reply)
            socket.send_string(monster_reply)

print("[RG] Closed room_generator.py")
context.destroy()

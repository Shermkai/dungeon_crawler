import zmq
import random


def generate_room(is_first_half):
    """Generates a description for the current room by pulling keywords from lists."""

    adjectives = ['dark', 'smelly', 'mossy', 'overgrown', 'cold', 'humid', 'decrepit', 'crumbling', 'volcanic',
                  'frozen', 'cluttered', 'hot', 'pleasant', 'horrifying', 'dirty', 'pristine']
    materials = ['stone', 'wood', 'ceramic', 'steel', 'slime', 'magma', 'dirt']
    feelings = ['dread', 'fear', 'joy', 'sadness', 'anger', 'laughter', 'melancholy', 'rage', 'hope', 'anxiety',
                'nostalgia', 'jumpiness', 'nothingness', 'disgust', 'intrigue']
    room_types = ['jail', 'chapel', 'bedroom', 'forge', 'bathhouse', 'animal chamber', 'garden', 'schoolroom',
                  'storage chamber', 'fridge', 'artisan chamber', 'workshop', 'child\'s room', 'burial site',
                  'corridor', 'kitchen', 'dining room', 'ballroom']
    items = ['key', 'sword', 'torch', 'bone']
    monsters = ['slime']
    door_position = ['north', 'east', 'south', 'west']

    # Generate a random monster 10% of the time
    monster_fragment = ""
    if random.random() > 0.9:
        monster_fragment = " and a " + random.choice(monsters)

    description = ""
    if is_first_half:
        description = ("You enter a " + random.choice(adjectives) + " room, its walls made of " +
                       random.choice(materials) + ". Immediately upon entry, you feel an intense feeling of " +
                       random.choice(feelings) + ", for the room appears to be a " + random.choice(room_types) +
                       ".")
    else:
        description = ("Inside, you are greeted by a " + random.choice(items) + monster_fragment +
                       ". There is a door to the " + random.choice(door_position) + " made of " +
                       random.choice(materials) + ". What do you do...?")

    return description


print("[RG] Initialized room_generator.py")

# Set up ZeroMQ
context = zmq.Context()           # Set up environment to create sockets
socket = context.socket(zmq.REP)  # Create reply socket
socket.bind("tcp://*:5555")       # This is where the socket will listen on the network port

# Await and deal with requests from client
while True:
    message = socket.recv()  # Message from client
    print(f"[RG] Received from client: {message.decode()}")

    if len(message) > 0:
        if message.decode() == 'Q':
            break

        print("[RG] Returning data to client...")
        if message.decode() == '0':
            socket.send_string(generate_room(True))
        else:
            socket.send_string(generate_room(False))

print("[RG] Closed room_generator.py")
context.destroy()

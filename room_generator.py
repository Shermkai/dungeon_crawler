import zmq
import random


def generate_room():
    """Generates a description for the current room."""

    adjectives = ['dark', 'smelly', 'mossy', 'overgrown']
    items = ['key', 'sword', 'torch', 'bone']
    monsters = ['slime']

    description = ("You enter a " + random.choice(adjectives) + " and " + random.choice(adjectives) +
                   " room. Inside, there appears to be a " + random.choice(items) + " and a " +
                   random.choice(monsters) + ". There is a door in the back. What do you do...?")

    return str(description)


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
        socket.send_string(generate_room())

context.destroy()

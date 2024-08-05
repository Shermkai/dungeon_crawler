import zmq
import random

print("[CM] Initialized combat_microservice.py")

# Set up ZeroMQ
context = zmq.Context()           # Set up environment to create sockets
socket = context.socket(zmq.REP)  # Create reply socket
socket.bind("tcp://*:5558")       # This is where the socket will listen on the network port

hit_threshold = 0.5

# Await and deal with requests from client
while True:
    message = socket.recv().decode()  # Message from client
    print(f"[CM] Received from client: {message}")

    if len(message) > 0:
        if message == 'Q':
            break

        elif message == 'RAISE THRESHOLD':
            hit_threshold += 0.05
            socket.send_string("Raised player hit chance to: " + str(hit_threshold) + "%")

        elif message == 'ATTACK':
            rand_val = random.random()
            if rand_val < hit_threshold:
                print("[CM] Sent to client: HIT")
                socket.send_string('HIT')
            else:
                print("[CM] Sent to client: MISS")
                socket.send_string('MISS')
        else:
            print("[CM] Sent to client: NONE")
            socket.send_string('NONE')

print("[CM] Closed combat_microservice.py")
context.destroy()

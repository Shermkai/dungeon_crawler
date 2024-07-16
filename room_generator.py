import zmq

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
        socket.send_string("Hello World!")

context.destroy()

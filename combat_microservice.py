import zmq

print("[CM] Initialized combat_microservice.py")

# Set up ZeroMQ
context = zmq.Context()           # Set up environment to create sockets
socket = context.socket(zmq.REP)  # Create reply socket
socket.bind("tcp://*:5558")       # This is where the socket will listen on the network port

# Await and deal with requests from client
while True:
    message = socket.recv().decode()  # Message from client
    print(f"[CM] Received from client: {message}")

    if len(message) > 0:
        if message == 'Q':
            break

        else:
            socket.send_string("Hello World!")

print("[CM] Closed combat_microservice.py")
context.destroy()

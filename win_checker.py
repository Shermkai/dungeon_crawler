import zmq

print("[WC] Initialized win_checker.py")

# Set up ZeroMQ
context = zmq.Context()           # Set up environment to create sockets
socket = context.socket(zmq.REP)  # Create reply socket
socket.bind("tcp://*:5556")       # This is where the socket will listen on the network port

# Await and deal with requests from client
while True:
    message = socket.recv()  # Message from client
    print(f"[WC] Received from client: {message.decode()}")

    if len(message) > 0:
        if message.decode() == 'Q':
            break

        if message.decode() == 'CHECK':
            reply = "Hello World!"
            print("[WC] Sent to client: ", reply)
            socket.send_string(reply)

print("[WC] Closed win_checker.py")
context.destroy()

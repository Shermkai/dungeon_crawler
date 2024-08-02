import zmq

print("[WC] Initialized win_checker.py")

# Set up ZeroMQ
context = zmq.Context()           # Set up environment to create sockets
socket = context.socket(zmq.REP)  # Create reply socket
socket.bind("tcp://*:5556")       # This is where the socket will listen on the network port

# Await and deal with requests from client
while True:
    message = socket.recv().decode()  # Message from client
    print(f"[WC] Received from client: {message}")

    if len(message) > 0:
        if message == 'Q':
            break

        else:
            if len(message.split()) >= 5:
                print("[WC] Sent to client: WIN")
                socket.send_string("WIN")
            else:
                print("[WC] Sent to client: NO WIN")
                socket.send_string("NO WIN")

print("[WC] Closed win_checker.py")
context.destroy()

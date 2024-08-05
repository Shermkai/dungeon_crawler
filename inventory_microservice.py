import zmq

print("[IM] Initialized inventory_microservice.py")

# Setup
key = 0
inventory = {}
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5557")

while True:
    request = socket.recv().decode()  # Get request from localhost
    print(f"[IM] Received from client: {request}")

    if len(request) > 4:
        req_type = request[0:3]  # Separate out first three characters to check if add or get

        if req_type == "add":
            addition = request[4:len(request)]  # Part of the string after the colon

            # If there are no duplicates, add to the list
            if addition in inventory.values():
                socket.send_string(f"Did not add: {addition}")
            else:
                key += 1
                inventory[str(key)] = addition
                socket.send_string(f"Added: {addition} to the inventory")  # Send back confirmation message

        elif req_type == "get":
            asked_for = request[4:len(request)]  # Part of the string after the colon

            if asked_for.isdigit():
                if int(asked_for) <= key:     # If the request item index is a key in the dictionary
                    item = inventory[asked_for]
                    socket.send_string(item)  # Send back item at that index
                elif int(asked_for) > key:      # If the request item index is out of bounds
                    socket.send_string("No item at that index")

            if asked_for == "all":
                return_string = ""  # Empty string to fill with items
                for x in range(1, key+1):
                    item = inventory[str(x)]
                    if len(return_string) == 0:
                        return_string += item
                    else:
                        return_string += ", "
                        return_string += item
                print("[IM] Sent to client: " + return_string)
                socket.send_string(return_string)  # Send back list of items
    else:
        if request == "q" or request == "Q":
            break

print("[IM] Closed inventory_microservice.py")
context.destroy()  # Destroy the localhost and end program

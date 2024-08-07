import pygame
import zmq
import subprocess
import time
import classes
import globals

# Run microservices in background
subprocess.Popen(["python", "room_generator.py"])
subprocess.Popen(["python", "win_checker.py"])
subprocess.Popen(["python", "inventory_microservice.py"])
subprocess.Popen(["python", "combat_microservice.py"])

# Set up ZeroMQ to communicate between files
context = zmq.Context()  # Set up environment to create sockets
room_socket = context.socket(zmq.REQ)  # Create request socket A
win_socket = context.socket(zmq.REQ)  # Create request socket B
inventory_socket = context.socket(zmq.REQ)  # Create request socket C
combat_socket = context.socket(zmq.REQ)  # Create request socket D
room_socket.connect("tcp://localhost:5555")  # Initialize microservice A
win_socket.connect("tcp://localhost:5556")  # Initialize microservice B
inventory_socket.connect("tcp://localhost:5557")  # Initialize microservice C
combat_socket.connect("tcp://localhost:5558")  # Initialize microservice D

# Set up objects
player = classes.Player()
closure_popup = classes.Popup()


def kill_microservices():
    """Sends a request to each of the microservices to end their execution.
    This is needed to avoid any errors from files not properly closing."""

    room_socket.send_string('Q')
    win_socket.send_string('Q')
    inventory_socket.send_string('Q')
    combat_socket.send_string('Q')


def win_screen():
    """Displays the screen that appears when the game is won.
    Returns False when the close button is pressed to indicate that the game loop should stop executing."""

    globals.screen.fill('black')  # Clear the game loop

    exit_button = classes.Button('BOTTOMCENTER', (globals.width / 3.5, globals.height / 7),
                                 (255, 115, 115), int(globals.height * .095), 'black', "Exit Game",
                                 True, (205, 50, 50))

    # Set up and draw text
    font = pygame.font.SysFont('arial', int(globals.height * 0.25))
    text = font.render("You Win!!!", True, 'white')
    globals.screen.blit(text, text.get_rect(center=(globals.width / 2, globals.height / 3)))

    is_screen_showing = True

    while is_screen_showing:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.check_press(event.pos):
                    globals.screen.fill('black')
                    is_screen_showing = False

        if is_screen_showing:
            exit_button.draw(pygame.mouse.get_pos())

        pygame.display.flip()

    return False


def game_over_screen():
    """Displays the screen that appears when the game is lost"""

    globals.screen.fill('black')  # Clear the game loop

    exit_button = classes.Button('BOTTOMCENTER', (globals.width / 3.5, globals.height / 7),
                                 (255, 115, 115), int(globals.height * .095), 'black', "Exit Game",
                                 True, (205, 50, 50))

    # Set up and draw text
    font = pygame.font.SysFont('arial', int(globals.height * 0.25))
    text = font.render("You Lose...", True, 'white')
    globals.screen.blit(text, text.get_rect(center=(globals.width / 2, globals.height / 3)))

    is_screen_showing = True

    while is_screen_showing:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.check_press(event.pos):
                    globals.screen.fill('black')
                    is_screen_showing = False

        if is_screen_showing:
            exit_button.draw(pygame.mouse.get_pos())

        pygame.display.flip()


def combat(monster):
    """Displays combat and handles microservice calls.
    Returns True if the player won the combat and False otherwise"""

    globals.screen.fill('black')  # Clear the game loop
    font = pygame.font.SysFont('arial', int(globals.height * .05))  # Create font

    # Create text display area
    rect_width = globals.width * .95
    rect_height = globals.height * .57
    rect_pos = (globals.width / 2, globals.height / 3)
    rect = pygame.Rect(rect_pos, (rect_width, rect_height))
    rect.center = rect_pos
    pygame.draw.rect(globals.screen, 'white', rect, 5, border_radius=1)

    # Image setup
    if monster == 'slime':
        monster_sprite = pygame.image.load("slime.png").convert()
        monster_sprite = pygame.transform.scale(monster_sprite, (globals.width / 3.5, globals.width / 3.5))
    else:
        monster_sprite = pygame.image.load("skeleton.png").convert()
        monster_sprite = pygame.transform.scale(monster_sprite, (globals.width / 3.5, globals.width / 3.5))

    globals.screen.blit(monster_sprite, monster_sprite.get_rect(center=rect_pos))

    # Monster health setup
    monster_health = 100
    monster_health_text = font.render("Monster Health: " + str(monster_health) + "%", True, 'white')
    globals.screen.blit(monster_health_text, monster_health_text.get_rect(center=(globals.width * 0.8,
                                                                                  globals.height * 0.8)))

    # Player health setup
    player_health_text = font.render("Player Health: " + str(int(player.get_health())) + "%", True, 'white')
    globals.screen.blit(player_health_text, player_health_text.get_rect(center=(globals.width * 0.2,
                                                                                globals.height * 0.8)))

    attack_button = classes.Button('TOPCENTER', (globals.width / 3.5, globals.height / 7),
                                   (125, 255, 115), int(globals.height * .095), 'black', "Attack!!!",
                                   True, (45, 175, 35))
    exit_button = classes.Button('BOTTOMCENTER', (globals.width / 3.5, globals.height / 7),
                                 (255, 115, 115), int(globals.height * .095), 'black', "Run Away!!!",
                                 True, (205, 50, 50))

    if monster == 'slime':
        pygame.mixer.Sound.play(globals.slime_sound)
    else:
        pygame.mixer.Sound.play(globals.rattle_sound)

    is_player_turn = True
    re_display_screen = False
    did_player_live = False
    is_combat_showing = True

    while is_combat_showing:
        if not is_player_turn:  # Take the monster's turn
            time.sleep(1.5)  # Delay for dramatic effect

            combat_socket.send_string('ATTACK')
            if combat_socket.recv().decode() == 'HIT':
                pygame.mixer.Sound.play(globals.oof_sound)
                re_display_screen = True
                if player.damage(12.5):  # If the player dies, indicate such
                    game_over_screen()
                    did_player_live = False
                    is_combat_showing = False

            # If the player lives, reactivate the attack button and pass the turn to them
            is_player_turn = True
            attack_button.set_is_inactive(False)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.check_press(event.pos):
                    globals.screen.fill('black')
                    did_player_live = True
                    is_combat_showing = False
                elif attack_button.check_press(event.pos):  # Take the player's turn
                    combat_socket.send_string('ATTACK')
                    if combat_socket.recv().decode() == 'HIT':
                        pygame.mixer.Sound.play(globals.slash_sound)
                        monster_health -= 33.3
                    is_player_turn = False
                    re_display_screen = True
                    attack_button.set_is_inactive(True)  # Deactivate the attack button during enemy turn

        # Redraw the screen to update values
        if re_display_screen:
            globals.screen.fill('black')
            re_display_screen = False

            if monster_health <= 1:
                did_player_live = True
                is_combat_showing = False

            monster_health_text = font.render("Monster Health: " + str(int(monster_health)) + "%", True, 'white')
            globals.screen.blit(monster_health_text, monster_health_text.get_rect(center=(globals.width * 0.8,
                                                                                          globals.height * 0.8)))
            player_health_text = font.render("Player Health: " + str(int(player.get_health())) + "%", True,
                                             'white')
            globals.screen.blit(player_health_text, player_health_text.get_rect(center=(globals.width * 0.2,
                                                                                        globals.height * 0.8)))
            pygame.draw.rect(globals.screen, 'white', rect, 5, border_radius=1)
            globals.screen.blit(monster_sprite, monster_sprite.get_rect(center=rect_pos))

        if is_combat_showing:
            attack_button.draw(pygame.mouse.get_pos())
            exit_button.draw(pygame.mouse.get_pos())

        pygame.display.flip()

    # If the player won the combat, add the monster's respective item to their inventory
    if did_player_live:
        if monster == 'slime':
            inventory_socket.send_string("add:slimeball")
            print(inventory_socket.recv().decode())
        else:
            inventory_socket.send_string("add:bone")
            print(inventory_socket.recv().decode())

    globals.screen.fill('black')
    return did_player_live


def inventory():
    """Displays and manipulates the player's inventory"""

    globals.screen.fill('black')  # Clear the game loop

    exit_button = classes.Button('BOTTOMCENTER', (globals.width / 3.5, globals.height / 7),
                                 (255, 115, 115), int(globals.height * .095), 'black', "Exit Inventory",
                                 True, (205, 50, 50))

    # Set up variables to be used by all rectangles
    font = pygame.font.SysFont('arial', int(globals.height * .075))
    square_dimension = globals.height * 0.28
    text_coordinates = []

    # Set up top row of rectangles
    square_x_pos = globals.width / 4
    for _ in range(3):
        rect = pygame.Rect((square_x_pos, globals.height / 5), (square_dimension, square_dimension))
        rect.center = (square_x_pos, globals.height / 5)
        pygame.draw.rect(globals.screen, (160, 160, 160), rect)
        square_x_pos += globals.width / 4

        text_coordinates.append(rect.center)

    # Set up bottom row of rectangles
    square_x_pos = globals.width * 0.375
    for _ in range(2):
        rect = pygame.Rect((square_x_pos, globals.height / 2), (square_dimension, square_dimension))
        rect.center = (square_x_pos, globals.height * 0.54)  # 0.54 factor ensures same margins above rectangles
        pygame.draw.rect(globals.screen, (160, 160, 160), rect)
        square_x_pos += globals.width / 4

        text_coordinates.append(rect.center)

    # Draw text for inventory items
    inventory_socket.send_string("get:all")
    inventory_list = inventory_socket.recv().decode()
    inventory_list = inventory_list.replace(',', '')  # Remove commas
    inventory_list = inventory_list.split()  # Turn string into list
    coord_index = 0  # Current index of the list of rectangle coordinates
    for item in inventory_list:
        item = item.capitalize()
        text = font.render(item, True, 'black')
        text_rect = text.get_rect(center=text_coordinates[coord_index])
        globals.screen.blit(text, text_rect)
        coord_index += 1

    is_inventory_showing = True

    while is_inventory_showing:

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.check_press(event.pos):
                    globals.screen.fill('black')
                    is_inventory_showing = False

        if is_inventory_showing:
            exit_button.draw(pygame.mouse.get_pos())

        pygame.display.flip()


def draw_game_loop(data):
    """Redraws game loop elements that may have been cleared"""

    globals.screen.blit(data.get_text_01(), data.get_text_rect_01())   # First half of description
    globals.screen.blit(data.get_text_02(), data.get_text_rect_02())   # Second half of description
    globals.screen.blit(data.get_ctrls_text(), data.get_ctrls_rect())  # Controls
    pygame.draw.rect(globals.screen, 'white', data.get_border_rect(), 5, border_radius=1)


def generate_text(data, new_font, new_rect, new_rect_width, message_part_01="", message_part_02=""):
    """Generates new displayable text for the game loop and returns all its components"""

    # Request and receive text data from room_generator.py microservice if default parameters were not overridden
    if message_part_01 == "":
        room_socket.send_string("RM1")
        message_part_01 = room_socket.recv().decode()
        room_socket.send_string("RM2")
        message_part_02 = room_socket.recv().decode()

    # Prepare the text and text rectangles to display in outer scope
    data.set_text_01(new_font.render(message_part_01, True, 'white', wraplength=int(new_rect_width * .975)))
    data.set_text_02(new_font.render(message_part_02, True, 'yellow', wraplength=int(new_rect_width * .975)))
    data.set_text_rect_01(data.get_text_01().get_rect(topleft=(new_rect.topleft[0] + 20, new_rect.topleft[1] + 20)))
    data.set_text_rect_02(data.get_text_02().get_rect(bottomleft=(new_rect.bottomleft[0] + 20,
                                                                  new_rect.bottomleft[1] - 20)))

    return message_part_01, message_part_02


def game_loop():
    """The core game loop"""

    globals.screen.fill('black')  # Clear the menu

    # Create text display area
    rect_width = globals.width * .95
    rect_height = globals.height * .57
    rect_pos = (globals.width / 2, globals.height / 3)
    rect = pygame.Rect(rect_pos, (rect_width, rect_height))
    rect.center = rect_pos

    # Create text
    font_small = pygame.font.SysFont('arial', int(globals.height * .03))
    font_large = pygame.font.SysFont('arial', int(globals.height * .05))
    ctrls_text = font_small.render("← to go back | → to go forward", True, 'white')
    ctrls_text_rect = ctrls_text.get_rect(center=(globals.width / 2, globals.height * 0.635))

    text_data = classes.Data(None, None, ctrls_text, None, None, ctrls_text_rect, rect)
    msg_01, msg_02 = generate_text(text_data, font_large, rect, rect_width)
    draw_game_loop(text_data)

    # Create buttons
    back_button = classes.Button('BOTTOMLEFT', (globals.width / 3.5, globals.height / 7),
                                 (160, 160, 160), int(globals.height * .1), 'black', "Menu", True)
    next_button = classes.Button('BOTTOMRIGHT', (globals.width / 3.5, globals.height / 7),
                                 (160, 160, 160), int(globals.height * .1), 'black', "New Room", True)
    close_button = classes.Button('BOTTOMCENTER', (globals.width / 3.5, globals.height / 7),
                                  (255, 115, 115), int(globals.height * .1), 'black', "Exit Dungeon",
                                  True, (205, 50, 50))
    item_button = classes.Button('TOPLEFT', (globals.width / 3.5, globals.height / 7),
                                 (160, 160, 160), int(globals.height * .1), 'black', "Grab Item", True)
    combat_button = classes.Button('TOPRIGHT', (globals.width / 3.5, globals.height / 7),
                                   (160, 160, 160), int(globals.height * .1), 'black', "Fight!", True)
    inventory_button = classes.Button('TOPCENTER', (globals.width / 3.5, globals.height / 7),
                                      (160, 160, 160), int(globals.height * .1), 'black', "Inventory", True)

    # Get the item and monster for the current room
    room_socket.send_string('ITEM')
    curr_room_item = room_socket.recv().decode()
    room_socket.send_string('MONSTER')
    curr_room_monster = room_socket.recv().decode()

    # Combat button active/inactive setup
    curr_combat_button_disabled = False  # Whether the combat button in the current room is disabled
    prev_combat_button_disabled = False  # Whether the combat button in the previous room is disabled
    if curr_room_monster == 'NONE':  # If there isn't a monster in the first room, disable the combat button
        curr_combat_button_disabled = True
        combat_button.set_is_inactive(curr_combat_button_disabled)

    return_state = ''  # The state in which the game loop was exited. Either 'BACK' or 'CLOSE'
    prev_room_item = ''  # Used to store a room's item for use in going back
    prev_room_monster = ''  # Used to store a room's monster for use in going back
    prev_msg_01 = ""  # Used to store the first half of the description for use in going back
    prev_msg_02 = ""  # Used to store the second half of the description for use in going back
    was_curr_item_taken = False  # Whether the current room's item was taken
    was_prev_item_taken = False  # Whether the previous room's item was taken
    is_first_room = True  # Whether the current room is the first room
    is_game_running = True

    while is_game_running:
        is_back = False  # Whether the next action is to go back to previous room/menu
        is_next = False  # Whether the next action is to go forward to a new room

        for event in pygame.event.get():

            # Check if mouse is over a button and respond accordingly
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_press(event.pos):
                    is_back = True
                elif next_button.check_press(event.pos):
                    is_next = True
                elif inventory_button.check_press(event.pos):
                    inventory()
                    draw_game_loop(text_data)

                elif item_button.check_press(event.pos):
                    # Add the item to the inventory
                    inventory_socket.send_string(f"add:{curr_room_item}")
                    print(inventory_socket.recv().decode())
                    was_curr_item_taken = True

                    # When the player grabs an item, increase their hit chance slightly in combat
                    combat_socket.send_string("RAISE THRESHOLD")
                    print(combat_socket.recv().decode())

                    # Check if the player has 5 items, meaning the game is won
                    inventory_socket.send_string("get:all")
                    win_socket.send_string(inventory_socket.recv().decode())
                    if win_socket.recv().decode() == "WIN":
                        is_game_running = win_screen()
                        return_state = 'CLOSE'

                elif combat_button.check_press(event.pos):
                    if not combat(curr_room_monster):
                        is_game_running = False
                        return_state = 'CLOSE'
                    curr_combat_button_disabled = True
                    draw_game_loop(text_data)

                    # Check if the player has 5 items, meaning the game is won
                    inventory_socket.send_string("get:all")
                    win_socket.send_string(inventory_socket.recv().decode())
                    if win_socket.recv().decode() == "WIN":
                        is_game_running = win_screen()
                        return_state = 'CLOSE'

                elif close_button.check_press(event.pos):
                    is_game_running = not closure_popup.routine()

                    # Re-display the text and rectangle if the game wasn't closed
                    if is_game_running:
                        draw_game_loop(text_data)
                    else:  # If the game was closed, indicate such
                        return_state = 'CLOSE'

            # Check if either of the arrow keys were pressed and respond accordingly
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    is_back = True
                elif event.key == pygame.K_RIGHT:
                    is_next = True

            # Back button or left arrow goes back one room. A further press returns to the main menu
            if is_back:
                globals.screen.fill('black')  # Clear the screen so the previous page appears properly
                if is_first_room:  # If this is the first room, go back to the main menu
                    is_game_running = False
                    return_state = 'BACK'
                else:  # If this is not the first room, go back to the previous room
                    is_first_room = True
                    back_button.set_text("Menu")

                    # Retrieve the previous room
                    was_curr_item_taken = was_prev_item_taken
                    curr_combat_button_disabled = prev_combat_button_disabled
                    msg_01, msg_02 = generate_text(text_data, font_large, rect, rect_width, prev_msg_01, prev_msg_02)
                    curr_room_item = prev_room_item
                    curr_room_monster = prev_room_monster
                    draw_game_loop(text_data)

            # Next button or right arrow generates a new room. These rooms are not saved like previous rooms,
            # so going back and then forward will generate a new room.
            elif is_next:
                is_first_room = False
                back_button.set_text("Back")
                globals.screen.fill('black')  # Clear the screen so the previous page appears properly

                prev_msg_01 = msg_01  # Store this room's description part 1 in case we return
                prev_msg_02 = msg_02  # Store this room's description part 2 in case we return
                prev_room_item = curr_room_item  # Store this room's item in case we return to this room
                prev_room_monster = curr_room_monster  # Store this room's monster in case we return to this room
                was_prev_item_taken = was_curr_item_taken  # Store whether this room's item was taken by the player
                prev_combat_button_disabled = curr_combat_button_disabled

                # Generate the new room
                was_curr_item_taken = False
                msg_01, msg_02 = generate_text(text_data, font_large, rect, rect_width)
                room_socket.send_string('ITEM')
                curr_room_item = room_socket.recv().decode()
                room_socket.send_string('MONSTER')
                curr_room_monster = room_socket.recv().decode()
                curr_combat_button_disabled = True if curr_room_monster == 'NONE' else False
                draw_game_loop(text_data)

                # Hide grab item button if the item is already in the inventory
                inventory_socket.send_string("get:all")
                if curr_room_item in inventory_socket.recv().decode():
                    was_curr_item_taken = True

            elif event.type == pygame.QUIT:
                is_game_running = False

        # Draw buttons
        # Without this if statement, closing the game will flash the buttons
        if is_game_running:
            back_button.draw(pygame.mouse.get_pos())
            next_button.draw(pygame.mouse.get_pos())
            close_button.draw(pygame.mouse.get_pos())
            inventory_button.draw(pygame.mouse.get_pos())

            item_button.set_is_inactive(was_curr_item_taken)
            item_button.draw(pygame.mouse.get_pos())

            combat_button.set_is_inactive(curr_combat_button_disabled)
            combat_button.draw(pygame.mouse.get_pos())

        pygame.display.flip()

    return return_state


def main_menu():
    """The main menu of the game."""

    # Create title text
    title_font = pygame.font.Font('OldLondon.ttf', int(globals.height * .23))
    title_text = title_font.render("Dungeon Crawler", True, 'white')
    title_rect = title_text.get_rect(center=(globals.width / 2, globals.height / 4))
    globals.screen.blit(title_text, title_rect)  # Text displayed outside loop because it doesn't change

    # Create subtitle text
    subtitle_font = pygame.font.SysFont('arial', int(globals.height * .045))
    subtitle_text_01 = subtitle_font.render("Explore a text-based dungeon and fight enemies!", True, 'white')
    subtitle_rect_01 = subtitle_text_01.get_rect(center=(globals.width / 2, globals.height / 2))
    subtitle_text_02 = subtitle_font.render("Collect all five unique items to win.", True, 'white')
    subtitle_rect_02 = subtitle_text_02.get_rect(center=(globals.width / 2, globals.height * 0.55))
    globals.screen.blit(subtitle_text_01, subtitle_rect_01)  # Text displayed outside loop because it doesn't change
    globals.screen.blit(subtitle_text_02, subtitle_rect_02)  # Text displayed outside loop because it doesn't change

    # Create buttons
    start_button = classes.Button('TOPCENTER', (globals.width / 3.5, globals.height / 7),
                                  (125, 255, 115), int(globals.height * .1), 'black', "Start Game",
                                  True, (45, 175, 35))
    close_button = classes.Button('BOTTOMCENTER', (globals.width / 3.5, globals.height / 7),
                                  (255, 115, 115), int(globals.height * .1), 'black', "Close Game",
                                  True, (205, 50, 50))

    is_menu_running = True

    while is_menu_running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.check_press(event.pos):
                    game_state = game_loop()

                    # Only close the game entirely if indicated by the game loop.
                    # Otherwise, we just keep running the menu.
                    if game_state == 'CLOSE':
                        is_menu_running = False

                elif close_button.check_press(event.pos):
                    is_menu_running = not closure_popup.routine()

                # Re-display title and subtitle if the game wasn't closed
                if is_menu_running:
                    globals.screen.blit(title_text, title_rect)
                    globals.screen.blit(subtitle_text_01, subtitle_rect_01)
                    globals.screen.blit(subtitle_text_02, subtitle_rect_02)

            elif event.type == pygame.QUIT:
                is_menu_running = False

        # Without this if statement, closing the game will flash the buttons
        if is_menu_running:
            start_button.draw(pygame.mouse.get_pos())
            close_button.draw(pygame.mouse.get_pos())

        pygame.display.flip()


main_menu()
kill_microservices()
pygame.quit()
quit()

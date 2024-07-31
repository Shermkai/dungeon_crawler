import pygame
import zmq
import subprocess


class Button:
    def __init__(self, position, size, button_color, text_size, text_color, text, bottom_anchor=False):
        # Set up the button rectangle
        self._button_rect = pygame.Rect(position, size)
        self._button_rect.center = position
        if bottom_anchor:
            self._button_rect.midbottom = position

        # Set up button text
        self._font = pygame.font.SysFont('arial', text_size)
        self._text_color = text_color
        self._text_wrap_length = int(size[0] * 0.975)
        self._text = self._font.render(text, True, self._text_color, wraplength=self._text_wrap_length)
        self._text_rect = self._text.get_rect(center=self._button_rect.center)

        # Set up the button's color
        self._color = button_color

        self._is_active = True

    def set_text(self, new_text):
        """Updates the button's text"""

        self._text = self._font.render(new_text, True, self._text_color,
                                       wraplength=self._text_wrap_length)
        self._text_rect = self._text.get_rect(center=self._button_rect.center)

    def set_is_active(self, new_state):
        """Updates the active/inactive state of the button"""
        self._is_active = not new_state

    def draw(self, position):
        """Draws and displays the button"""

        if self._is_active:
            # Draw the default rectangle initially
            pygame.draw.rect(screen, self._color, self._button_rect)

            # If the cursor is on the button, override the default rectangle with an outlined one
            if self._button_rect.collidepoint(position):
                pygame.draw.rect(screen, 'white', self._button_rect, 10, border_radius=1)

            screen.blit(self._text, self._text_rect)  # Display the text
        else:
            pygame.draw.rect(screen, 'black', self._button_rect)

    def check_press(self, position):
        """Returns True or False depending on whether the button is being hovered over. Used for clicks."""
        if self._button_rect.collidepoint(position):
            pygame.mixer.Sound.play(click_sound)
            return True
        return False


class Popup:
    def __init__(self):
        # Set up popup dimensions
        self._pos = (width / 2, height / 2)
        self._popup_width = width / 1.5
        self._popup_height = height / 1.5

        # Set up popup text
        font = pygame.font.SysFont('arial', int(height * .08))
        self._text = font.render("Are you sure you want to close the game? You will lose all your progress.",
                                 True, 'white', wraplength=int(self._popup_width / 1.1))
        self._text_rect = self._text.get_rect(center=(width / 2, height / 3))

        # Set up popup rectangle
        self._popup_rect = pygame.Rect(self._pos, (self._popup_width, self._popup_height))
        self._popup_rect.center = self._pos

        # Create buttons
        self._deny_button = Button((width / 3, height / 1.5), (width / 3.5, height / 7),
                                   (255, 115, 115), int(height * .1), 'black', "No")
        self._confirm_button = Button((width * .67, height / 1.5), (width / 3.5, height / 7),
                                      (125, 255, 115), int(height * .1), 'black', "Yes")

    def draw(self):
        """Draws and displays the popup"""

        # Draw rectangle and white outline
        pygame.draw.rect(screen, (90, 90, 90), self._popup_rect)
        pygame.draw.rect(screen, 'white', self._popup_rect, 5, border_radius=1)

        # Draw buttons
        self._confirm_button.draw(pygame.mouse.get_pos())
        self._deny_button.draw(pygame.mouse.get_pos())

        screen.blit(self._text, self._text_rect)

    def routine(self):
        """Displays and handles interactions with the popup that appears when attempting to exit the game.
        Returns True or False depending on whether the confirmation was accepted."""

        is_popup_showing = True
        was_game_closed = False  # Whether the popup was confirmed or if the user returned to the game

        while is_popup_showing:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self._confirm_button.check_press(event.pos):
                        was_game_closed = True
                        is_popup_showing = False

                    elif self._deny_button.check_press(event.pos):
                        is_popup_showing = False

            self.draw()
            pygame.display.flip()

        screen.fill('black')  # Clear the screen
        pygame.display.flip()
        return was_game_closed


# Run microservices in background
subprocess.Popen(["python", "room_generator.py"])

# Global constants
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
height = screen.get_height()
width = screen.get_width()
closure_popup = Popup()
click_sound = pygame.mixer.Sound("click.wav")

# Set up ZeroMQ to communicate between files
context = zmq.Context()  # Set up environment to create sockets
socket = context.socket(zmq.REQ)  # Create request socket
socket.connect("tcp://localhost:5555")


def kill_microservices():
    """Sends a request to each of the microservices to end their execution.
    This is needed to avoid any errors from files not properly closing."""

    socket.send_string("Q")


def win_screen():
    """Displays the screen that appears when the game is won.
    Returns False when the close button is pressed to indicate that the game loop should stop executing."""

    screen.fill('black')  # Clear the game loop

    exit_button = Button((width / 2, height - height / 20), (width / 3.5, height / 7),
                         (255, 115, 115), int(height * .095), 'black', "Exit Game", True)

    # Set up and draw text
    font = pygame.font.SysFont('arial', int(height * 0.25))
    text = font.render("You Win!!!", True, 'white')
    screen.blit(text, text.get_rect(center=(width / 2, height / 2)))

    is_screen_showing = True

    while is_screen_showing:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.check_press(event.pos):
                    screen.fill('black')
                    is_screen_showing = False

        if is_screen_showing:
            exit_button.draw(pygame.mouse.get_pos())

        pygame.display.flip()

    return False


def inventory():
    """Displays and manipulates the player's inventory"""

    screen.fill('black')  # Clear the game loop

    exit_button = Button((width / 2, height - height / 20), (width / 3.5, height / 7),
                         (255, 115, 115), int(height * .095), 'black', "Exit Inventory", True)

    # Set up variables to be used by all rectangles
    font = pygame.font.SysFont('arial', int(height * .075))
    square_dimension = height * 0.28

    # Set up top row of rectangles
    square_x_pos = width / 4
    for _ in range(3):
        rect = pygame.Rect((square_x_pos, height / 5), (square_dimension, square_dimension))
        rect.center = (square_x_pos, height / 5)
        pygame.draw.rect(screen, 'white', rect)
        square_x_pos += width / 4

        # Place text
        text = font.render("TEST", True, 'black')
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    # Set up bottom row of rectangles
    square_x_pos = width * 0.375
    for _ in range(2):
        rect = pygame.Rect((square_x_pos, height / 2), (square_dimension, square_dimension))
        rect.center = (square_x_pos, height * 0.54)  # 0.54 factor ensures same margins above rectangles
        pygame.draw.rect(screen, 'white', rect)
        square_x_pos += width / 4

        # Place text
        text = font.render("TEST", True, 'black')
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    is_inventory_showing = True

    while is_inventory_showing:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.check_press(event.pos):
                    screen.fill('black')
                    is_inventory_showing = False

        if is_inventory_showing:
            exit_button.draw(pygame.mouse.get_pos())

        pygame.display.flip()


def draw_game_loop(new_text_01, new_text_02, new_controls, new_text_rect_01, new_text_rect_02, new_controls_rect,
                   new_rect):
    """Redraws game loop elements that may have been cleared"""

    screen.blit(new_text_01, new_text_rect_01)  # First half of description
    screen.blit(new_text_02, new_text_rect_02)  # Second half of description
    screen.blit(new_controls, new_controls_rect)  # Controls
    pygame.draw.rect(screen, 'white', new_rect, 5, border_radius=1)


def generate_text(new_font, new_rect, new_rect_width, message_part_01="", message_part_02=""):
    """Generates new displayable text for the game loop and returns all its components"""

    # Request and receive text data from room_generator.py microservice if default parameters were not overridden
    if message_part_01 == "":
        socket.send_string("RM1")
        message_part_01 = socket.recv().decode()
        socket.send_string("RM2")
        message_part_02 = socket.recv().decode()

    # Prepare the text and text rectangles to display in outer scope
    new_text_01 = new_font.render(message_part_01, True, 'white', wraplength=int(new_rect_width * .975))
    new_text_02 = new_font.render(message_part_02, True, 'yellow', wraplength=int(new_rect_width * .975))
    new_text_rect_01 = new_text_01.get_rect(topleft=(new_rect.topleft[0] + 20, new_rect.topleft[1] + 20))
    new_text_rect_02 = new_text_02.get_rect(bottomleft=(new_rect.bottomleft[0] + 20, new_rect.bottomleft[1] - 20))

    return new_text_01, new_text_02, new_text_rect_01, new_text_rect_02, message_part_01, message_part_02


def game_loop():
    """The core game loop"""

    screen.fill('black')  # Clear the menu

    # Create text display area
    rect_width = width * .95
    rect_height = height * .57
    rect_pos = (width / 2, height / 3)
    rect = pygame.Rect(rect_pos, (rect_width, rect_height))
    rect.center = rect_pos

    # Create text
    font_small = pygame.font.SysFont('arial', int(height * .03))
    font_large = pygame.font.SysFont('arial', int(height * .05))
    ctrls_text = font_small.render("← to go back | → to go forward", True, 'white')
    ctrls_text_rect = ctrls_text.get_rect(center=(width / 2, height * 0.635))
    text_01, text_02, text_rect_01, text_rect_02, msg_01, msg_02 = generate_text(font_large, rect, rect_width)

    draw_game_loop(text_01, text_02, ctrls_text, text_rect_01, text_rect_02, ctrls_text_rect, rect)

    # Create buttons
    back_button = Button((width / 5, height - height / 20), (width / 3.5, height / 7),
                         (110, 110, 110), int(height * .1), 'black', "Menu", True)
    next_button = Button((width * 0.8, height - height / 20), (width / 3.5, height / 7),
                         (125, 255, 115), int(height * .1), 'black', "New Room", True)
    close_button = Button((width / 2, height - height / 20), (width / 3.5, height / 7),
                          (255, 115, 115), int(height * .1), 'black', "Exit Dungeon", True)
    inventory_button = Button((width / 2, height - height / 5), (width / 3.5, height / 7),
                              (110, 110, 110), int(height * .1), 'black', "Inventory", True)
    item_button = Button((width / 5, height - height / 5), (width / 3.5, height / 7),
                         (110, 110, 110), int(height * .1), 'black', "Grab Item", True)
    combat_button = Button((width * 0.8, height - height / 5), (width / 3.5, height / 7),
                           'orange', int(height * .1), 'black', "Fight!", True)

    # Get the item for the current room
    socket.send_string("ITEM")
    curr_room_item = socket.recv().decode()

    return_state = ''  # The state in which the game loop was exited. Either 'BACK' or 'CLOSE'
    prev_room_item = ""  # Used to store a room's item for use in going back
    prev_msg_part_01 = ""  # Used to store the first half of the description for use in going back
    prev_msg_part_02 = ""  # Used to store the second half of the description for use in going back
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
                    draw_game_loop(text_01, text_02, ctrls_text, text_rect_01, text_rect_02, ctrls_text_rect, rect)
                elif item_button.check_press(event.pos):
                    print("Grabbed", curr_room_item)
                    was_curr_item_taken = True
                elif combat_button.check_press(event.pos):
                    print("Fight!")
                elif close_button.check_press(event.pos):
                    is_game_running = not closure_popup.routine()

                    # Re-display the text and rectangle if the game wasn't closed
                    if is_game_running:
                        draw_game_loop(text_01, text_02, ctrls_text, text_rect_01, text_rect_02, ctrls_text_rect, rect)
                    else:  # If the game was closed, indicate such
                        return_state = 'CLOSE'

            # Check if either of the arrow keys were pressed and respond accordingly
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    is_back = True
                elif event.key == pygame.K_RIGHT:
                    is_next = True
                elif event.key == pygame.K_w:
                    is_game_running = win_screen()
                    return_state = 'CLOSE'

            # Back button or left arrow goes back one room. A further press returns to the main menu
            if is_back:
                screen.fill('black')  # Clear the screen so the previous page appears properly
                if is_first_room:  # If this is the first room, go back to the main menu
                    is_game_running = False
                    return_state = 'BACK'
                else:  # If this is not the first room, go back to the previous room
                    is_first_room = True
                    back_button.set_text("Menu")

                    # Retrieve the previous room
                    was_curr_item_taken = was_prev_item_taken
                    text_01, text_02, text_rect_01, text_rect_02, msg_01, msg_02 = generate_text(font_large, rect,
                                                                                                 rect_width,
                                                                                                 prev_msg_part_01,
                                                                                                 prev_msg_part_02)
                    curr_room_item = prev_room_item
                    draw_game_loop(text_01, text_02, ctrls_text, text_rect_01, text_rect_02, ctrls_text_rect, rect)

            # Next button or right arrow generates a new room. These rooms are not saved like previous rooms,
            # so going back and then forward will generate a new room.
            elif is_next:
                is_first_room = False
                back_button.set_text("Back")
                screen.fill('black')  # Clear the screen so the previous page appears properly
                prev_msg_part_01 = msg_01  # Store this room's description part 1 in case we return
                prev_msg_part_02 = msg_02  # Store this room's description part 2 in case we return
                prev_room_item = curr_room_item  # Store this room's item in case we return to this room
                was_prev_item_taken = was_curr_item_taken  # Store whether this room's item was taken by the player

                # Generate the new room
                was_curr_item_taken = False
                text_01, text_02, text_rect_01, text_rect_02, msg_01, msg_02 = generate_text(font_large, rect,
                                                                                             rect_width)
                socket.send_string("ITEM")
                curr_room_item = socket.recv().decode()
                draw_game_loop(text_01, text_02, ctrls_text, text_rect_01, text_rect_02, ctrls_text_rect, rect)

            elif event.type == pygame.QUIT:
                is_game_running = False

        # Draw buttons
        # Without this if statement, closing the game will flash the buttons
        if is_game_running:
            back_button.draw(pygame.mouse.get_pos())
            next_button.draw(pygame.mouse.get_pos())
            close_button.draw(pygame.mouse.get_pos())
            inventory_button.draw(pygame.mouse.get_pos())
            combat_button.draw(pygame.mouse.get_pos())

            item_button.draw(pygame.mouse.get_pos())
            item_button.set_is_active(was_curr_item_taken)

        pygame.display.flip()

    return return_state


def main_menu():
    """The main menu of the game."""

    # Create title text
    title_font = pygame.font.Font('OldLondon.ttf', int(height * .23))
    title_text = title_font.render("Dungeon Crawler", True, 'white')
    title_rect = title_text.get_rect(center=(width / 2, height / 4))
    screen.blit(title_text, title_rect)  # Text displayed outside loop because it doesn't change

    # Create subtitle text
    subtitle_font = pygame.font.SysFont('arial', int(height * .045))
    subtitle_text = subtitle_font.render("Explore a text-based dungeon and fight enemies!", True, 'white')
    subtitle_rect = subtitle_text.get_rect(center=(width / 2, height / 2))
    screen.blit(subtitle_text, subtitle_rect)  # Text displayed outside loop because it doesn't change

    # Create buttons
    start_button = Button((width / 2, height - height / 3), (width / 3.5, height / 7),
                          (125, 255, 115), int(height * .1), 'black', "Start Game")
    close_button = Button((width / 2, height - height / 6), (width / 3.5, height / 7),
                          (255, 115, 115), int(height * .1), 'black', "Close Game")

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
                    screen.blit(title_text, title_rect)
                    screen.blit(subtitle_text, subtitle_rect)

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

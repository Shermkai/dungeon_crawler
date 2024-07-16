import pygame
import zmq
import subprocess


class Button:
    def __init__(self, position, size, button_color, text_size, text_color, text):
        # Set up button text
        font = pygame.font.SysFont('arial', text_size)
        self._text = font.render(text, True, text_color)
        self._text_rect = self._text.get_rect(center=position)

        # Set up the button rectangle
        self._button_rect = pygame.Rect(position, size)
        self._button_rect.center = position

        # Set up the button's color
        self._color = button_color

    def draw(self, position):
        """Draws and displays the button"""

        # Draw the default rectangle initially
        pygame.draw.rect(screen, self._color, self._button_rect)

        # If the cursor is on the button, override the default rectangle with an outlined one
        if self._button_rect.collidepoint(position):
            pygame.draw.rect(screen, 'white', self._button_rect, 5, border_radius=1)

        screen.blit(self._text, self._text_rect)  # Display the text

    def check_press(self, position):
        """Returns True or False depending on whether the button is being hovered over. Used for clicks."""
        if self._button_rect.collidepoint(position):
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
        """Displays and handles interactions with the popup that appears when attempting to exit the game. Returns True
        or False depending on whether the confirmation was accepted."""

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

        screen.fill((0, 0, 0))  # Clear the screen
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

# Set up ZeroMQ to communicate between files
context = zmq.Context()           # Set up environment to create sockets
socket = context.socket(zmq.REQ)  # Create request socket
socket.connect("tcp://localhost:5555")


def kill_microservices():
    """Sends a request to each of the microservices to end their execution.
    This is needed to avoid any errors from files not properly closing."""

    socket.send_string("Q")


def game_loop():
    """The core game loop"""

    screen.fill('black')

    # Create text display area
    rect_width = width * .95
    rect_height = height * .57
    rect_pos = (width / 2, height / 3)
    rect = pygame.Rect(rect_pos, (rect_width, rect_height))
    rect.center = rect_pos
    pygame.draw.rect(screen, 'white', rect, 5, border_radius=1)

    # Receive text data from room_generator.py microservice
    socket.send_string("Request Data")
    message = socket.recv().decode()

    # Create text
    font = pygame.font.SysFont('arial', int(height * .045))
    text = font.render(message, True, 'white', wraplength=int(rect_width * .985))
    text_rect = text.get_rect(center=rect_pos)
    screen.blit(text, text_rect)  # Text displayed outside loop because it doesn't change

    # Create buttons
    close_button = Button((width / 2, height - height / 6), (width / 3.5, height / 7),
                          (255, 115, 115), int(height * .1), 'black', "Close Game")

    is_game_running = True

    while is_game_running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if close_button.check_press(event.pos):
                    is_game_running = not closure_popup.routine()

                    # Re-display the text and rectangle if the game wasn't closed
                    if is_game_running:
                        screen.blit(text, text_rect)
                        pygame.draw.rect(screen, 'white', rect, 5, border_radius=1)

            elif event.type == pygame.QUIT:
                is_game_running = False

        # Without this if statement, closing the game will flash the buttons
        if is_game_running:
            close_button.draw(pygame.mouse.get_pos())

        pygame.display.flip()


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
                    game_loop()
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

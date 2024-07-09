import pygame


class Button:
    def __init__(self, position, size, button_color, text_size, text_color, text):
        # Set up button text
        font = pygame.font.SysFont('arial', text_size)
        self._text = font.render(text, True, text_color)
        self._text_rect = self._text.get_rect(center=position)

        # Set up the button rectangle
        self._pos = (position[0] - size[0] / 2, position[1] - size[1] / 2)  # Offset pos by half button size to center
        self._button_rect = pygame.Rect(self._pos, size)

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
        self._popup_width = width / 1.5
        self._popup_height = height / 1.5
        self._popup_x_coord = width / 2
        self._popup_y_coord = height / 2

        # Set up popup text
        font = pygame.font.SysFont('arial', 85)
        self._text = font.render("Are you sure you want to close the game? You will lose all your progress.",
                                 True, 'white', wraplength=int(self._popup_width / 1.1))
        self._text_rect = self._text.get_rect(center=(width / 2, height / 3))

        # Set up popup rectangle
        self._pos = (self._popup_x_coord - self._popup_width / 2, self._popup_y_coord - self._popup_height / 2)
        self._popup_rect = pygame.Rect(self._pos, (self._popup_width, self._popup_height))

    def draw(self):
        pygame.draw.rect(screen, (90, 90, 90), self._popup_rect)
        screen.blit(self._text, self._text_rect)

    @staticmethod
    def routine():
        """Displays and handles interactions with the popup that appears when attempting to exit the game. Returns True
        or False depending on whether the confirmation was accepted."""

        is_popup_showing = True
        was_game_closed = False  # Whether the popup was confirmed or if the user returned to the game

        while is_popup_showing:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:

                    # TODO: Remove these in favor of buttons
                    if event.key == pygame.K_DELETE:
                        was_game_closed = True
                        is_popup_showing = False

                    elif event.key == pygame.K_END:
                        is_popup_showing = False

            closure_popup.draw()
            pygame.display.flip()

        screen.fill((0, 0, 0))  # Clear the screen
        pygame.display.flip()
        return was_game_closed


# Global constants
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
height = screen.get_height()
width = screen.get_width()
closure_popup = Popup()


def game_loop():
    """The core game loop"""

    # Display a white screen with red text
    screen.fill((255, 255, 255))
    font = pygame.font.SysFont('arial', 50)
    text = font.render("This text should be long enough to get wrapped into a new line thanks to the wraplength "
                       "argument. Also Hello World!", True, 'red', wraplength=400)
    text_rect = text.get_rect(center=(width / 2, height / 2))
    is_game_running = True

    while is_game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_game_running = False

        screen.blit(text, text_rect)
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

                    # Without this if statement, closing the game will flash the title/subtitle
                    if is_menu_running:
                        screen.blit(title_text, title_rect)        # Re-display title after screen clear
                        screen.blit(subtitle_text, subtitle_rect)  # Re-display subtitle after screen clear

            elif event.type == pygame.QUIT:
                is_menu_running = False

        # Without this if statement, closing the game will flash the buttons
        if is_menu_running:
            start_button.draw(pygame.mouse.get_pos())
            close_button.draw(pygame.mouse.get_pos())

        pygame.display.flip()


main_menu()
pygame.quit()
quit()

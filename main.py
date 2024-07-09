import pygame


class Button:
    def __init__(self, position, size, button_color, text_size, text_color, text):
        # Set up text
        font = pygame.font.SysFont('arial', text_size)
        self._text = font.render(text, True, text_color)
        self._text_rect = self._text.get_rect(center=position)

        # Set up the button rectangle
        self._pos = (position[0] - size[0] / 2, position[1] - size[1] / 2)  # Offset pos by half button size to center
        self._button_rect = pygame.Rect(self._pos, size)

        # Set up the button's colors
        self._color = button_color

    def draw(self, surface, position):
        if self._button_rect.collidepoint(position):  # If the cursor is on the button
            pygame.draw.rect(surface, (255, 255, 255), self._button_rect, 5, border_radius=1)
        else:
            pygame.draw.rect(surface, self._color, self._button_rect)

        screen.blit(self._text, self._text_rect)

    def check_press(self, position):
        if self._button_rect.collidepoint(position):
            return True
        return False


pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
height = screen.get_height()
width = screen.get_width()


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
    title_font = pygame.font.Font('OldLondon.ttf', 250)
    title_text = title_font.render("Dungeon Crawler", True, 'white')
    title_rect = title_text.get_rect(center=(width / 2, height / 4))
    screen.blit(title_text, title_rect)  # Text displayed outside loop because it doesn't change

    # Create buttons
    start_button = Button((width / 2, height - height / 3),
                          (560, 160), (125, 255, 115), 120, 'black', "Start Game")
    close_button = Button((width / 2, height - height / 6),
                          (560, 160), (255, 115, 115), 120, 'black', "Close Game")

    is_menu_running = True

    while is_menu_running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.check_press(event.pos):
                    game_loop()
                    is_menu_running = False
                elif close_button.check_press(event.pos):
                    is_menu_running = False
            elif event.type == pygame.QUIT:
                is_menu_running = False

        # Only draw the menu assets if the game loop is yet to start
        # Without the if statement, closing the game will flash the main menu
        if is_menu_running:
            start_button.draw(screen, pygame.mouse.get_pos())
            close_button.draw(screen, pygame.mouse.get_pos())

        pygame.display.flip()


main_menu()
pygame.quit()
quit()

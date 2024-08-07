import pygame
import globals


class Button:
    """Handles button creation and interaction"""

    def __init__(self, position, size, button_color, text_size, text_color, text, bottom_anchor=False,
                 button_border_color=(255, 255, 255)):
        coordinates = position
        if position == 'TOPLEFT':
            coordinates = (globals.width / 5, globals.height - globals.height / 5)
        elif position == 'BOTTOMLEFT':
            coordinates = (globals.width / 5, globals.height - globals.height / 20)
        elif position == 'TOPCENTER':
            coordinates = (globals.width / 2, globals.height - globals.height / 5)
        elif position == 'BOTTOMCENTER':
            coordinates = (globals.width / 2, globals.height - globals.height / 20)
        elif position == 'TOPRIGHT':
            coordinates = (globals.width * 0.8, globals.height - globals.height / 5)
        elif position == 'BOTTOMRIGHT':
            coordinates = (globals.width * 0.8, globals.height - globals.height / 20)

        # Set up the button rectangle
        self._button_rect = pygame.Rect(coordinates, size)
        self._button_rect.center = coordinates
        if bottom_anchor:
            self._button_rect.midbottom = coordinates

        # Set up button text
        self._font = pygame.font.SysFont('arial', text_size)
        self._text_color = text_color
        self._text_wrap_length = int(size[0] * 0.975)
        self._text = self._font.render(text, True, self._text_color, wraplength=self._text_wrap_length)
        self._text_rect = self._text.get_rect(center=self._button_rect.center)

        # Set up the button's color
        self._color = button_color
        self._border_color = button_border_color

        self._is_inactive = False

    def set_text(self, new_text):
        """Updates the button's text"""

        self._text = self._font.render(new_text, True, self._text_color,
                                       wraplength=self._text_wrap_length)
        self._text_rect = self._text.get_rect(center=self._button_rect.center)

    def set_is_inactive(self, new_state):
        """Updates the active/inactive state of the button"""
        self._is_inactive = new_state

    def draw(self, position):
        """Draws and displays the button"""

        if self._is_inactive:
            pygame.draw.rect(globals.screen, 'black', self._button_rect)
        else:
            # Draw the default rectangle initially
            pygame.draw.rect(globals.screen, self._color, self._button_rect)

            # If the cursor is on the button, override the default rectangle with an outlined one
            if self._button_rect.collidepoint(position):
                pygame.draw.rect(globals.screen, self._border_color, self._button_rect, 10, border_radius=1)

            globals.screen.blit(self._text, self._text_rect)  # Display the text

    def check_press(self, position):
        """Returns True or False depending on whether the button is being hovered over. Used for clicks."""
        if self._button_rect.collidepoint(position) and not self._is_inactive:
            pygame.mixer.Sound.play(globals.click_sound)
            return True
        return False


class Data:
    """Stores game loop data pertaining to the room's display, such as text and the rectangular border"""

    def __init__(self, new_txt_01, new_txt_02, new_ctrls_txt, new_txt_rect_01, new_txt_rect_02, new_ctrls_rect,
                 new_rect):
        self._text_01 = new_txt_01
        self._text_02 = new_txt_02
        self._ctrls_text = new_ctrls_txt
        self._text_rect_01 = new_txt_rect_01
        self._text_rect_02 = new_txt_rect_02
        self._ctrls_rect = new_ctrls_rect
        self._border_rect = new_rect

    def get_text_01(self):
        return self._text_01

    def set_text_01(self, new_txt_01):
        self._text_01 = new_txt_01

    def get_text_02(self):
        return self._text_02

    def set_text_02(self, new_txt_02):
        self._text_02 = new_txt_02

    def get_ctrls_text(self):
        return self._ctrls_text

    def get_text_rect_01(self):
        return self._text_rect_01

    def set_text_rect_01(self, new_text_rect_01):
        self._text_rect_01 = new_text_rect_01

    def get_text_rect_02(self):
        return self._text_rect_02

    def set_text_rect_02(self, new_text_rect_02):
        self._text_rect_02 = new_text_rect_02

    def get_ctrls_rect(self):
        return self._ctrls_rect

    def get_border_rect(self):
        return self._border_rect


class Player:
    """Handles player health and damage"""

    def __init__(self):
        self._health = 100

    def get_health(self):
        """Returns the player's health"""
        return self._health

    def damage(self, damage):
        """Reduces the player's health by the given damage.
        Returns True if this results in death (0 health) and False otherwise"""
        self._health -= damage
        return self._health <= 1


class Popup:
    """Handles the popup that displays when attempting to close the game"""

    def __init__(self):
        # Set up popup dimensions
        self._pos = (globals.width / 2, globals.height / 2)
        self._popup_width = globals.width / 1.5
        self._popup_height = globals.height / 1.5

        # Set up popup text
        font = pygame.font.SysFont('arial', int(globals.height * .08))
        self._text = font.render("Are you sure you want to close the game? You will lose all your progress.",
                                 True, 'white', wraplength=int(self._popup_width / 1.1))
        self._text_rect = self._text.get_rect(center=(globals.width / 2, globals.height / 3))

        # Set up popup rectangle
        self._popup_rect = pygame.Rect(self._pos, (self._popup_width, self._popup_height))
        self._popup_rect.center = self._pos

        # Create buttons
        self._deny_button = Button((globals.width / 3, globals.height / 1.5), (globals.width / 3.5, globals.height / 7),
                                   (255, 115, 115), int(globals.height * .1), 'black', "No",
                                   button_border_color=(205, 50, 50))
        self._confirm_button = Button((globals.width * .67, globals.height / 1.5),
                                      (globals.width / 3.5, globals.height / 7),
                                      (125, 255, 115), int(globals.height * .1), 'black', "Yes",
                                      button_border_color=(45, 175, 35))

    def draw(self):
        """Draws and displays the popup"""

        # Draw rectangle and white outline
        pygame.draw.rect(globals.screen, (90, 90, 90), self._popup_rect)
        pygame.draw.rect(globals.screen, 'white', self._popup_rect, 10, border_radius=1)

        # Draw buttons
        self._confirm_button.draw(pygame.mouse.get_pos())
        self._deny_button.draw(pygame.mouse.get_pos())

        globals.screen.blit(self._text, self._text_rect)

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

        globals.screen.fill('black')  # Clear the screen
        pygame.display.flip()
        return was_game_closed

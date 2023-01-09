
import arcade
import game.constants as c
import json


MESSAGES_JSON = 'game/messages.json'


class InfoBar(arcade.Section):
    """
    arcade section for bottom of screen
    (an informational display below the main game)
    """
    def __init__(self, left: int = 0, bottom: int = 0,
                 width: int = c.INFO_BAR_WIDTH,
                 height: int = c.INFO_BAR_HEIGHT,
                 # name: str = "intro",
                 accept_keyboard_events: bool = False,
                 **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        self.name = "info_bar"
        self.char_index = -1  # used by animated typed messages
        self.player = self.window.player

    def on_draw(self):
        arcade.draw_lrtb_rectangle_filled(0, c.SCREEN_WIDTH,
                                          c.INFO_BAR_HEIGHT, 0,
                                          arcade.color.EERIE_BLACK)
        arcade.draw_lrtb_rectangle_outline(0, c.SCREEN_WIDTH,
                                           c.INFO_BAR_HEIGHT, 0,
                                           arcade.color.ANTIQUE_WHITE,
                                           border_width=5)
        self.print_message(self.view.get_level_name())
        self.display_score()

    def get_message(self, msg_name: str) -> str:
        """Takes name of message and returns message str from json file"""
        messages_file = open(MESSAGES_JSON)
        messages = json.load(messages_file)

        # Intro message is typed out, not displayed at once
        if msg_name == "intro":
            if self.char_index // c.TYPING_SPEED < len(messages[msg_name]):
                self.char_index += 1
            messages_file.close()
            return messages[msg_name][0:self.char_index//c.TYPING_SPEED]

        # Other messsages are returned as entire string at once
        messages_file.close()
        return messages[msg_name]

    def print_message(self, msg_name: str) -> None:

        # Print game introduction message
        if not self.view.intro_complete:
            arcade.draw_text(self.get_message("intro"),
                             start_x=50, start_y=115, font_size=15,
                             font_name="arial", bold=True, multiline=True,
                             width=700, align="center",
                             color=(250, 235, 215, 255))

        # Print regular message
        else:
            arcade.draw_text(self.get_message(msg_name),
                             start_x=50, start_y=115, font_size=15,
                             font_name="arial", bold=True, multiline=True,
                             width=700, align="center",
                             color=(250, 235, 215, 255))

    def display_score(self):
        arcade.draw_text("Honey: " + str(self.player.score),
                         start_x=c.SCREEN_WIDTH-140, start_y=20,
                         color=arcade.color.GOLDEN_YELLOW,
                         font_size=15, width=25, align='left',
                         bold=True)

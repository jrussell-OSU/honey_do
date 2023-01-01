
import arcade
import constants as c


class InfoBar(arcade.Section):
    """
    view for bottom of screen (an informational display below the main game)
    """
    def __init__(self, left: int, bottom: int, width: int, height: int,
                 **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        self.char_index = -1  # track which letter we are in the message
        # to print to player

    def on_draw(self):
        arcade.draw_lrtb_rectangle_filled(0, c.SCREEN_WIDTH,
                                          c.INFO_BAR_HEIGHT, 0,
                                          arcade.color.EERIE_BLACK)
        arcade.draw_lrtb_rectangle_outline(0, c.SCREEN_WIDTH,
                                           c.INFO_BAR_HEIGHT, 0,
                                           arcade.color.ANTIQUE_WHITE,
                                           border_width=5)
        self.print_messages()

    def get_message_char(self, msg_name: str) -> str:
        messages = {
            "intro": "Winter is approaching, and your hive doesn't "
            "have enough honey to survive the winter. "
            "Getting more won't be easy --  but you must leave and "
            "go on a dangerous journey to save your hive. Be careful... "
            "the Wasps are hungry too... "
        }
        if self.char_index // 4 < len(messages[msg_name]):
            self.char_index += 1
        return messages[msg_name][0:self.char_index//4]

    def print_messages(self):

        arcade.draw_text(self.get_message_char("intro"),
                         start_x=50, start_y=115, font_size=15,
                         font_name="arial", bold=True, multiline=True,
                         width=700, align="center", color=(250, 235, 215, 255))

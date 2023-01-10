
from game.sections.info_bar import InfoBar
import arcade
from game.sections.hive import HomeSection, ForeignHiveSection
from game.sections.outside import OutsideLeave, OutsideReturn


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.name = "game_view"
        self.current_level = None
        self.intro_complete = False

    def setup(self):

        self.current_level = HomeSection()
        self.section_manager.add_section(self.current_level)
        self.section_manager.add_section(InfoBar())

    def change_level(self, level: arcade.Section):
        arcade.pause(0.5)
        self.section_manager.clear_sections()
        if level == "home":
            self.current_level = HomeSection()
        elif level == "outside_leave":
            self.current_level = OutsideLeave()
        elif level == "foreign_hive":
            self.current_level = ForeignHiveSection()
        elif level == "outside_return":
            self.current_level = OutsideReturn()
        self.section_manager.add_section(self.current_level)

        # Note: instantiating InfoBar each new level, because if same infobar
        # object each level, major bugs for unknown reasons w/ arcade module
        # TODO: figure out how to instantiate/use only one infobar for entire game
        self.section_manager.add_section(InfoBar())

    def on_draw(self):
        self.clear()

    def get_level_name(self) -> str:
        return self.current_level.name

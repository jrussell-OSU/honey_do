# Author: Jacob Russell
# Date: 12-07-2022
# Descrption: "Honey Do" is a game that I made
# for my hot wife where you are a little bee

# Reference: relies on docs and examples from https://api.arcade.academy/

# TODO list:
# Make exit hole location permanent for each game session


import arcade
import game.constants as c
from game.sprites import Player
from game.views.game_view import GameView


class Window(arcade.Window):
    """
    The main (and only) window in which all the views are displayed
    """
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.views = {}
        self.player = Player(c.PLAYER_SPRITE_IMAGE, c.PLAYER_SPRITE_SCALING)

        # TODO: implement arcade "resources" in rest of project
        arcade.resources.add_resource_handle("sprites", "assets/sprites")
        arcade.resources.add_resource_handle("backgrounds", "assets/backgrounds")
        arcade.resources.add_resource_handle("sounds", "assets/sounds")

    def change_view(self, view: arcade.View):
        self.views[view.name] = view
        self.show_view(view)


def main():
    window = Window(c.SCREEN_WIDTH, c.SCREEN_HEIGHT, c.GAME_TITLE)
    view = GameView()
    view.setup()
    window.change_view(view)
    window.run()


if __name__ == "__main__":
    main()

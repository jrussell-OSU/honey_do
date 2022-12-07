# Citation: code structure based on example from:
# https://opensource.com/article/18/4/easy-2d-game-creation-python-and-arcade


import arcade
import random


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BEE_COUNT = 50
BEE_SPRITE_SCALING = 1
PLAYER_SPRITE_SCALING = .7
PLAYER_START_POS_X = 300
PLAYER_START_POS_Y = 400

class Game(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """Sets up the game for the current level"""

        # Create sprite lists
        self.player_list = arcade.SpriteList()
        self.bee_list = arcade.SpriteList()

        # Create and position player
        self.player_sprite = arcade.Sprite("../assets/sprites/bee_player.png",
                                           PLAYER_SPRITE_SCALING)
        self.player_sprite.center_x = PLAYER_START_POS_X
        self.player_sprite.center_y = PLAYER_START_POS_Y
        self.player_list.append(self.player_sprite)

        # Create and position bees
        for i in range(BEE_COUNT):
            # Create bee
            bee = arcade.Sprite("../assets/sprites/bee1.png",
                                BEE_SPRITE_SCALING)

            # Position bee
            bee.center_x = random.randrange(SCREEN_WIDTH)
            bee.center_y = random.randrange(SCREEN_HEIGHT)

            # Add bee to sprite list
            self.bee_list.append(bee)


    def on_key_press(self, key: int, modifiers: int):
        """Processes key presses

        Arguments:
            key {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were down at the time
        """

    def on_key_release(self, key: int, modifiers: int):
        """Processes key releases

        Arguments:
            key {int} -- Which key was released
            modifiers {int} -- Which modifiers were down at the time
        """

    def on_draw(self):
        arcade.start_render()
        self.player_list.draw()
        self.bee_list.draw()

    def on_update(self, delta_time: float):
        """Updates the position of all game objects

        Arguments:
            delta_time {float} -- How much time since the last call
        """

        #
        pass


def main():
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()

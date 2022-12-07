# Author: Jacob Russell
# Date: 12-07-2022
# Descrption: "Honey Do" is a game that I made
# for my hot wife where you are a little bee


import arcade
import random
# import math


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_TITLE = "Honey Do"
BEE_COUNT = 100
BEE_SPRITE_SCALING = 1
PLAYER_SPRITE_SCALING = .7
PLAYER_START_POS_X = 300
PLAYER_START_POS_Y = 400
PLAYER_SPRIT_PATH = "../assets/sprites/bee_player.png"
BEE_SPRIT_PATH = "../assets/sprites/bee1.png"
PLAYER_MOVE_SPEED = 3
PLAYER_ANGLE_SPEED = 3


class Game(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.scene = None
        self.player_sprite = None
        self.physics_engine = None

        arcade.set_background_color(arcade.color.FOREST_GREEN)

    def setup(self):
        """Sets up the game for the current level"""

        # Create sprite lists
        self.player_list = arcade.SpriteList()
        self.bee_list = arcade.SpriteList()

        # Create and position player
        self.player_sprite = Player(PLAYER_SPRIT_PATH, PLAYER_SPRITE_SCALING)
        self.player_sprite.center_x = PLAYER_START_POS_X
        self.player_sprite.center_y = PLAYER_START_POS_Y
        self.player_list.append(self.player_sprite)

        # Create and position bees
        for i in range(BEE_COUNT):

            # Create bee
            bee = Bee(BEE_SPRIT_PATH, BEE_SPRITE_SCALING)

            # Position bee
            bee.center_x = random.randint(15, (SCREEN_WIDTH - 15))
            bee.center_y = random.randint(15, (SCREEN_HEIGHT - 15))

            # Give each bee random angle/direction
            bee.angle = random.randrange(0, 360)

            # Add bee to sprite list
            self.bee_list.append(bee)

        # Set physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.bee_list
        )

    def on_draw(self):
        arcade.start_render()
        self.player_list.draw()
        self.bee_list.draw()

    def on_key_press(self, key: int, modifiers: int):
        """What happens when a key is pressed"""
        if key in [arcade.key.W, arcade.key.UP]:
            self.player_sprite.change_y = PLAYER_MOVE_SPEED
            self.player_sprite.angle = 0
        elif key in [arcade.key.S, arcade.key.DOWN]:
            self.player_sprite.change_y = -PLAYER_MOVE_SPEED
            self.player_sprite.angle = 180
        elif key in [arcade.key.D, arcade.key.RIGHT]:
            self.player_sprite.change_x = PLAYER_MOVE_SPEED
            self.player_sprite.angle = 270
        elif key in [arcade.key.A, arcade.key.LEFT]:
            self.player_sprite.change_x = -PLAYER_MOVE_SPEED
            self.player_sprite.angle = 90

    def on_key_release(self, key: int, modifiers: int):
        """What happens when key is released"""
        if key in [arcade.key.W, arcade.key.UP]:
            self.player_sprite.change_y = 0
        elif key in [arcade.key.S, arcade.key.DOWN]:
            self.player_sprite.change_y = 0
        elif key in [arcade.key.D, arcade.key.RIGHT]:
            self.player_sprite.change_x = 0
        elif key in [arcade.key.A, arcade.key.LEFT]:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time: float):
        """Updates position of game objects, based on delta_time"""

        # randomly periodically rotate bees
        for bee in self.bee_list:
            if random.randint(0, 30) == 30:
                bee.angle = random.randrange(0, 360)

        self.bee_list.update()
        self.player_list.update()
        self.physics_engine.update()


class Player(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)

    def update(self):
        pass
        # Rotate player
        # self.angle += self.change_angle


class Bee(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)

    def update(self):
        pass


def main():
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()

# Author: Jacob Russell
# Date: 12-07-2022
# Descrption: "Honey Do" is a game that I made
# for my hot wife where you are a little bee


import arcade
import random
# import math


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_TITLE = "Honey Thief"
BEE_SPRITE_COUNT = 100
BEE_SPRITE_SCALING = 1.5
HONEY_SPRITE_SCALING = 1.5
HONEY_SPRITE_COUNT = 30
player_SCALING = 1.2
PLAYER_START_POS_X = 300
PLAYER_START_POS_Y = 400
player_PATH = "../assets/sprites/bee_player.png"
BEE_SPRITE_PATH = "../assets/sprites/bee.png"
HONEY_SPRITE_PATH = "../assets/sprites/honey_drop.png"
PLAYER_MOVE_SPEED = 3
PLAYER_ANGLE_SPEED = 3
BACKGROUND_COLOR = arcade.color.DARK_GOLDENROD


class Game(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.scene = None
        self.player = None
        self.physics_engine = None

    def setup(self):
        """Sets up the game for the current level"""

        arcade.set_background_color(BACKGROUND_COLOR)

        # Create sprite lists
        self.player_list = arcade.SpriteList()
        self.bee_list = arcade.SpriteList()
        self.honey_list = arcade.SpriteList()

        # Create and position player
        self.player = Player(player_PATH, player_SCALING)
        self.player.center_x = PLAYER_START_POS_X
        self.player.center_y = PLAYER_START_POS_Y
        self.player_list.append(self.player)

        # Create and position bees
        for i in range(BEE_SPRITE_COUNT):

            # Create bee
            bee = Bee(BEE_SPRITE_PATH, BEE_SPRITE_SCALING)

            # Position bee
            bee.center_x = random.randint(15, (SCREEN_WIDTH - 15))
            bee.center_y = random.randint(15, (SCREEN_HEIGHT - 15))

            # Give each bee random angle/direction
            bee.angle = random.randrange(0, 360)

            # Add bee to sprite list
            self.bee_list.append(bee)

        # Create and position honey drops
        for i in range(HONEY_SPRITE_COUNT):

            # Create honey drop
            honey_drop = Honey_Drop(HONEY_SPRITE_PATH, HONEY_SPRITE_SCALING)

            # Position honey drop
            honey_drop.center_x = random.randint(15, (SCREEN_WIDTH - 15))
            honey_drop.center_y = random.randint(15, (SCREEN_HEIGHT - 15))

            # Add honey drop to sprite list
            self.honey_list.append(honey_drop)

        # Prevent bee and honey drop collisions
        for bee in self.bee_list:
            collision_list = arcade.check_for_collision_with_lists(
                                bee, [self.bee_list, self.honey_list])
            for bee in collision_list:
                bee.remove_from_sprite_lists()

        # Set and apply physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.bee_list
        )

    def on_draw(self):
        arcade.start_render()
        self.player_list.draw()
        self.bee_list.draw()
        self.honey_list.draw()

    def on_key_press(self, key: int, modifiers: int):
        """What happens when a key is pressed"""
        if key in [arcade.key.W, arcade.key.UP]:
            self.player.change_y = PLAYER_MOVE_SPEED
            self.player.angle = 0
        elif key in [arcade.key.S, arcade.key.DOWN]:
            self.player.change_y = -PLAYER_MOVE_SPEED
            self.player.angle = 180
        elif key in [arcade.key.D, arcade.key.RIGHT]:
            self.player.change_x = PLAYER_MOVE_SPEED
            self.player.angle = 270
        elif key in [arcade.key.A, arcade.key.LEFT]:
            self.player.change_x = -PLAYER_MOVE_SPEED
            self.player.angle = 90

    def on_key_release(self, key: int, modifiers: int):
        """What happens when key is released"""
        if key in [arcade.key.W, arcade.key.UP]:
            self.player.change_y = 0
        elif key in [arcade.key.S, arcade.key.DOWN]:
            self.player.change_y = 0
        elif key in [arcade.key.D, arcade.key.RIGHT]:
            self.player.change_x = 0
        elif key in [arcade.key.A, arcade.key.LEFT]:
            self.player.change_x = 0

    def on_update(self, delta_time: float):
        """Updates position of game objects, based on delta_time"""

        # randomly periodically rotate bees
        for bee in self.bee_list:
            if random.randint(0, 30) == 30:
                bee.angle = random.randrange(0, 360)

        # Prevent bee and honey drop collisions
        collision_list = arcade.check_for_collision_with_list(
                                self.player, self.honey_list)
        for honey_drop in collision_list:
            honey_drop.remove_from_sprite_lists()

        self.bee_list.update()
        self.honey_list.update()
        self.player_list.update()
        self.physics_engine.update()


class Player(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)


class Bee(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)


class Honey_Drop(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)


def main():
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()

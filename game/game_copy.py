# Author: Jacob Russell
# Date: 12-07-2022
# Descrption: "Honey Do" is a game that I made for my hot wife
# where you are a little robber bee who steals honey

# TODO list:
# Make player start random, but no collisions
# Add short flights for player
    # change player sprite to a "shadow" of the sprint
    # to simulate flying above. turn off collision detection
    # until landing. put a limit on how far you can go during
    # flight. Press space-bar to activate.
# Honey drop collection gives points
# Add a background image (honeycomb)
# Add honey drop licking action?
# Make walls on screen edges
# Add a hive "exit"?
# Bumping bees causes player damage
# More sprites to show "animation" (e.g. wings moving)
# Set range for random bee rotations relative to starting angle
# Make a side panel GUI with controls and score?


import arcade
import random
# import math

# ################## GLOBAL CONSTANTS ##################

# Screen/Window/Scene:
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_TITLE = "Honey Robber"
BACKGROUND_COLOR = arcade.color.DARK_GOLDENROD

# Sprites:
BEE_SPRITE_DEFAULT = "../assets/sprites/bee.png"
PLAYER_SPRITE_DEFAULT = "../assets/sprites/bee_player.png"
HONEY_SPRITE_DEFAULT = "../assets/sprites/honey_drop.png"
BEE_SPRITE_SCALE = 1.5
HONEY_SPRITE_SCALE = 1.5
PLAYER_SPRITE_SCALE = 1.2
BEE_SPRITE_COUNT = 100
HONEY_SPRITE_COUNT = 30


# ################### CLASSES & METHODS ##################

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
        self.walls_list = arcade.SpriteList()  # TODO: will be used for walls later

        # Create and position player
        self.player = Player("../assets/sprites/bee_player.png", 1.2)
        self.player_list.append(self.player)
        self.position_sprite(self.player)  # randomly position player

        # Create bee and position bees
        self.bee_list = [Bee("../assets/sprites/bee.png", 1.5) for i in range(BEE_SPRITE_COUNT)]
        print(self.bee_list)
        self.position_sprites(self.bee_list)  # randomly position bees

        # Create and position honey drops
        self.honey_list = [Honey_Drop("../assets/sprites/honey_drop.png", 1.5) for i in range(HONEY_SPRITE_COUNT)]
        self.position_sprites(self.honey_list)  # randomly position honey drops

        # Prevent bee and honey drop collisions
        for bee in self.bee_list:
            collision_list = arcade.check_for_collision_with_lists(
                                bee, [self.bee_list, self.honey_list])
            for bee in collision_list:
                bee.remove_from_sprite_lists()  # any collisions, remove bee

        # Randomize player position. Change position until no collisions
        while arcade.check_for_collision_with_lists(
                                self.player, [self.bee_list, self.honey_list]):
            self.position_sprites(self.player_list)


        # Set physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.wall_list,
        )

    def position_sprite(self, sprite, pos_x=None, pos_y=None) -> None:
        """Takes list of sprites and positions. Position defaults to random.
        Adds padding to ensure sprites don't overlap with screen border"""
        padding = 15  # how many pixels sprite center is from screen edges
        if pos_x is None:
            pos_x = random.randint(padding, (SCREEN_WIDTH - padding))
        if pos_y is None:
            pos_y = random.randint(padding, (SCREEN_HEIGHT - padding))
        sprite.center_x = pos_x
        sprite.center_y = pos_y

    def position_sprites(self, sprites_list: list, pos_x=None, pos_y=None) -> None:
        """Takes list of sprites and positions. Position defaults to random.
        Adds padding to ensure sprites don't overlap with screen border"""
        padding = 15  # how many pixels sprite center is from screen edges
        if pos_x is None:
            pos_x = random.randint(padding, (SCREEN_WIDTH - padding))
        if pos_y is None:
            pos_y = random.randint(padding, (SCREEN_HEIGHT - padding))
        for sprite in sprites_list:
            sprite.center_x = pos_x
            sprite.center_y = pos_y

    def on_draw(self):
        """Render screen and draw sprites"""
        arcade.start_render()
        self.player_list.draw()
        self.bee_list.draw()
        self.honey_list.draw()

        # Display the score
        arcade.draw_text("Honey: " + self.player.score, SCREEN_WIDTH - 15,
                         SCREEN_HEIGHT - 10, arcade.color.WHITE, 15, 20, 'right')

    def on_key_press(self, key: int, modifiers: int):
        """What happens when a key is pressed"""
        if key in [arcade.key.W, arcade.key.UP]:
            self.player.change_y = self.player.movement_speed
            self.player.angle = 0
        elif key in [arcade.key.S, arcade.key.DOWN]:
            self.player.change_y = -self.player.movement_speed
            self.player.angle = 180
        elif key in [arcade.key.D, arcade.key.RIGHT]:
            self.player.change_x = self.player.movement_speed
            self.player.angle = 270
        elif key in [arcade.key.A, arcade.key.LEFT]:
            self.player.change_x = -self.player.movement_speed
            self.player.angle = 90
        elif key in [arcade.key.SPACE]:
            pass


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

        # When player touches honey drop, increment score
        collision_list = arcade.check_for_collision_with_list(
                                self.player, self.honey_list)
        for honey_drop in collision_list:
            honey_drop.remove_from_sprite_lists()  # remove honey drop
            self.player.score += 1  # update player score

        # When player touches a bee, decrement score
        if arcade.check_for_collision_with_list(self.player, self.bee_list):
            self.player.score -= 1

        # Update all sprites
        self.bee_list.update()
        self.honey_list.update()
        self.player_list.update()
        self.physics_engine.update()

    # TODO: NOT CURRENTLY IN USE, MAY DELETE:
    def collisions(self, sprite, sprite_list: list) -> list:
        """Returns list of collisions between given sprite and
        sprite list(s)"""
        if sprite_list[0] is list:  # if multiple lists given
            return arcade.check_for_collision_with_lists(sprite, sprite_list)
        return arcade.check_for_collision_with_list(sprite, sprite_list)


class Player(arcade.Sprite):
    def __init__(self, filename=PLAYER_SPRITE_DEFAULT, scale=PLAYER_SPRITE_SCALE):
        super().__init__(filename, scale)

        self.score = 0
        self.scale = scale
        # self.start_pos_x = 300
        # self.start_pos_y = 400
        self.filename = filename
        self.movement_speed = 3
        self.angle_speed = 3
        self.flying = False

    def __str__(self):
        return f"filename: {self.filename}, scale {self.scale}"


class Bee(arcade.Sprite):
    def __init__(self, filename=BEE_SPRITE_DEFAULT, scale=BEE_SPRITE_SCALE):
        super().__init__(filename, scale)

        self.scale = scale
        self.filename = filename

    def __str__(self):
        return f"filename: {self.filename}, scale {self.scale}"

class Honey_Drop(arcade.Sprite):
    def __init__(self, filename=HONEY_SPRITE_DEFAULT, scale=HONEY_SPRITE_SCALE):
        super().__init__(filename, scale)

        self.scale = scale
        self.filename = filename

    def __str__(self):
        return f"filename: {self.filename}, scale {self.scale}"

# ################# DRIVER CODE #######################

def main():
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()

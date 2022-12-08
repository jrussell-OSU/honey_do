# Author: Jacob Russell
# Date: 12-07-2022
# Descrption: "Honey Do" is a game that I made
# for my hot wife where you are a little bee

# TODO list:
# Make player start random, but no collisions
# Add short flights for player
# Honey drop collection gives points
# Add a background image (honeycomb)
# Add honey drop licking action?
# Make walls on screen edges
# Add a hive "exit"?
# Bumping bees causes player damage
# More sprites to show "animation" (e.g. wings moving)
# Set range for random bee rotations relative to starting angle


import arcade
import random
# import math

# ################## GLOBAL CONSTANTS ##################

# Screen Settings:
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_TITLE = "Honey Thief"
BACKGROUND_COLOR = arcade.color.DARK_GOLDENROD

# Player Sprite Settings:
# PLAYER_SPRITE_SCALING = 1.2
# PLAYER_START_POS_X = 300
# PLAYER_START_POS_Y = 400
# PLAYER_SPRITE_IMAGE = "../assets/sprites/bee_player.png"
# PLAYER_MOVE_SPEED = 3
# PLAYER_ANGLE_SPEED = 3

# Bee Sprite Settings:
BEE_SPRITE_COUNT = 100
# BEE_SPRITE_SCALING = 1.5
# BEE_SPRITE_IMAGE = "../assets/sprites/bee.png"

# Honey Sprite Settings:
# HONEY_SPRITE_SCALING = 1.5
HONEY_SPRITE_COUNT = 30
# HONEY_SPRITE_IMAGE = "../assets/sprites/honey_drop.png"


# ################### CLASSES / METHODS ##################


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
        self.player = Player()
        self.player_list.append(self.player)

        # Create bee and position bees
        self.bee_list = [Bee() for i in range(BEE_SPRITE_COUNT)]
        position_sprites(bee_list)  # randomly position bees

        # Create and position honey drops
        self.honey_list = [Honey_Drop() for i in range(HONEY_SPRITE_COUNT)]
        position_sprites(honey_list)  # randomly position honey drops

        # Prevent bee and honey drop collisions
        for bee in self.bee_list:
            collision_list = arcade.check_for_collision_with_lists(
                                bee, [self.bee_list, self.honey_list])
            for bee in collision_list:
                bee.remove_from_sprite_lists()  # any collisions, remove bee

        # Randomize player position. Change position until no collisions
        while arcade.check_for_collision_with_lists(
                                player, [self.bee_list, self.honey_list]):
            position_sprites(player_list)
            
                
        # Set physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.bee_list, self.honey_list
        )
        
    def position_sprites(sprites_list: list, x_pos=None, y_pos=None) -> None:
        """Takes list of sprites and positions. Position defaults to random.
        Adds padding to ensure sprites don't overlap with screen border"""
        padding = 15  # how many pixels sprite center is from screen edges 
        if x_pos is None:
            x_pos = random.randint(padding, (SCREEN_WIDTH - padding))
        if y_pos is None:
            y_pos = random.randint(padding, (SCREEN_HEIGHT - padding))
        for sprite in sprites_list:
            sprite.center_x = x_pos
            sprite.center_y = y_pos
            
    def on_draw(self):
        """Render screen and draw sprites"""
        arcade.start_render()
        self.player_list.draw()
        self.bee_list.draw()
        self.honey_list.draw()
        
        # Display the score
        arcade.draw_text(self.player.score, SCREEN_WIDTH - 10, SCREEN_HEIGHT + 10,
                         arcade.color.WHITE, 15, 20, 'right')

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

        # When player touches honey drop
        collision_list = arcade.check_for_collision_with_list(
                                self.player, self.honey_list)
        for honey_drop in collision_list:  
            honey_drop.remove_from_sprite_lists()  # remove honey drop
            player.score += 1  # update player score

        # Update all sprites
        self.bee_list.update()
        self.honey_list.update()
        self.player_list.update()
        self.physics_engine.update()


class Player(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)
        
        self.score = 0
        self.scaling = 1.2
        self.start_pos_x = 300
        self.start_pos_y = 400
        self.sprite_image = "../assets/sprites/bee_player.png"
        self.movement_speed = 3
        self.angle_speed = 3
        
class Bee(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)
        
        self.scaling = 1.5
        self.initial_image = "../assets/sprites/bee.png"

class Honey_Drop(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)

        self.scaling = 1.5
        self.initial_image = "../assets/sprites/honey_drop.png"


# ################# DRIVER CODE #######################
        
def main():
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()

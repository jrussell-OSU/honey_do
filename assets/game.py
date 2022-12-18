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
# More sprites to show "animation" (e.g. wings walking)
# When hitting a bee, player bounces back


import arcade
import random
# from PIL import Image
# import typing

# ################## GLOBAL CONSTANTS ##################

# Screen Settings:
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_TITLE = "Honey Thief"
BACKGROUND_COLOR = arcade.color.WARM_BLACK
BACKGROUND_IMAGE = "../assets/sprites/honeycomb.png"
PADDING = 25  # how many pixels from edge of screen to place sprites

# Player Sprite Settings:
PLAYER_SPRITE_SCALING = 1.2
PLAYER_SPRITE_IMAGE = "../assets/sprites/bee_player.png"
PLAYER_MOVE_SPEED = 1.5
ANIMATION_SPEED = 3  # lower = slow, higher = faster
PLAYER_ANGLE_SPEED = 3

# Bee Sprite Settings:
BEE_SPRITE_COUNT = 75
BEE_SPRITE_SCALING = 1.5
BEE_SPRITE_IMAGE = "../assets/sprites/bee.png"

# Honey Sprite Settings:
HONEY_SPRITE_SCALING = 1.5
HONEY_SPRITE_COUNT = 30
HONEY_SPRITE_IMAGE = "../assets/sprites/honey_drop.png"


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
        self.background = arcade.load_texture(BACKGROUND_IMAGE)

        # Create sprite lists
        self.player_list = arcade.SpriteList()
        self.bee_list = arcade.SpriteList()
        self.honey_list = arcade.SpriteList()
        self.wall_list = []

        # Create combined list of all sprites:
        self.all_sprite_lists = [
            self.player_list,
            self.bee_list,
            self.honey_list
        ]

        # Create and position player
        self.player = Player(PLAYER_SPRITE_IMAGE, PLAYER_SPRITE_SCALING)
        self.sprite_random_pos(self.player)
        self.player_list.append(self.player)

        # Create bees with random position and angle, then add to list
        for i in range(BEE_SPRITE_COUNT):
            bee = Bee(BEE_SPRITE_IMAGE, BEE_SPRITE_SCALING)
            self.sprite_random_pos(bee)
            bee.angle = random.randrange(0, 360)
            self.bee_list.append(bee)

        # Create honey drops with random position and angle, then add to list
        for i in range(HONEY_SPRITE_COUNT):
            honey_drop = Honey_Drop(HONEY_SPRITE_IMAGE, HONEY_SPRITE_SCALING)
            self.sprite_random_pos(honey_drop)
            self.honey_list.append(honey_drop)

        # Make transparent border to level
        arcade.draw_lrtb_rectangle_outline((0, 0, 0, 0))

        # Set and apply physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.wall_list
        )

    def sprite_random_pos(self, sprite):
        """Move sprite to a random position (until no collisions detected)."""
        sprite.center_x = random.randint(PADDING,
                                         (SCREEN_WIDTH - PADDING))
        sprite.center_y = random.randint(PADDING,
                                         (SCREEN_HEIGHT - PADDING))
        while arcade.check_for_collision_with_lists(sprite,
                                                    self.all_sprite_lists):
            sprite.center_x = random.randint(PADDING,
                                             (SCREEN_WIDTH - PADDING))
            sprite.center_y = random.randint(PADDING,
                                             (SCREEN_HEIGHT - PADDING))

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        self.player_list.draw()
        self.bee_list.draw()
        self.honey_list.draw()
        arcade.draw_text("Honey:" + str(self.player.score), SCREEN_WIDTH-120,
                         SCREEN_HEIGHT-20, arcade.color.WHITE, 15, 20, 'right')

    def on_key_press(self, key: int, modifiers: int):
        """What happens when a key is pressed"""

        if key in [arcade.key.W, arcade.key.UP]:
            self.player.change_y = PLAYER_MOVE_SPEED
            self.player.angle = 0
            self.player.walking = True
        elif key in [arcade.key.S, arcade.key.DOWN]:
            self.player.change_y = -PLAYER_MOVE_SPEED
            self.player.angle = 180
            self.player.walking = True
        elif key in [arcade.key.D, arcade.key.RIGHT]:
            self.player.change_x = PLAYER_MOVE_SPEED
            self.player.angle = 270
            self.player.walking = True
        elif key in [arcade.key.A, arcade.key.LEFT]:
            self.player.change_x = -PLAYER_MOVE_SPEED
            self.player.angle = 90
            self.player.walking = True
        elif key in [arcade.key.SPACE]:
            shadow = arcade.load_texture("../assets/sprites/bee_shadow1.png")
            self.player.texture = shadow
            self.player.flying = True

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
        elif key in [arcade.key.SPACE]:
            self.player.flying = False
            self.player.texture = arcade.load_texture("../assets/sprites/bee_player.png")
        self.player.walking = False

    def on_update(self, delta_time: float):
        """Updates position of game objects, based on delta_time"""

        # randomly periodically rotate bees
        for bee in self.bee_list:
            if random.randint(0, 30) == 30:
                bee.angle = random.randrange(0, 360)

        # When player touches honey drop
        collision_list = arcade.check_for_collision_with_list(
                                self.player, self.honey_list)
        if not self.player.flying:  # if player isn't flying
            for honey_drop in collision_list:
                honey_drop.remove_from_sprite_lists()  # remove honey drop
                self.player.score += 3  # update player score

        # When player touches a bee, decrement score
        if arcade.check_for_collision_with_list(self.player, self.bee_list):
            if not self.player.flying:  # no collisions if flying
                self.player.score -= 1
        if self.player.score < 0:  # score can't be negative
            self.player.score = 0

        # Update all sprites
        for sprite_list in self.all_sprite_lists:
            sprite_list.update()
        if self.player.walking:  # animation
            self.player_list.update_animation()
        self.physics_engine.update()


class Player(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)

        self.score = 0
        self.texture_index = 0  # tracks current texture
        self.walking = False  # whether player is walking
        self.frame = 0  # tracks frames for animations
        self.flying = False

        # Setup and load walking animation textures
        self.walking_textures = []
        self.walking_texture_paths = [
            "../assets/sprites/bee_player_move1.png",
            "../assets/sprites/bee_player_move2.png"
        ]
        for filepath in self.walking_texture_paths:
            self.walking_textures.append(arcade.load_texture(filepath))

        # Setup and load flying animation textures
        self.flying_textures = []
        self.flying_texture_paths = [
            "../assets/sprites/bee_shadow1.png",
            "../assets/sprites/bee_shadow2.png"
        ]
        for filepath in self.flying_texture_paths:
            self.flying_textures.append(arcade.load_texture(filepath))

    def update_animation(self, delta_time: float = 1/60) -> None:

        # player animation
        textures = []
        if self.flying:
            textures = self.flying_textures
        elif self.walking:
            textures = self.walking_textures
        self.frame += 1
        if self.frame % (20 // ANIMATION_SPEED) == 0:
            self.texture = textures[self.texture_index]
            self.texture_index = (self.texture_index + 1) % 2


class Bee(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)


class Honey_Drop(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)


# ################# DRIVER CODE #######################

def main():
    window = Game(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
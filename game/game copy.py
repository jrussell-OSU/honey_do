# Author: Jacob Russell
# Date: 12-07-2022
# Descrption: "Honey Do" is a game that I made
# for my hot wife where you are a little bee

# Reference: relies on docs and examples from https://api.arcade.academy/

# TODO list:
# Add time limit to flights
# random color honeycomb background and bees for each new hive
# choose your own player color wheel
# GUI
# tongue sticks out when collecting honey_drop
# when exit the hive, change to a side scroller where you
#       have to dodge stuff while flying
# side scroll could have procedural background
#       e.g. draw a couple trees and houses, then have a random number
#       of them randomly placed in scrolling background
# make screen dimmer inside hive?
# the more honey you have, the shorter your flights in the hive
# and more sluggish in side scroll
# Gameplay:
#   start at home hive
#        it's clearly not looking good, most cells are empty
#        maybe you can talk to some of the bees?
#   exit home hive, enter side scrolling platformer
#       You have to dodge stuff in your flight (e.g. wasps,
#           cars, birds, whatever)
#       if you hit too many, you must return home to try again
#       at end of side scroll, you enter another bee hive
#       you have to steal as much honey as possible, then leave
#       side scroll again, where you lose honey when you get hit
#       get home, you give them honey, everyone celebrates
#       fades to black then comes back in to show a number of filled cells
#       based on how much honey you got. also more bees are dancing
#
#

import arcade
import random


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
HONEY_SPRITE_COUNT = 15
HONEY_SPRITE_IMAGE = "../assets/sprites/honey_drop.png"

WALL_SPRITE_IMAGE = "../assets/sprites/wall_small_black.png"

# ################### CLASSES / METHODS ##################


class Game(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.scene = None
        self.scene_name = None  # what scene we are in
        self.player = None
        self.physics_engine = None
        self.sounds = {
            "hurt": arcade.load_sound("../assets/sounds/hurt.wav"),
            "honey_drop": arcade.load_sound("../assets/sounds/honey_drop.wav"),
            "background": arcade.load_sound(
                "../assets/sounds/background.wav", streaming=True),
            "jump": arcade.load_sound("../assets/sounds/jump.wav")
        }

    # *************** MAIN GAME METHODS *********************

    def setup(self):
        """Sets up the game for the current level"""

        self.scene = arcade.Scene()
        self.setup_scene_hive()  # set up first level, inside a hive

    def place_borders(self):
        # Create invisible border around scene

        vertical_pos = [[0, SCREEN_HEIGHT / 2],
                        [SCREEN_WIDTH, SCREEN_HEIGHT / 2]]
        horizontal_pos = [[SCREEN_WIDTH / 2, 0],
                          [SCREEN_WIDTH / 2, SCREEN_HEIGHT]]

        for pos in vertical_pos:
            wall = Wall(WALL_SPRITE_IMAGE, 1)
            wall.position = pos
            wall.alpha = 0
            wall.height = SCREEN_HEIGHT
            wall.width = 2
            self.scene.add_sprite("Walls", wall)

        for pos in horizontal_pos:
            wall = Wall(WALL_SPRITE_IMAGE, 1)
            wall.position = pos
            wall.alpha = 0
            wall.height = 2
            wall.width = SCREEN_WIDTH
            self.scene.add_sprite("Walls", wall)

    def sprite_random_pos(self, sprite, padding=PADDING):
        """Move sprite to a random position (until no collisions detected)."""
        sprite.center_x = random.randint(padding,
                                         (SCREEN_WIDTH - padding))
        sprite.center_y = random.randint(padding,
                                         (SCREEN_HEIGHT - padding))
        while arcade.check_for_collision_with_lists(sprite,
                                                    self.scene.sprite_lists):
            sprite.center_x = random.randint(padding,
                                             (SCREEN_WIDTH - padding))
            sprite.center_y = random.randint(padding,
                                             (SCREEN_HEIGHT - padding))

    def on_draw(self):
        """Draws game objects inside of game window"""
        self.clear()

        if self.scene_name == "hive":
            self.draw_hive()
        elif self.scene_name == "outside":
            self.draw_outside()

    def on_key_press(self, key: int, modifiers: int):
        """What happens when a key is pressed"""
        if key == arcade.key.ESCAPE:
            #arcade.close_window()
            pass

        if self.scene_name == "hive":
            self.key_press_hive(key, modifiers)
        elif self.scene_name == "outside":
            self.key_press_outside(key, modifiers)

    def on_key_release(self, key: int, modifiers: int):
        """What happens when key is released"""

        if self.scene_name == "hive":
            self.key_release_hive(key, modifiers)
        elif self.scene_name == "outside":
            self.key_release_outside(key, modifiers)

    def update_player_speed(self):
        if self.scene_name == "hive":
            self.update_player_speed_hive()
        elif self.scene_name == "outside":
            self.update_player_speed_outside()

    def on_update(self, delta_time: float):
        """Updates position of game objects, based on delta_time"""

        if self.scene_name == "hive":
            self.update_hive()

        elif self.scene_name == "outside":
            self.update_outside()

    # *************** HIVE SCENE METHODS *********************

    def setup_scene_hive(self):
        """Sets up a hive scene"""

        # will be used when we need to change controls or other methods
        # after a scene is changed (e.g. one scene is top-down, the next
        # is side scrolling)
        self.scene_name = "hive"

        arcade.set_background_color(BACKGROUND_COLOR)
        self.background = arcade.load_texture(BACKGROUND_IMAGE)

        # Create sprite lists
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Exits")
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Bees")
        self.scene.add_sprite_list("Honey")

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Create invisible screen borders
        self.place_borders()

        # Create and place exit hole
        exit_hole = arcade.Sprite("../assets/sprites/exit_hole_blurry1.png",
                                  scale=1)
        self.sprite_random_pos(exit_hole, padding=100)
        self.scene.add_sprite("Exits", exit_hole)

        # Create and position player
        self.player = Player(PLAYER_SPRITE_IMAGE, PLAYER_SPRITE_SCALING)
        self.sprite_random_pos(self.player)
        self.scene.add_sprite("Player", self.player)

        # Create bees with random position and angle, then add to list
        for i in range(BEE_SPRITE_COUNT):
            bee = Bee(BEE_SPRITE_IMAGE, BEE_SPRITE_SCALING)
            self.sprite_random_pos(bee)
            bee.angle = random.randrange(0, 360)
            self.scene.add_sprite("Bees", bee)

        # Create honey drops with random position and angle, then add to list
        for i in range(HONEY_SPRITE_COUNT):
            honey = Honey_Drop(HONEY_SPRITE_IMAGE, HONEY_SPRITE_SCALING)
            self.sprite_random_pos(honey)
            self.scene.add_sprite("Honey", honey)

        # Background Sound Track
        # arcade.play_sound(self.sounds["background"], looping=True)

        # Set and apply physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene.name_mapping["Walls"]
        )

    def draw_hive(self):
        """Draws hive scene"""
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)

        self.scene.draw()
        arcade.draw_text("Honey:" + str(self.player.score),
                         SCREEN_WIDTH-120, SCREEN_HEIGHT-20,
                         arcade.color.WHITE, 15, 20, 'right')

    def key_press_hive(self, key: int, modifiers: int):
        """Key press behavior for hive scene"""

        if key in [arcade.key.W, arcade.key.UP]:
            self.up_pressed = True
            self.update_player_speed()
        elif key in [arcade.key.S, arcade.key.DOWN]:
            self.down_pressed = True
            self.update_player_speed()
        elif key in [arcade.key.D, arcade.key.RIGHT]:
            self.right_pressed = True
            self.update_player_speed()
        elif key in [arcade.key.A, arcade.key.LEFT]:
            self.left_pressed = True
            self.update_player_speed()
        elif key in [arcade.key.SPACE]:
            # arcade.play_sound(self.sounds["jump"], speed=2.0)
            shadow = arcade.load_texture(
                "../assets/sprites/bee_shadow1.png")
            self.player.texture = shadow
            self.player.flying = True

    def key_release_hive(self, key: int, modifiers: int):

        if key in [arcade.key.W, arcade.key.UP]:
            self.player.change_y = 0
            self.up_pressed = False
            self.update_player_speed()
        elif key in [arcade.key.S, arcade.key.DOWN]:
            self.player.change_y = 0
            self.down_pressed = False
            self.update_player_speed()
        elif key in [arcade.key.D, arcade.key.RIGHT]:
            self.player.change_x = 0
            self.right_pressed = False
            self.update_player_speed()
        elif key in [arcade.key.A, arcade.key.LEFT]:
            self.player.change_x = 0
            self.left_pressed = False
            self.update_player_speed()
        elif key in [arcade.key.SPACE]:
            self.player.flying = False
            self.player.texture = arcade.load_texture(
                "../assets/sprites/bee_player.png")
        self.player.walking = False

    def update_player_speed_hive(self):

        # Calculate speed based on the keys pressed
        self.player.change_x = 0
        self.player.change_y = 0

        if self.up_pressed and not any([self.down_pressed,
                                        self.left_pressed,
                                        self.right_pressed]):
            self.player.change_y = PLAYER_MOVE_SPEED
            self.player.angle = 0
            self.player.walking = True
        elif self.down_pressed and not any([self.up_pressed,
                                            self.left_pressed,
                                            self.right_pressed]):
            self.player.change_y = -PLAYER_MOVE_SPEED
            self.player.angle = 180
            self.player.walking = True
        if self.left_pressed and not any([self.up_pressed,
                                          self.down_pressed,
                                          self.right_pressed]):
            self.player.change_x = -PLAYER_MOVE_SPEED
            self.player.angle = 90
            self.player.walking = True
        elif self.right_pressed and not any([self.up_pressed,
                                            self.down_pressed,
                                            self.left_pressed]):
            self.player.change_x = PLAYER_MOVE_SPEED
            self.player.angle = 270
            self.player.walking = True

    def update_hive(self):

        if any([self.up_pressed, self.down_pressed,
                self.left_pressed, self.right_pressed]):
            self.player.walking = True
        else:
            self.player.walking = False

        # randomly periodically rotate bees
        for bee in self.scene["Bees"]:
            if random.randint(0, 30) == 30:
                bee.angle = random.randrange(0, 360)

        # When player touches exit
        if arcade.check_for_collision_with_list(
                                self.player, self.scene.name_mapping["Exits"]):
            self.scene = arcade.Scene()
            self.setup_scene_hive()

        # When player touches honey drop
        collision_list = arcade.check_for_collision_with_list(
                                self.player, self.scene.name_mapping["Honey"])
        if not self.player.flying:  # if player isn't flying
            for honey_drop in collision_list:
                arcade.play_sound(self.sounds["honey_drop"])
                honey_drop.remove_from_sprite_lists()  # remove honey drop
                self.player.score += 1  # update player score

        # When player touches a bee, decrement score
        # if player isn't already being "hurt" by bee
        if arcade.check_for_collision_with_list(
                self.player, self.scene.name_mapping["Bees"]):
            if not self.player.hurt and not self.player.flying:
                self.player.hurt = True
                arcade.play_sound(self.sounds["hurt"])
                if self.player.score > 0:  # score can't be negative
                    self.player.score -= 1
        else:  # if we aren't being hurt by a bee
            self.player.hurt = False

        # Update all sprites
        for sprite_list in self.scene.sprite_lists:
            sprite_list.update()
        if self.player.flying:
            self.player.update_animation()
        elif self.player.hurt:
            self.player.update_animation()
        elif self.player.walking:  # animation
            self.player.update_animation()
        self.physics_engine.update()

    # *************** OUTSIDE SCENE METHODS *********************

    def setup_scene_outside(self):
        pass

    def draw_outside(self):
        """Draws outside scene"""
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)

        self.scene.draw()
        arcade.draw_text("Honey:" + str(self.player.score),
                         SCREEN_WIDTH-120, SCREEN_HEIGHT-20,
                         arcade.color.WHITE, 15, 20, 'right')

    def key_press_outside(self, key: int, modifiers: int):

        if key in [arcade.key.W, arcade.key.UP]:
            self.up_pressed = True
            self.update_player_speed()
        elif key in [arcade.key.S, arcade.key.DOWN]:
            self.down_pressed = True
            self.update_player_speed()
        elif key in [arcade.key.D, arcade.key.RIGHT]:
            self.right_pressed = True
            self.update_player_speed()
        elif key in [arcade.key.A, arcade.key.LEFT]:
            self.left_pressed = True
            self.update_player_speed()
        elif key in [arcade.key.SPACE]:
            pass

    def key_release_outside(self, key: int, modifiers: int):

        if key in [arcade.key.W, arcade.key.UP]:
            self.player.change_y = 0
            self.up_pressed = False
            self.update_player_speed()
        elif key in [arcade.key.S, arcade.key.DOWN]:
            self.player.change_y = 0
            self.down_pressed = False
            self.update_player_speed()
        elif key in [arcade.key.D, arcade.key.RIGHT]:
            self.player.change_x = 0
            self.right_pressed = False
            self.update_player_speed()
        elif key in [arcade.key.A, arcade.key.LEFT]:
            self.player.change_x = 0
            self.left_pressed = False
            self.update_player_speed()
        elif key in [arcade.key.SPACE]:
            self.player.flying = False
            self.player.texture = arcade.load_texture(
                "../assets/sprites/bee_player.png")
        self.player.walking = False

    def update_player_speed_outside(self):

        # Calculate speed based on the keys pressed
        self.player.change_x = 0
        self.player.change_y = 0

        if self.up_pressed and not any([self.down_pressed,
                                        self.left_pressed,
                                        self.right_pressed]):
            self.player.change_y = PLAYER_MOVE_SPEED
            self.player.angle = 0
            self.player.walking = True
        elif self.down_pressed and not any([self.up_pressed,
                                            self.left_pressed,
                                            self.right_pressed]):
            self.player.change_y = -PLAYER_MOVE_SPEED
            self.player.angle = 180
            self.player.walking = True
        if self.left_pressed and not any([self.up_pressed,
                                          self.down_pressed,
                                          self.right_pressed]):
            self.player.change_x = -PLAYER_MOVE_SPEED
            self.player.angle = 90
            self.player.walking = True
        elif self.right_pressed and not any([self.up_pressed,
                                            self.down_pressed,
                                            self.left_pressed]):
            self.player.change_x = PLAYER_MOVE_SPEED
            self.player.angle = 270
            self.player.walking = True

    def update_outside(self):
        pass


class Player(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)

        self.score = 0
        self.texture_index = 0  # tracks current texture
        self.walking = False  # whether player is walking
        self.frame = 0  # tracks frames for animations
        self.flying = False
        self.hurt = False

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

        # Setup and load hurt animation textures
        self.hurt_textures = []
        self.hurt_texture_paths = [
            "../assets/sprites/player_hurt1.png",
            "../assets/sprites/player_hurt2.png"
            # "../assets/sprites/player_hurt3.png",
            # "../assets/sprites/player_hurt4.png",
        ]
        for filepath in self.hurt_texture_paths:
            self.hurt_textures.append(arcade.load_texture(filepath))

    def update_animation(self, delta_time: float = 1/60) -> None:

        # player animation
        if self.hurt:
            if self.frame % (20 // ANIMATION_SPEED) == 0:
                self.texture = self.hurt_textures[self.texture_index]
                # NOTE: MUST CHANGE THIS IF MORE THAN TWO TEXTURES USED
                self.texture_index = (self.texture_index + 1)\
                    % len(self.hurt_textures)
        elif self.flying:
            if self.frame % (20 // ANIMATION_SPEED) == 0:
                self.texture = self.flying_textures[self.texture_index]
                # NOTE: MUST CHANGE THIS IF MORE THAN TWO TEXTURES USED
                self.texture_index = (self.texture_index + 1)\
                    % len(self.flying_textures)
        elif self.walking:
            if self.frame % (20 // ANIMATION_SPEED) == 0:
                self.texture = self.walking_textures[self.texture_index]
                # NOTE: MUST CHANGE THIS IF MORE THAN TWO TEXTURES USED
                self.texture_index = (self.texture_index + 1)\
                    % len(self.walking_textures)
        self.frame += 1


class Wall(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)


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
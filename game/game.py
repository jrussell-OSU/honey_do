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
# tongue sticks out when collecting honey
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
# for neighborhood, remove alls treets with potholes (it's ugly)
#       and instead add street tiles with cars on them for variety
#
#  consider making a different outdoor scene in a forest... would be nicer
# add exit hole sprites


# Use multiple inheritance to make a "Level" class with the methods of
# Game

import arcade
import random
from pyglet.math import Vec2


# ################## GLOBAL CONSTANTS ##################

# Screen Settings:
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MAIN_VIEW_WIDTH = 800
MAIN_VIEW_HEIGHT = 600
GAME_TITLE = "Honey Thief"
BACKGROUND_COLOR = arcade.color.BLACK
BACKGROUND_IMAGE = "../assets/backgrounds/honeycomb.png"
HOME_BACKGROUND = "../assets/backgrounds/honeycomb_map_pink_empty.png"
EXIT_HOLE_YELLOW = "../assets/sprites/exit_hole_yellow.png"
EXIT_HOLE_PINK = "../assets/sprites/exit_hole_pink.png"
PADDING = 25  # how many pixels from edge of screen to place sprites
OUTSIDE_HEIGHT = 8896
CAMERA_SPEED = 2.0
OUTSIDE_IMAGE = "../assets/backgrounds/wilderness_neighborhood.png"
OUTSIDE_FLIPPED = "../assets/backgrounds/wilderness_neighborhood_flipped.png"
FADE_RATE = 5  # TODO: do fading of views


# Sprite Settings:
PLAYER_SPRITE_SCALING = 1.0
PLAYER_SPRITE_IMAGE = "../assets/sprites/bee_player_move1_2.png"
PLAYER_MOVE_SPEED = 1.75
ANIMATION_SPEED = 3  # lower = slow, higher = faster
PLAYER_ANGLE_SPEED = 3

BEE_ENEMY_COUNT = 75
BEE_ENEMY_SCALING = 1.5
BEE_ENEMY_IMAGE = "../assets/sprites/bee.png"
BEE_FRIEND_COUNT = 20
BEE_FRIEND_SCALING = 1.0
BEE_FRIEND_IMAGE = "../assets/sprites/bee_player_move1_2.png"

HONEY_SPRITE_SCALING = 1.25
HONEY_SPRITE_COUNT = 15
HONEY_SPRITE_IMAGE = "../assets/sprites/honey.png"

WALL_SPRITE_IMAGE = "../assets/sprites/wall_small_black.png"

WASP_SCALING = 1.5
WASP_IMAGE = "../assets/sprites/wasp_flying1.png"
WASP_SPEED_MIN = 7
WASP_SPEED_MAX = 8
WASP_ATTACK_INTERVAL = 3
WASP_SPACING = 150

# ################### CLASSES / METHODS ##################


class Window(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # will hold different screen views
        # (e.g., menu view, hivelevel view, outsidelevel view)
        # useful so different views have different controls etc.
        self.views = {}

        # only keyboard commands allowed
        # self.set_exclusive_keyboard(exclusive=True)

        self.player = Player(PLAYER_SPRITE_IMAGE, PLAYER_SPRITE_SCALING)

    def get_player(self):
        return self.player


class HiveView(arcade.View):
    def __init__(self):
        super().__init__()

        self.scene = arcade.Scene()
        # self.window.views["hive"] = HiveView()
        self.player = Player
        self.player = self.window.player  # save same player between views
        self.physics_engine = None
        self.sounds = {
            "hurt": arcade.load_sound("../assets/sounds/hurt.wav"),
            "honey": arcade.load_sound("../assets/sounds/honey.wav"),
            "background": arcade.load_sound(
                "../assets/sounds/background.wav", streaming=True),
            "jump": arcade.load_sound("../assets/sounds/jump.wav")
        }
        self.camera = arcade.Camera(self.window.width, self.window.height,
                                    self.window)

    def setup(self):
        """Sets up a hive scene"""

        print(f"Viewport: {arcade.get_viewport()}")

        self.exit_hole = EXIT_HOLE_YELLOW

        self.window.views["hive"] = self
        arcade.set_background_color(BACKGROUND_COLOR)
        self.background = arcade.load_texture(BACKGROUND_IMAGE)

        # Background Sound Track
        # arcade.play_sound(self.sounds["background"], looping=True)

        # Create sprite lists
        self.scene.add_sprite_list("Walls")  # , use_spatial_hash=True)
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
        exit_hole = arcade.Sprite(self.exit_hole,
                                  scale=1)
        self.sprite_random_pos(exit_hole, padding=100)
        self.scene.add_sprite("Exits", exit_hole)

        # Create and position player
        self.sprite_random_pos(self.player)
        self.scene.add_sprite("Player", self.player)

        # Create bees with random position and angle, then add to list
        for i in range(BEE_ENEMY_COUNT):
            bee = BeeEnemy(BEE_ENEMY_IMAGE, BEE_ENEMY_SCALING)
            self.sprite_random_pos(bee)
            bee.angle = random.randrange(0, 360)
            self.scene.add_sprite("Bees", bee)

        # Create honey drops with random position and angle, then add to list
        for i in range(HONEY_SPRITE_COUNT):
            honey = Honey(HONEY_SPRITE_IMAGE, HONEY_SPRITE_SCALING)
            self.sprite_random_pos(honey)
            self.scene.add_sprite("Honey", honey)

        # Set and apply physics engine
        # self.physics_engine = arcade.PhysicsEnginePlatformer(
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene.name_mapping["Walls"]
        )

    def sprite_random_pos(self, sprite: arcade.Sprite,
                          padding: int = PADDING) -> None:
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
        """Draws hive scene"""
        arcade.start_render()
        # arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        self.camera.use()
        self.scene.draw()
        arcade.draw_text("Honey:" + str(self.player.score),
                         SCREEN_WIDTH-120, SCREEN_HEIGHT-20,
                         arcade.color.WHITE, 15, 20, 'right')

    def change_view(self, view: arcade.View) -> None:
        # keys = key.KeyStateHandler()
        # print(keys)
        arcade.pause(1)
        view.setup()
        self.window.show_view(view)

    def place_borders(self):
        # Create invisible border around scene

        vertical_pos = [[0, SCREEN_HEIGHT / 2],
                        [SCREEN_WIDTH, SCREEN_HEIGHT / 2]]
        horizontal_pos = [[SCREEN_WIDTH / 2, 0],
                          [SCREEN_WIDTH / 2, SCREEN_HEIGHT]]

        for pos in vertical_pos:
            wall = Wall(WALL_SPRITE_IMAGE, position=pos, kind="veritical",
                        height=SCREEN_HEIGHT, width=2)
            self.scene.add_sprite("Walls", wall)

        for pos in horizontal_pos:
            wall = Wall(WALL_SPRITE_IMAGE, position=pos, kind="horizontal",
                        height=2, width=SCREEN_WIDTH)
            self.scene.add_sprite("Walls", wall)

    def on_key_press(self, key: int, modifiers: int):
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

    def on_key_release(self, key: int, modifiers: int):

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
                "../assets/sprites/bee_player_move1_2.png")
        self.player.walking = False

    def reset_controls(self):
        self.scene_over = True
        self.up_pressed = False
        self.down_pressed = False
        self.right_pressed = False
        self.left_pressed = False

    def update_player_speed(self):

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

    def on_update(self, delta_time: float):
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

            print("Exiting level...")
            # Clear the window, and setup the next scene
            # self.window.clear(viewport=(0, 800, 0, 600))
            # self.window.close()
            # arcade.open_window(SCREEN_WIDTH, SCREEN_HEIGHT)
            outside_view = OutsideView2()
            self.change_view(outside_view)
            # outside_view.setup()
            # self.window.show_view(outside_view)

        # When player touches honey drop
        collision_list = arcade.check_for_collision_with_list(
                                self.player, self.scene.name_mapping["Honey"])
        if not self.player.flying:  # if player isn't flying
            for honey in collision_list:
                arcade.play_sound(self.sounds["honey"])
                honey.remove_from_sprite_lists()  # remove honey drop
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
        self.player.update_animation()
        self.physics_engine.update()


class HiveHome(HiveView):
    def __init__(self):
        super().__init__()

        self.exit_hole = EXIT_HOLE_PINK
        self.scene = arcade.Scene()
        self.scene_over = False  # whether done with this scene (trigger)
        # self.window.views["hive"] = HiveView()
        self.player = Player
        self.player = self.window.player  # save same player between views
        self.physics_engine = None
        self.sounds = {
            "hurt": arcade.load_sound("../assets/sounds/hurt.wav"),
            "honey": arcade.load_sound("../assets/sounds/honey.wav"),
            "background": arcade.load_sound(
                "../assets/sounds/background.wav", streaming=True),
            "jump": arcade.load_sound("../assets/sounds/jump.wav")
        }
        self.camera = arcade.Camera(self.window.width, self.window.height,
                                    self.window)

    def setup(self):
        """Sets up a hive scene"""

        print(f"Viewport: {arcade.get_viewport()}")
        # self.camera.move_to()

        self.window.views["home"] = self
        arcade.set_background_color(BACKGROUND_COLOR)
        self.background = arcade.load_texture(HOME_BACKGROUND)

        # Background Sound Track
        # arcade.play_sound(self.sounds["background"], looping=True)

        # Create sprite lists
        self.scene.add_sprite_list("Walls")  # , use_spatial_hash=True)
        self.scene.add_sprite_list("Exits")
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Bees")

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Create invisible screen borders
        self.place_borders()

        # Create and place exit hole
        exit_hole = arcade.Sprite(self.exit_hole,
                                  scale=1)
        self.sprite_random_pos(exit_hole, padding=100)
        self.scene.add_sprite("Exits", exit_hole)

        # Create and position player
        self.sprite_random_pos(self.player)
        self.scene.add_sprite("Player", self.player)

        # Create bees with random position and angle, then add to list
        for i in range(BEE_FRIEND_COUNT):
            bee = BeeFriend(BEE_FRIEND_IMAGE, BEE_FRIEND_SCALING)
            self.sprite_random_pos(bee)
            bee.angle = random.randrange(0, 360)
            self.scene.add_sprite("Bees", bee)

        # self.print_messages()  # print narration/instruction to player

        # Set and apply physics engine
        # self.physics_engine = arcade.PhysicsEnginePlatformer(
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene.name_mapping["Walls"]
        )

    def on_draw(self):
        """Draws hive scene"""
        arcade.start_render()
        # arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        self.camera.use()
        self.scene.draw()
        self.print_messages()
        arcade.draw_text("Honey:" + str(self.player.score),
                         SCREEN_WIDTH-120, SCREEN_HEIGHT-20,
                         arcade.color.WHITE, 15, 20, 'right')

    def change_view(self, view: arcade.View) -> None:
        # keys = key.KeyStateHandler()
        # print(keys)
        arcade.pause(1)
        view.setup()
        self.window.show_view(view)

    def get_message(self, msg_name: str) -> str:
        messages = {
            "intro": "Your hive isn't doing well, and winter is approaching."
            "You need enough honey to survive the winter. "
            "You'll have to go get some more, but it won't be easy. "
            "You must leave and go on a dangerous journey to save your hive."
            "Be careful, the wasps are hungry too..."
        }
        return messages[msg_name]

    def print_messages(self):

        arcade.draw_text(self.get_message("intro"),
                         start_x=50, start_y=115, font_size=15,
                         font_name="arial", bold=True, multiline=True,
                         width=700, align="center", color=(250, 235, 215, ))

    def on_update(self, delta_time: float):
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
            self.reset_controls()  # ignore pressed controls between scenes
            outside_view = OutsideView1()
            self.change_view(outside_view)

        # Update all sprites
        for sprite_list in self.scene.sprite_lists:
            sprite_list.update()
        self.player.update_animation()
        self.physics_engine.update()


class HiveForeign(HiveView):
    def __init__(self):
        super().__init__()

        self.scene = arcade.Scene()
        # self.window.views["hive"] = HiveView()
        self.player = Player
        self.player = self.window.player  # save same player between views
        self.physics_engine = None
        self.sounds = {
            "hurt": arcade.load_sound("../assets/sounds/hurt.wav"),
            "honey": arcade.load_sound("../assets/sounds/honey.wav"),
            "background": arcade.load_sound(
                "../assets/sounds/background.wav", streaming=True),
            "jump": arcade.load_sound("../assets/sounds/jump.wav")
        }
        self.camera = arcade.Camera(self.window.width, self.window.height,
                                    self.window)

    def setup(self):
        """Sets up a hive scene"""

        print(f"Viewport: {arcade.get_viewport()}")

        self.exit_hole = EXIT_HOLE_YELLOW

        self.window.views["hive"] = self
        arcade.set_background_color(BACKGROUND_COLOR)
        self.background = arcade.load_texture(BACKGROUND_IMAGE)

        # Background Sound Track
        # arcade.play_sound(self.sounds["background"], looping=True)

        # Create sprite lists
        self.scene.add_sprite_list("Walls")  # , use_spatial_hash=True)
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
        exit_hole = arcade.Sprite(self.exit_hole,
                                  scale=1)
        self.sprite_random_pos(exit_hole, padding=100)
        self.scene.add_sprite("Exits", exit_hole)

        # Create and position player
        self.sprite_random_pos(self.player)
        self.scene.add_sprite("Player", self.player)

        # Create bees with random position and angle, then add to list
        for i in range(BEE_ENEMY_COUNT):
            bee = BeeEnemy(BEE_ENEMY_IMAGE, BEE_ENEMY_SCALING)
            self.sprite_random_pos(bee)
            bee.angle = random.randrange(0, 360)
            self.scene.add_sprite("Bees", bee)

        # Create honey drops with random position and angle, then add to list
        for i in range(HONEY_SPRITE_COUNT):
            honey = Honey(HONEY_SPRITE_IMAGE, HONEY_SPRITE_SCALING)
            self.sprite_random_pos(honey)
            self.scene.add_sprite("Honey", honey)

        # Set and apply physics engine
        # self.physics_engine = arcade.PhysicsEnginePlatformer(
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene.name_mapping["Walls"]
        )

    def on_draw(self):
        """Draws hive scene"""
        arcade.start_render()
        # arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, SCREEN_HEIGHT,
                                            self.background)
        self.camera.use()
        self.scene.draw()
        arcade.draw_text("Honey:" + str(self.player.score),
                         SCREEN_WIDTH-120, SCREEN_HEIGHT-20,
                         arcade.color.WHITE, 15, 20, 'right')

    def change_view(self, view: arcade.View) -> None:
        # keys = key.KeyStateHandler()
        # print(keys)
        arcade.pause(1)
        view.setup()
        self.window.show_view(view)

    def on_update(self, delta_time: float):
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

            print("Exiting level...")
            # Clear the window, and setup the next scene
            # self.window.clear(viewport=(0, 800, 0, 600))
            # self.window.close()
            # arcade.open_window(SCREEN_WIDTH, SCREEN_HEIGHT)
            outside_view = OutsideView2()
            self.change_view(outside_view)
            # outside_view.setup()
            # self.window.show_view(outside_view)

        # When player touches honey drop
        collision_list = arcade.check_for_collision_with_list(
                                self.player, self.scene.name_mapping["Honey"])
        if not self.player.flying:  # if player isn't flying
            for honey in collision_list:
                arcade.play_sound(self.sounds["honey"])
                honey.remove_from_sprite_lists()  # remove honey drop
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
        self.player.update_animation()
        self.physics_engine.update()


class OutsideView(arcade.View):
    def __init__(self):
        super().__init__()

        self.scene = arcade.Scene()
        self.player = Player(PLAYER_SPRITE_IMAGE, PLAYER_SPRITE_SCALING)
        self.player.score = self.window.player.score  # save score
        # self.player = self.window.player  # save same player between views
        self.camera = arcade.Camera(self.window.width, self.window.height)

    def setup(self):

        self.window.views["outside"] = self

        self.clear()
        self.scene_name = "outside"

        # Start timed functions (enemy attacks)
        self.timed_attacks()

        # Camera that scrolls the screen

        # Setup background image
        # arcade.set_background_color(BACKGROUND_COLOR)
        self.background = arcade.load_texture(
            OUTSIDE_IMAGE, width=800, height=OUTSIDE_HEIGHT)

        # Create sprite lists
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Wasps")

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Add sprites

        # Create and position player
        self.player.outside = True
        self.player.hurt = False
        self.player.flying = False
        self.player.walking = False
        self.player.position = (400, 300)
        self.player.angle = 0
        self.scene.add_sprite("Player", self.player)
        # self.player.hurt = False

        # setup camera auto scrolling
        self.camera_scroll_y = self.player.center_y - self.window.height / 2

        # Place walls
        self.place_borders()

        # Set and apply physics engine
        # self.physics_engine = arcade.PhysicsEnginePlatformer(
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene.name_mapping["Walls"]
        )

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

    def timed_attacks(self) -> None:
        arcade.schedule(self.wasp_attack, WASP_ATTACK_INTERVAL)

    def wasp_attack(self, *args) -> None:
        """
        Generates wasp directly above player that will move directly toward
        the player (i.e. downwards from screen top) at a semi-random velocity
        """
        print("wasp attack!")  # for debugging
        (player_x, player_y) = self.player.position

        # Randomly choose direction to attack from
        direction = random.choice(["left", "right", "up", "down"])
        if direction == "up":
            wasp = Wasp(angle=180, position=(player_x, player_y+700))
            wasp.change_y = -1 * random.randint(WASP_SPEED_MIN, WASP_SPEED_MAX)
        elif direction == "down":
            wasp = Wasp(angle=0, position=(player_x, player_y-700))
            wasp.change_y = random.randint(WASP_SPEED_MIN, WASP_SPEED_MAX)
        elif direction == "right":
            wasp = Wasp(angle=90, position=(player_x+700, player_y))
            wasp.change_x = -1 * random.randint(WASP_SPEED_MIN, WASP_SPEED_MAX)
        elif direction == "left":
            wasp = Wasp(angle=270, position=(player_x-700, player_y))
            wasp.change_x = random.randint(WASP_SPEED_MIN, WASP_SPEED_MAX)
        self.scene.add_sprite("Wasps", wasp)

        # Randomly add additional simultaneous, parallel attackers
        if random.choice([1, 3]) == 3:
            if wasp.angle == 180:  # if attacking from up direction
                wasp2 = Wasp(angle=wasp.angle, change_y=wasp.change_y,
                             position=(wasp.center_x-WASP_SPACING,
                                       wasp.center_y))
                wasp3 = Wasp(angle=wasp.angle, change_y=wasp.change_y,
                             position=(wasp.center_x+WASP_SPACING,
                                       wasp.center_y))
            elif wasp.angle == 0:  # if attacking from up direction
                wasp2 = Wasp(angle=wasp.angle, change_y=wasp.change_y,
                             position=(wasp.center_x-WASP_SPACING,
                                       wasp.center_y))
                wasp3 = Wasp(angle=wasp.angle, change_y=wasp.change_y,
                             position=(wasp.center_x+WASP_SPACING,
                                       wasp.center_y))
            elif wasp.angle == 90:  # if attacking from up direction
                wasp2 = Wasp(angle=wasp.angle, change_x=wasp.change_x,
                             position=(wasp.center_x,
                                       wasp.center_y-WASP_SPACING))
                wasp3 = Wasp(angle=wasp.angle, change_x=wasp.change_x,
                             position=(wasp.center_x,
                                       wasp.center_y+WASP_SPACING))
            elif wasp.angle == 270:  # if attacking from up direction
                wasp2 = Wasp(angle=wasp.angle, change_x=wasp.change_x,
                             position=(wasp.center_x,
                                       wasp.center_y-WASP_SPACING))
                wasp3 = Wasp(angle=wasp.angle, change_x=wasp.change_x,
                             position=(wasp.center_x,
                                       wasp.center_y+WASP_SPACING))

            self.scene.add_sprite("Wasps", wasp2)
            self.scene.add_sprite("Wasps", wasp3)
        print(f"Attacking wasp speed: {wasp.change_y}")

    def place_borders(self):
        # Create invisible border around scene

        vertical_pos = [[0, OUTSIDE_HEIGHT / 2],
                        [SCREEN_WIDTH, OUTSIDE_HEIGHT / 2]]
        horizontal_pos = [[SCREEN_WIDTH / 2, 0 - 10],
                          [SCREEN_WIDTH / 2, SCREEN_HEIGHT - 10]]
        # horizontal walls move a little out of place when
        # first camera scrolling. subtract 10 pixels to compensate

        for pos in vertical_pos:
            wall = Wall(WALL_SPRITE_IMAGE, position=pos, kind="vertical",
                        height=OUTSIDE_HEIGHT, width=2)
            self.scene.add_sprite("Walls", wall)

        for pos in horizontal_pos:
            wall = Wall(WALL_SPRITE_IMAGE, position=pos, kind="horizontal",
                        height=2, width=SCREEN_WIDTH)
            self.scene.add_sprite("Walls", wall)

    def scroll_to_player(self):
        """scroll window to player position"""

        # x is 0 because the camera only moves (scrolls) vertically on y axis
        position = Vec2(0, self.player.center_y - self.height / 2)
        self.camera.move_to(position, CAMERA_SPEED)

    def change_view(self, view: arcade.View) -> None:

        arcade.unschedule(self.wasp_attack)
        arcade.pause(1)
        view.setup()
        self.window.show_view(view)

    def camera_auto_scroll(self):
        """Auto scroll camera vertically"""
        position = Vec2(0, self.camera_scroll_y)
        if self.camera_scroll_y >= SCREEN_HEIGHT:
            # if self.camera_scroll_y >= OUTSIDE_HEIGHT - SCREEN_HEIGHT:
            Hive_View = HiveView()
            self.change_view(Hive_View)
        self.camera_scroll_y += CAMERA_SPEED
        self.camera.move_to(position, CAMERA_SPEED / 2)

    def on_draw(self):
        """Draws outside scene"""
        arcade.start_render()
        # arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            SCREEN_WIDTH, OUTSIDE_HEIGHT,
                                            self.background)

        self.camera.use()
        self.scene.draw()
        text_x = SCREEN_WIDTH - 120
        text_y = SCREEN_HEIGHT - 30 + self.camera_scroll_y
        arcade.draw_text("Honey:" + str(self.player.score),
                         text_x, text_y,
                         arcade.color.WHITE, 15, 20, 'right')

    def on_key_press(self, key: int, modifiers: int):

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

    def on_key_release(self, key: int, modifiers: int):

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
                "../assets/sprites/bee_player_move1_2.png")
        self.player.walking = False

    def update_player_speed(self):

        # Calculate speed based on the keys pressed
        self.player.change_x = 0
        self.player.change_y = 0

        # Movement speed * 2 compared to hive speed
        move_speed_mod = 1.5
        if self.up_pressed and not any([self.down_pressed,
                                        self.left_pressed,
                                        self.right_pressed]):
            self.player.change_y = PLAYER_MOVE_SPEED * move_speed_mod
        elif self.down_pressed and not any([self.up_pressed,
                                            self.left_pressed,
                                            self.right_pressed]):
            self.player.change_y = -PLAYER_MOVE_SPEED * move_speed_mod
        if self.left_pressed and not any([self.up_pressed,
                                          self.down_pressed,
                                          self.right_pressed]):
            self.player.change_x = -PLAYER_MOVE_SPEED * move_speed_mod
        elif self.right_pressed and not any([self.up_pressed,
                                            self.down_pressed,
                                            self.left_pressed]):
            self.player.change_x = PLAYER_MOVE_SPEED * move_speed_mod

    def on_update(self, delta_time: float):

        # Move invisible borders along with camera
        for wall in self.scene.name_mapping["Walls"]:
            wall.center_y += CAMERA_SPEED

        for wasp in self.scene.name_mapping["Wasps"]:
            wasp.update_animation()

        # When player touches a WASP, decrement score
        # if player isn't already being "hurt" by wasp
        if arcade.check_for_collision_with_list(
                self.player, self.scene.name_mapping["Wasps"]):
            if not self.player.hurt and not self.player.flying:
                self.player.hurt = True
                # arcade.play_sound(self.sounds["hurt"])
                if self.player.score > 0:  # score can't be negative
                    self.player.score -= 1
        else:  # if we aren't being hurt by a bee
            self.player.hurt = False

        self.player.update_animation()

        # Update all sprites
        for sprite_list in self.scene.sprite_lists:
            sprite_list.update()

        self.physics_engine.update()

        self.camera_auto_scroll()


class OutsideView1(OutsideView):
    def __init__(self):
        super().__init__()

    def setup(self):

        print(f"Viewport: {arcade.get_viewport()}")

        self.window.views["outside"] = self

        self.clear()
        self.scene_name = "outside"

        # Start timed functions (enemy attacks)
        self.timed_attacks()

        # Camera that scrolls the screen

        # Setup background image
        # arcade.set_background_color(BACKGROUND_COLOR)
        self.background = arcade.load_texture(
            OUTSIDE_IMAGE, width=800, height=OUTSIDE_HEIGHT)

        # Create sprite lists
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Wasps")

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Add sprites

        # Create and position player
        self.player.outside = True
        self.player.hurt = False
        self.player.flying = False
        self.player.walking = False
        self.player.position = (400, 300)
        self.player.angle = 0
        self.scene.add_sprite("Player", self.player)
        # self.player.hurt = False

        # setup camera auto scrolling
        self.camera_scroll_y = self.player.center_y - self.window.height / 2

        # Place walls
        self.place_borders()

        # Set and apply physics engine
        # self.physics_engine = arcade.PhysicsEnginePlatformer(
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene.name_mapping["Walls"]
        )

    def camera_auto_scroll(self):
        """Auto scroll camera vertically"""
        position = Vec2(0, self.camera_scroll_y)
        if self.camera_scroll_y >= SCREEN_HEIGHT:
            # if self.camera_scroll_y >= OUTSIDE_HEIGHT - SCREEN_HEIGHT:
            Hive_View = HiveForeign()
            self.change_view(Hive_View)
        self.camera_scroll_y += CAMERA_SPEED
        self.camera.move_to(position, CAMERA_SPEED / 2)


class OutsideView2(OutsideView):
    def __init__(self):
        super().__init__()

    def setup(self):

        print(f"Viewport: {arcade.get_viewport()}")

        self.window.views["outside"] = self

        self.clear()
        self.scene_name = "outside"

        # Start timed functions (enemy attacks)
        self.timed_attacks()

        # Camera that scrolls the screen

        # Setup background image
        # arcade.set_background_color(BACKGROUND_COLOR)
        self.background = arcade.load_texture(
            OUTSIDE_FLIPPED, width=800, height=OUTSIDE_HEIGHT)

        # Create sprite lists
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Wasps")

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Add sprites

        # Create and position player
        self.player.outside = True
        self.player.hurt = False
        self.player.flying = False
        self.player.walking = False
        self.player.position = (400, 300)
        self.player.angle = 0
        self.scene.add_sprite("Player", self.player)
        # self.player.hurt = False

        # setup camera auto scrolling
        self.camera_scroll_y = self.player.center_y - self.window.height / 2

        # Place walls
        self.place_borders()

        # Set and apply physics engine
        # self.physics_engine = arcade.PhysicsEnginePlatformer(
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene.name_mapping["Walls"]
        )

    def camera_auto_scroll(self):
        """Auto scroll camera vertically"""
        position = Vec2(0, self.camera_scroll_y)
        if self.camera_scroll_y >= SCREEN_HEIGHT:
            # if self.camera_scroll_y >= OUTSIDE_HEIGHT - SCREEN_HEIGHT:
            Home_View = HiveHome()
            self.change_view(Home_View)
        self.camera_scroll_y += CAMERA_SPEED
        self.camera.move_to(position, CAMERA_SPEED / 2)


class Player(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)

        self.score = 0
        self.texture_index = 0  # tracks current texture
        self.walking = False  # whether player is walking
        self.frame = 0  # tracks frames for animations
        self.flying = False
        self.hurt = False
        self.outside = False

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

        # Outside flying (scroll view) animation textures
        self.outside_textures = []
        self.outside_texture_paths = [
            "../assets/sprites/player_outside1.png",
            "../assets/sprites/player_outside2.png"
        ]
        for filepath in self.outside_texture_paths:
            self.outside_textures.append(arcade.load_texture(filepath))

    def load_animations(self, file_list: list):
        pass

    def update_animation(self) -> None:

        # player animation
        if self.hurt:
            if self.frame % (20 // ANIMATION_SPEED) == 0:
                self.texture = self.hurt_textures[self.texture_index]
                self.texture_index = (self.texture_index + 1)\
                    % len(self.hurt_textures)
        elif self.flying:
            if self.frame % (20 // ANIMATION_SPEED) == 0:
                self.texture = self.flying_textures[self.texture_index]
                self.texture_index = (self.texture_index + 1)\
                    % len(self.flying_textures)
        elif self.walking:
            if self.frame % (20 // ANIMATION_SPEED) == 0:
                self.texture = self.walking_textures[self.texture_index]
                self.texture_index = (self.texture_index + 1)\
                    % len(self.walking_textures)
        elif self.outside:
            if self.frame % (20 // ANIMATION_SPEED) == 0:
                self.texture = self.outside_textures[self.texture_index]
                self.texture_index = (self.texture_index + 1)\
                    % len(self.outside_textures)

        self.frame += 1


class Wall(arcade.Sprite):
    def __init__(self, sprite, position, kind,
                 height=SCREEN_HEIGHT, width=SCREEN_WIDTH, alpha=0, scaling=1):
        super().__init__(sprite, scaling)

        self.position = position
        self.alpha = alpha
        self.scaling = scaling
        self.height = height
        self.width = width
        self.kind = kind


class BeeEnemy(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)


class BeeFriend(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)


class Wasp(arcade.Sprite):
    def __init__(self, sprite=WASP_IMAGE, scaling=WASP_SCALING,
                 change_y=0, change_x=0, position=(0, 0), angle=0):
        super().__init__(sprite, scaling)

        self.change_y = change_y
        self.change_x = change_x
        self.position = position
        self.angle = angle
        self.frame = 0  # tracks frames for animations
        self.texture_index = 0  # tracks current texture

        # Setup and load flying animation textures
        self.flying_textures = []
        self.flying_texture_paths = [
            "../assets/sprites/wasp_flying1.png",
            "../assets/sprites/wasp_flying2.png"
        ]
        for filepath in self.flying_texture_paths:
            self.flying_textures.append(arcade.load_texture(filepath))

    def update_animation(self) -> None:

        # wasp animation
        if self.frame % (20 // ANIMATION_SPEED) == 0:
            self.texture = self.flying_textures[self.texture_index]
            self.texture_index = (self.texture_index + 1)\
                % len(self.flying_textures)

        self.frame += 1


class Honey(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)


# ################# DRIVER CODE #######################

def main():
    window = Window(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE)
    # window.center_window()
    home_view = HiveHome()
    home_view.setup()
    window.show_view(home_view)
    arcade.run()


if __name__ == "__main__":
    main()

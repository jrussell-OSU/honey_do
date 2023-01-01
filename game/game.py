# Author: Jacob Russell
# Date: 12-07-2022
# Descrption: "Honey Do" is a game that I made
# for my hot wife where you are a little bee

# Reference: relies on docs and examples from https://api.arcade.academy/

# TODO list:
# Add time limit to flights
# random color honeycomb background and bees for each new hive
# GUI
# tongue sticks out when collecting honey
# make screen dimmer inside hive?


import arcade
import random
from pyglet.math import Vec2
from sprites import Player, Wall, Wasp, BeeEnemy, BeeFriend, Honey
import constants as c
from info_bar import InfoBar


# ################### CLASSES / METHODS ##################

class Window(arcade.Window):
    """
    The window in which all the views are displayed
    """
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # will hold different screen views
        # (e.g., menu view, hivelevel view, outsidelevel view)
        # useful so different views have different controls etc.
        self.views = {}

        self.sections = {}
        self.current_section: arcade.Section = None

        # only keyboard commands allowed
        # self.set_exclusive_keyboard(exclusive=True)

        self.player = Player(c.PLAYER_SPRITE_IMAGE, c.PLAYER_SPRITE_SCALING)

    def get_player(self):
        return self.player


class HomeView(arcade.View):
    def __init__(self):
        super().__init__()

        self.bottom_section = InfoBar(0, 0, c.SCREEN_WIDTH,
                                      c.INFO_BAR_HEIGHT,
                                      accept_keyboard_events=False
                                      )
        self.home_section = HomeSection(0, c.INFO_BAR_HEIGHT,
                                        c.SCREEN_WIDTH, c.MAIN_VIEW_HEIGHT)

        self.section_manager.add_section(self.home_section)
        self.section_manager.add_section(self.bottom_section)

    def on_draw(self):
        arcade.start_render()


class HiveSection(arcade.Section):

    def __init__(self, left: int, bottom: int, width: int, height: int,
                 **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

    def sprite_random_pos(self, sprite: arcade.Sprite,
                          padding: int = c.PADDING) -> None:
        """Move sprite to a random position (until no collisions detected)."""
        sprite.center_x = random.randint(padding,
                                         (c.SCREEN_WIDTH - padding))
        sprite.center_y = random.randint(padding + c.INFO_BAR_HEIGHT,
                                         (c.SCREEN_HEIGHT - padding))
        while arcade.check_for_collision_with_lists(sprite,
                                                    self.scene.sprite_lists):
            sprite.center_x = random.randint(padding,
                                             (c.SCREEN_WIDTH - padding))
            sprite.center_y = random.randint(padding + c.INFO_BAR_HEIGHT,
                                             (c.SCREEN_HEIGHT - padding))

    def change_view(self, view: arcade.View) -> None:
        # keys = key.KeyStateHandler()
        # print(keys)
        arcade.pause(1)
        self.window.show_view(view)

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

    def edge_check(self, sprite: Player):
        """Prevent (player) sprite going past screen edge"""
        if sprite.center_x > (c.MAIN_VIEW_WIDTH - sprite.radius):
            sprite.center_x = (c.MAIN_VIEW_WIDTH - sprite.radius)
        if sprite.center_x < (0 + sprite.radius):
            sprite.center_x = (0 + sprite.radius)
        if sprite.center_y < (c.INFO_BAR_HEIGHT + sprite.radius):
            sprite.center_y = (c.INFO_BAR_HEIGHT + sprite.radius)
        if sprite.center_y > (c.SCREEN_HEIGHT - sprite.radius):
            sprite.center_y = (c.SCREEN_HEIGHT - sprite.radius)


class HomeSection(HiveSection):
    """
    Section of player's home (friendly) hive.
    """
    def __init__(self, left: int, bottom: int, width: int, height: int,
                 **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        self.exit_hole = c.EXIT_HOLE_PINK
        self.scene = arcade.Scene()
        self.scene_over = False  # whether done with this scene (trigger)
        # self.window.views["hive"] = HiveView()
        self.player: Player = self.window.player  # save same player b/t views
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

        self.setup()

    def setup(self):
        """Sets up a hive scene"""

        print(f"Viewport: {arcade.get_viewport()}")
        # self.camera.move_to()

        self.window.views["home"] = self
        arcade.set_background_color(c.BACKGROUND_COLOR)
        self.background = arcade.load_texture(c.HOME_BACKGROUND)

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

        # Create and place exit hole
        exit_hole = arcade.Sprite(self.exit_hole,
                                  scale=1)
        self.sprite_random_pos(exit_hole, padding=100)
        self.scene.add_sprite("Exits", exit_hole)

        # Create and position player
        self.sprite_random_pos(self.player)
        self.scene.add_sprite("Player", self.player)

        # Create bees with random position and angle, then add to list
        for i in range(c.BEE_FRIEND_COUNT):
            bee = BeeFriend(c.BEE_FRIEND_IMAGE, c.BEE_FRIEND_SCALING)
            self.sprite_random_pos(bee)
            bee.angle = random.randrange(0, 360)
            self.scene.add_sprite("Bees", bee)

        # Set and apply physics engine
        # self.physics_engine = arcade.PhysicsEnginePlatformer(
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene.name_mapping["Walls"]
        )

    def on_draw(self):
        """Draws hive scene"""
        arcade.start_render()
        # arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0,
                                            c.SCREEN_HEIGHT-c.MAIN_VIEW_HEIGHT,
                                            c.MAIN_VIEW_WIDTH,
                                            c.MAIN_VIEW_HEIGHT,
                                            self.background)
        self.camera.use()
        self.scene.draw()
        # self.print_messages()
        arcade.draw_text("Honey:" + str(self.player.score),
                         c.SCREEN_WIDTH-120, c.SCREEN_HEIGHT-20,
                         arcade.color.WHITE, 15, 20, 'right')

    def update_player_speed(self):

        # Calculate speed based on the keys pressed
        self.player.change_x = 0
        self.player.change_y = 0

        if self.up_pressed and not any([self.down_pressed,
                                        self.left_pressed,
                                        self.right_pressed]):
            self.player.change_y = c.PLAYER_MOVE_SPEED
            self.player.angle = 0
            self.player.walking = True
        elif self.down_pressed and not any([self.up_pressed,
                                            self.left_pressed,
                                            self.right_pressed]):
            self.player.change_y = -c.PLAYER_MOVE_SPEED
            self.player.angle = 180
            self.player.walking = True
        if self.left_pressed and not any([self.up_pressed,
                                          self.down_pressed,
                                          self.right_pressed]):
            self.player.change_x = -c.PLAYER_MOVE_SPEED
            self.player.angle = 90
            self.player.walking = True
        elif self.right_pressed and not any([self.up_pressed,
                                            self.down_pressed,
                                            self.left_pressed]):
            self.player.change_x = c.PLAYER_MOVE_SPEED
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
            self.reset_controls()  # ignore pressed controls between scenes
            outside_view = OutsideView("OutsideView1")
            self.change_view(outside_view)

        # Update all sprites
        for sprite_list in self.scene.sprite_lists:
            sprite_list.update()
        self.player.update_animation()
        self.physics_engine.update()

        # Prevent player from going past screen edge
        self.edge_check(self.player)


class OutsideView(arcade.View):
    """
    Top-down, scrolling level that takes place outside, in the air.
    """
    def __init__(self, level: str):
        super().__init__()

        self.bottom_section = InfoBar(0, 0, c.SCREEN_WIDTH,
                                      c.INFO_BAR_HEIGHT,
                                      accept_keyboard_events=False,
                                      )

        if level == "OutsideView1":
            self.outside_section = OutsideLeave(0, c.INFO_BAR_HEIGHT,
                                                   c.SCREEN_WIDTH,
                                                   c.MAIN_VIEW_HEIGHT)
            self.section_manager.add_section(self.outside_section)
            self.section_manager.add_section(self.bottom_section)
        elif level == "OutsideView2":
            self.outside_section = OutsideReturn(0, c.INFO_BAR_HEIGHT,
                                                   c.SCREEN_WIDTH,
                                                   c.MAIN_VIEW_HEIGHT)
            self.section_manager.add_section(self.outside_section)
            self.section_manager.add_section(self.bottom_section)

    def on_draw(self):
        arcade.start_render()


class OutsideSection(arcade.Section):
    def __init__(self, left: int, bottom: int, width: int, height: int,
                 **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        self.camera_scroll_y = 0

    def sprite_random_pos(self, sprite, padding=c.PADDING):
        """Move sprite to a random position (until no collisions detected)."""
        sprite.center_x = random.randint(padding,
                                         (c.SCREEN_WIDTH - padding))
        sprite.center_y = random.randint(padding,
                                         (c.SCREEN_HEIGHT - padding))
        while arcade.check_for_collision_with_lists(sprite,
                                                    self.scene.sprite_lists):
            sprite.center_x = random.randint(padding,
                                             (c.SCREEN_WIDTH - padding))
            sprite.center_y = random.randint(padding,
                                             (c.SCREEN_HEIGHT - padding))

    def scroll_to_player(self):
        """scroll window to player position"""

        # x is 0 because the camera only moves (scrolls) vertically on y axis
        position = Vec2(0, self.player.center_y - self.height / 2)
        self.camera.move_to(position, c.CAMERA_SPEED)

    def change_view(self, view: arcade.View) -> None:

        arcade.pause(1)
        self.window.show_view(view)

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
            self.player.change_y = c.PLAYER_MOVE_SPEED * move_speed_mod
        elif self.down_pressed and not any([self.up_pressed,
                                            self.left_pressed,
                                            self.right_pressed]):
            self.player.change_y = -c.PLAYER_MOVE_SPEED * move_speed_mod
        if self.left_pressed and not any([self.up_pressed,
                                          self.down_pressed,
                                          self.right_pressed]):
            self.player.change_x = -c.PLAYER_MOVE_SPEED * move_speed_mod
        elif self.right_pressed and not any([self.up_pressed,
                                            self.down_pressed,
                                            self.left_pressed]):
            self.player.change_x = c.PLAYER_MOVE_SPEED * move_speed_mod

    def edge_check(self, sprite: Player):
        """Prevent (player) sprite going past screen edge"""
        if sprite.center_x > (c.MAIN_VIEW_WIDTH - sprite.radius):
            sprite.center_x = (c.MAIN_VIEW_WIDTH - sprite.radius)
        if sprite.center_x < (0 + sprite.radius):
            sprite.center_x = (0 + sprite.radius)
        if sprite.center_y < (c.INFO_BAR_HEIGHT + sprite.radius +
                              self.camera_scroll_y + c.CAMERA_SPEED):
            sprite.center_y = (c.INFO_BAR_HEIGHT + sprite.radius +
                               self.camera_scroll_y + c.CAMERA_SPEED)
        if sprite.center_y > (c.SCREEN_HEIGHT - sprite.radius +
                              self.camera_scroll_y + c.CAMERA_SPEED):
            sprite.center_y = (c.SCREEN_HEIGHT - sprite.radius +
                               self.camera_scroll_y + c.CAMERA_SPEED)


class OutsideLeave(OutsideSection):
    """
    View of outside, top-scrolling. Leaving home, heading to foreign hive.
    """
    def __init__(self, left: int, bottom: int, width: int, height: int,
                 **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        self.scene = arcade.Scene()
        self.player = Player(c.PLAYER_SPRITE_IMAGE, c.PLAYER_SPRITE_SCALING)
        self.player.score = self.window.player.score
        self.camera = arcade.Camera(self.window.width, self.window.height)

        self.setup()

    def setup(self):

        print(f"Viewport: {arcade.get_viewport()}")

        self.window.views["outside"] = self

        self.scene_name = "outside"

        # Start timed functions (enemy attacks)
        self.timed_attacks()

        # Setup background image
        self.background = arcade.load_texture(
            c.OUTSIDE_IMAGE, width=800, height=c.OUTSIDE_HEIGHT)

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

        # Set and apply physics engine
        # self.physics_engine = arcade.PhysicsEnginePlatformer(
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene.name_mapping["Walls"]
        )

    def timed_attacks(self) -> None:
        arcade.schedule(self.wasp_attack, c.WASP_ATTACK_INTERVAL)

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
            wasp.change_y = -1 * random.randint(c.WASP_SPEED_MIN,
                                                c.WASP_SPEED_MAX)
        elif direction == "down":
            wasp = Wasp(angle=0, position=(player_x, player_y-700))
            wasp.change_y = random.randint(c.WASP_SPEED_MIN, c.WASP_SPEED_MAX)
        elif direction == "right":
            wasp = Wasp(angle=90, position=(player_x+700, player_y))
            wasp.change_x = -1 * random.randint(c.WASP_SPEED_MIN,
                                                c.WASP_SPEED_MAX)
        elif direction == "left":
            wasp = Wasp(angle=270, position=(player_x-700, player_y))
            wasp.change_x = random.randint(c.WASP_SPEED_MIN, c.WASP_SPEED_MAX)
        self.scene.add_sprite("Wasps", wasp)

        # Randomly add additional simultaneous, parallel attackers
        if random.choice([1, 3]) == 3:
            if wasp.angle == 180:  # if attacking from up direction
                wasp2 = Wasp(angle=wasp.angle, change_y=wasp.change_y,
                             position=(wasp.center_x-c.WASP_SPACING,
                                       wasp.center_y))
                wasp3 = Wasp(angle=wasp.angle, change_y=wasp.change_y,
                             position=(wasp.center_x+c.WASP_SPACING,
                                       wasp.center_y))
            elif wasp.angle == 0:  # if attacking from up direction
                wasp2 = Wasp(angle=wasp.angle, change_y=wasp.change_y,
                             position=(wasp.center_x-c.WASP_SPACING,
                                       wasp.center_y))
                wasp3 = Wasp(angle=wasp.angle, change_y=wasp.change_y,
                             position=(wasp.center_x+c.WASP_SPACING,
                                       wasp.center_y))
            elif wasp.angle == 90:  # if attacking from up direction
                wasp2 = Wasp(angle=wasp.angle, change_x=wasp.change_x,
                             position=(wasp.center_x,
                                       wasp.center_y-c.WASP_SPACING))
                wasp3 = Wasp(angle=wasp.angle, change_x=wasp.change_x,
                             position=(wasp.center_x,
                                       wasp.center_y+c.WASP_SPACING))
            elif wasp.angle == 270:  # if attacking from up direction
                wasp2 = Wasp(angle=wasp.angle, change_x=wasp.change_x,
                             position=(wasp.center_x,
                                       wasp.center_y-c.WASP_SPACING))
                wasp3 = Wasp(angle=wasp.angle, change_x=wasp.change_x,
                             position=(wasp.center_x,
                                       wasp.center_y+c.WASP_SPACING))

            self.scene.add_sprite("Wasps", wasp2)
            self.scene.add_sprite("Wasps", wasp3)
        print(f"Attacking wasp speed: {wasp.change_y}")

    def camera_auto_scroll(self):
        """Auto scroll camera vertically"""
        position = Vec2(0, self.camera_scroll_y)
        if self.camera_scroll_y >= c.SCREEN_HEIGHT:
            # if self.camera_scroll_y >= c.OUTSIDE_HEIGHT - c.SCREEN_HEIGHT:
            Hive_View = HiveView()
            self.change_view(Hive_View)
        self.camera_scroll_y += c.CAMERA_SPEED
        self.camera.move_to(position, c.CAMERA_SPEED / 2)

    def on_draw(self):
        """Draws outside scene"""
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0,
                                            c.SCREEN_HEIGHT-c.MAIN_VIEW_HEIGHT,
                                            c.MAIN_VIEW_WIDTH,
                                            c.OUTSIDE_HEIGHT,
                                            self.background)
        self.camera.use()
        self.scene.draw()
        text_x = c.SCREEN_WIDTH - 120
        text_y = c.SCREEN_HEIGHT - 30 + self.camera_scroll_y
        arcade.draw_text("Honey:" + str(self.player.score),
                         text_x, text_y,
                         arcade.color.WHITE, 15, 20, 'right')

    def on_update(self, delta_time: float):

        # Move invisible borders along with camera
        for wall in self.scene.name_mapping["Walls"]:
            wall.center_y += c.CAMERA_SPEED

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

        self.edge_check(self.player)


class HiveView(arcade.View):
    def __init__(self):
        super().__init__()

        self.bottom_section = InfoBar(0, 0, c.SCREEN_WIDTH,
                                      c.INFO_BAR_HEIGHT,
                                      accept_keyboard_events=False,
                                      prevent_dispatch={False}
                                      )
        self.hive_section = ForeignHiveSection(0, c.INFO_BAR_HEIGHT,
                                               c.SCREEN_WIDTH,
                                               c.MAIN_VIEW_HEIGHT)

        self.section_manager.add_section(self.hive_section)
        self.section_manager.add_section(self.bottom_section)

    def on_draw(self):
        arcade.start_render()


class ForeignHiveSection(HiveSection):
    """
    View of a foreign (hostile) bee hive.
    """
    def __init__(self, left: int, bottom: int, width: int, height: int,
                 **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

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

        self.setup()

    def setup(self):
        """Sets up a hive scene"""

        print(f"Viewport: {arcade.get_viewport()}")

        self.exit_hole = c.EXIT_HOLE_YELLOW

        self.window.views["hive"] = self
        arcade.set_background_color(c.BACKGROUND_COLOR)
        self.background = arcade.load_texture(c.BACKGROUND_IMAGE)

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

        # Create and place exit hole
        exit_hole = arcade.Sprite(self.exit_hole,
                                  scale=1)
        self.sprite_random_pos(exit_hole, padding=100)
        self.scene.add_sprite("Exits", exit_hole)

        # Create and position player
        self.sprite_random_pos(self.player)
        self.scene.add_sprite("Player", self.player)

        # Create bees with random position and angle, then add to list
        for i in range(c.BEE_ENEMY_COUNT):
            bee = BeeEnemy(c.BEE_ENEMY_IMAGE, c.BEE_ENEMY_SCALING)
            self.sprite_random_pos(bee)
            bee.angle = random.randrange(0, 360)
            self.scene.add_sprite("Bees", bee)

        # Create honey drops with random position and angle, then add to list
        for i in range(c.HONEY_SPRITE_COUNT):
            honey = Honey(c.HONEY_SPRITE_IMAGE, c.HONEY_SPRITE_SCALING)
            self.sprite_random_pos(honey)
            self.scene.add_sprite("Honey", honey)

        # Set and apply physics engine
        # self.physics_engine = arcade.PhysicsEnginePlatformer(
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene.name_mapping["Walls"]
        )

    def sprite_random_pos(self, sprite: arcade.Sprite,
                          padding: int = c.PADDING) -> None:
        """Move sprite to a random position (until no collisions detected)."""
        sprite.center_x = random.randint(padding,
                                         (c.SCREEN_WIDTH - padding))
        sprite.center_y = random.randint(padding + c.INFO_BAR_HEIGHT,
                                         (c.SCREEN_HEIGHT - padding))
        while arcade.check_for_collision_with_lists(sprite,
                                                    self.scene.sprite_lists):
            sprite.center_x = random.randint(padding + c.INFO_BAR_HEIGHT,
                                             (c.SCREEN_WIDTH - padding))
            sprite.center_y = random.randint(padding,
                                             (c.SCREEN_HEIGHT - padding))

    def on_draw(self):
        """Draws hive scene"""
        arcade.start_render()
        # arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0,
                                            c.SCREEN_HEIGHT-c.MAIN_VIEW_HEIGHT,
                                            c.MAIN_VIEW_WIDTH,
                                            c.MAIN_VIEW_HEIGHT,
                                            self.background)
        self.camera.use()
        self.scene.draw()
        arcade.draw_text("Honey:" + str(self.player.score),
                         c.SCREEN_WIDTH-120, c.SCREEN_HEIGHT-20,
                         arcade.color.WHITE, 15, 20, 'right')

    def change_view(self, view: arcade.View) -> None:
        # keys = key.KeyStateHandler()
        # print(keys)
        arcade.pause(1)
        self.window.show_view(view)

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
            self.player.change_y = c.PLAYER_MOVE_SPEED
            self.player.angle = 0
            self.player.walking = True
        elif self.down_pressed and not any([self.up_pressed,
                                            self.left_pressed,
                                            self.right_pressed]):
            self.player.change_y = -c.PLAYER_MOVE_SPEED
            self.player.angle = 180
            self.player.walking = True
        if self.left_pressed and not any([self.up_pressed,
                                          self.down_pressed,
                                          self.right_pressed]):
            self.player.change_x = -c.PLAYER_MOVE_SPEED
            self.player.angle = 90
            self.player.walking = True
        elif self.right_pressed and not any([self.up_pressed,
                                            self.down_pressed,
                                            self.left_pressed]):
            self.player.change_x = c.PLAYER_MOVE_SPEED
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
            # arcade.open_window(c.SCREEN_WIDTH, c.SCREEN_HEIGHT)
            outside_view = OutsideView("OutsideView2")
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

        self.edge_check(self.player)


class OutsideReturn(OutsideSection):
    """
    View of outside, top-scrolling. Heading toward home.
    """
    def __init__(self, left: int, bottom: int, width: int, height: int,
                 **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

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

        self.setup()

    def setup(self):

        print(f"Viewport: {arcade.get_viewport()}")

        self.window.views["outside"] = self

        self.scene_name = "outside"

        # Start timed functions (enemy attacks)
        self.timed_attacks()

        # Camera that scrolls the screen

        # Setup background image
        # arcade.set_background_color(c.BACKGROUND_COLOR)
        self.background = arcade.load_texture(
            c.OUTSIDE_FLIPPED, width=800, height=c.OUTSIDE_HEIGHT)

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

        # Set and apply physics engine
        # self.physics_engine = arcade.PhysicsEnginePlatformer(
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene.name_mapping["Walls"]
        )

    def timed_attacks(self) -> None:
        arcade.schedule(self.wasp_attack, c.WASP_ATTACK_INTERVAL)

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
            wasp.change_y = -1 * random.randint(c.WASP_SPEED_MIN,
                                                c.WASP_SPEED_MAX)
        elif direction == "down":
            wasp = Wasp(angle=0, position=(player_x, player_y-700))
            wasp.change_y = random.randint(c.WASP_SPEED_MIN,
                                           c.WASP_SPEED_MAX)
        elif direction == "right":
            wasp = Wasp(angle=90, position=(player_x+700, player_y))
            wasp.change_x = -1 * random.randint(c.WASP_SPEED_MIN,
                                                c.WASP_SPEED_MAX)
        elif direction == "left":
            wasp = Wasp(angle=270, position=(player_x-700, player_y))
            wasp.change_x = random.randint(c.WASP_SPEED_MIN,
                                           c.WASP_SPEED_MAX)
        self.scene.add_sprite("Wasps", wasp)

        # Randomly add additional simultaneous, parallel attackers
        if random.choice([1, 3]) == 3:
            if wasp.angle == 180:  # if attacking from up direction
                wasp2 = Wasp(angle=wasp.angle, change_y=wasp.change_y,
                             position=(wasp.center_x-c.WASP_SPACING,
                                       wasp.center_y))
                wasp3 = Wasp(angle=wasp.angle, change_y=wasp.change_y,
                             position=(wasp.center_x+c.WASP_SPACING,
                                       wasp.center_y))
            elif wasp.angle == 0:  # if attacking from up direction
                wasp2 = Wasp(angle=wasp.angle, change_y=wasp.change_y,
                             position=(wasp.center_x-c.WASP_SPACING,
                                       wasp.center_y))
                wasp3 = Wasp(angle=wasp.angle, change_y=wasp.change_y,
                             position=(wasp.center_x+c.WASP_SPACING,
                                       wasp.center_y))
            elif wasp.angle == 90:  # if attacking from up direction
                wasp2 = Wasp(angle=wasp.angle, change_x=wasp.change_x,
                             position=(wasp.center_x,
                                       wasp.center_y-c.WASP_SPACING))
                wasp3 = Wasp(angle=wasp.angle, change_x=wasp.change_x,
                             position=(wasp.center_x,
                                       wasp.center_y+c.WASP_SPACING))
            elif wasp.angle == 270:  # if attacking from up direction
                wasp2 = Wasp(angle=wasp.angle, change_x=wasp.change_x,
                             position=(wasp.center_x,
                                       wasp.center_y-c.WASP_SPACING))
                wasp3 = Wasp(angle=wasp.angle, change_x=wasp.change_x,
                             position=(wasp.center_x,
                                       wasp.center_y+c.WASP_SPACING))

            self.scene.add_sprite("Wasps", wasp2)
            self.scene.add_sprite("Wasps", wasp3)
        print(f"Attacking wasp speed: {wasp.change_y}")

    def change_view(self, view: arcade.View) -> None:

        arcade.unschedule(self.wasp_attack)
        arcade.pause(1)
        self.window.show_view(view)

    def camera_auto_scroll(self):
        """Auto scroll camera vertically"""
        position = Vec2(0, self.camera_scroll_y)
        if self.camera_scroll_y >= c.SCREEN_HEIGHT:
            Home_View = HomeView()
            self.change_view(Home_View)
        self.camera_scroll_y += c.CAMERA_SPEED
        self.camera.move_to(position, c.CAMERA_SPEED / 2)

    def on_draw(self):
        """Draws outside scene"""
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0,
                                            c.SCREEN_HEIGHT-c.MAIN_VIEW_HEIGHT,
                                            c.MAIN_VIEW_WIDTH,
                                            c.OUTSIDE_HEIGHT,
                                            self.background)
        self.camera.use()
        self.scene.draw()
        text_x = c.SCREEN_WIDTH - 120
        text_y = c.SCREEN_HEIGHT - 30 + self.camera_scroll_y
        arcade.draw_text("Honey:" + str(self.player.score),
                         text_x, text_y,
                         arcade.color.WHITE, 15, 20, 'right')

    def on_update(self, delta_time: float):

        # Move invisible borders along with camera
        for wall in self.scene.name_mapping["Walls"]:
            wall.center_y += c.CAMERA_SPEED

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

        self.edge_check(self.player)


# ################# DRIVER CODE #######################

def main():
    window = Window(c.SCREEN_WIDTH, c.SCREEN_HEIGHT, c.GAME_TITLE)
    # window.center_window()
    home_view = HomeView()
    # home_view.setup()
    window.show_view(home_view)
    window.run()


if __name__ == "__main__":
    main()

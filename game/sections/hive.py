import arcade
import game.constants as c
from game.sprites import Player, BeeEnemy, BeeFriend, Honey
import random
import time


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
                "assets/sprites/bee_shadow1.png")
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
                "assets/sprites/bee_player_move1_2.png")
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
    def __init__(self, left: int = 0,
                 bottom: int = c.INFO_BAR_HEIGHT,
                 width: int = c.MAIN_VIEW_WIDTH,
                 height: int = c.MAIN_VIEW_HEIGHT,
                 **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        self.name = "home"
        self.exit_hole = c.EXIT_HOLE_PINK
        self.scene = arcade.Scene()
        self.scene_over = False  # whether done with this scene (trigger)
        self.player: Player = self.window.player  # save same player b/t views
        self.physics_engine = None
        self.sounds = {
            "hurt": arcade.load_sound("assets/sounds/hurt.wav"),
            "honey": arcade.load_sound("assets/sounds/honey.wav"),
            "background": arcade.load_sound(
                "assets/sounds/background.wav", streaming=True),
            "jump": arcade.load_sound("assets/sounds/jump.wav")
        }
        self.camera = arcade.Camera(self.window.width, self.window.height,
                                    self.window)

        self.setup()

    def setup(self):
        """Sets up a hive scene"""

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
        self.view.clear()
        # arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0,
                                            c.SCREEN_HEIGHT-c.MAIN_VIEW_HEIGHT,
                                            c.MAIN_VIEW_WIDTH,
                                            c.MAIN_VIEW_HEIGHT,
                                            self.background)
        self.camera.use()
        self.scene.draw()

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
            self.view.intro_complete = True
            self.view.change_level("outside_leave")

        # Update all sprites
        for sprite_list in self.scene.sprite_lists:
            sprite_list.update()
        self.player.update_animation()
        self.physics_engine.update()

        # Prevent player from going past screen edge
        self.edge_check(self.player)


class ForeignHiveSection(HiveSection):
    """
    View of a foreign (hostile) bee hive.
    Honey can be collected by colliding with honey sprites.
    Other bees flutter wings as player passes.
    """
    def __init__(self, left: int = 0,
                 bottom: int = c.INFO_BAR_HEIGHT,
                 width: int = c.MAIN_VIEW_WIDTH,
                 height: int = c.MAIN_VIEW_HEIGHT,
                 **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        self.name = "foreign_hive"
        self.scene = arcade.Scene()
        self.player: Player = self.window.player
        self.physics_engine = None
        self.sounds = {
            "hurt": arcade.load_sound("assets/sounds/hurt.wav"),
            "honey": arcade.load_sound("assets/sounds/honey.wav"),
            "background": arcade.load_sound(
                "assets/sounds/background.wav", streaming=True),
            "jump": arcade.load_sound("assets/sounds/jump.wav")
        }
        self.camera = arcade.Camera(self.window.width, self.window.height,
                                    self.window)
        self.time_limit = c.TIME_LIMIT  # when limit reached, level ends
        self.time_elapsed = 0
        self.start_time = 0  # time player enters level, in seconds
        self.setup()

    def setup(self):
        """Sets up a hive scene"""

        self.start_time = time.time()

        self.exit_hole = c.EXIT_HOLE_YELLOW

        arcade.set_background_color(c.BACKGROUND_COLOR)
        self.background = arcade.load_texture(c.BACKGROUND_IMAGE)

        # Background Sound Track
        # arcade.play_sound(self.sounds["background"], looping=True)

        # Create sprite lists
        self.scene.add_sprite_list("Walls")  # , use_spatial_hash=True)
        self.scene.add_sprite_list("Exits")
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Honey")
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

        # Create honey drops with random position and angle, then add to list
        for i in range(c.HONEY_SPRITE_COUNT):
            honey = Honey(c.HONEY_SPRITE_IMAGE, c.HONEY_SPRITE_SCALING)
            self.sprite_random_pos(honey)
            self.scene.add_sprite("Honey", honey)

        # Create bees with random position and angle, then add to list
        for i in range(c.BEE_ENEMY_COUNT):
            bee = BeeEnemy(c.BEE_ENEMY_IMAGE, c.BEE_ENEMY_SCALING)
            self.sprite_random_pos(bee)
            bee.angle = random.randrange(0, 360)
            self.scene.add_sprite("Bees", bee)

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
                                                    [
                                                     self.scene.
                                                     get_sprite_list("Exits")
                                                     ]
                                                    ):
            sprite.center_x = random.randint(padding + c.INFO_BAR_HEIGHT,
                                             (c.SCREEN_WIDTH - padding))
            sprite.center_y = random.randint(padding,
                                             (c.SCREEN_HEIGHT - padding))

    def on_draw(self):
        """Draws hive scene"""
        self.view.clear()
        # arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0,
                                            c.SCREEN_HEIGHT-c.MAIN_VIEW_HEIGHT,
                                            c.MAIN_VIEW_WIDTH,
                                            c.MAIN_VIEW_HEIGHT,
                                            self.background)
        self.camera.use()
        self.scene.draw()
        self.timer_display()

    def check_timer(self):

        # If time limit reached, player is forced to next level
        if self.time_elapsed >= self.time_limit:
            print("Exiting level...")
            self.view.change_level("outside_return")
        self.time_elapsed = time.time() - self.start_time

    def timer_display(self):
        time_left = int(self.time_limit - self.time_elapsed)
        arcade.draw_text("TIME LEFT: " + str(time_left),
                         start_x=c.SCREEN_WIDTH-165,
                         start_y=c.SCREEN_HEIGHT-30,
                         color=arcade.color.SCARLET,
                         font_size=15, width=20, align='left',
                         bold=True)

    def change_view(self, view: arcade.View) -> None:
        """
        the game window displays another view
        this is equivalent to changing the game's level
        """
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
                "assets/sprites/bee_shadow1.png")
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
                "assets/sprites/bee_player_move1_2.png")
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
        elif self.left_pressed and not any([self.up_pressed,
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

        # If time limit reached, player is forced to next level
        self.check_timer()

        # When player touches exit
        if arcade.check_for_collision_with_list(
                                self.player, self.scene.name_mapping["Exits"]):

            print("Exiting level...")
            self.view.change_level("outside_return")

        # When player touches honey drop
        collision_list = arcade.check_for_collision_with_list(
                                self.player, self.scene.name_mapping["Honey"])
        if not self.player.flying:  # if player isn't flying
            for honey in collision_list:
                arcade.play_sound(self.sounds["honey"])
                honey.remove_from_sprite_lists()  # remove honey drop
                self.player.score += 1  # update player score

        # When player touches a bee, bee wings flutter
        collisions: list[BeeEnemy] = arcade.check_for_collision_with_list(
            self.player, self.scene.get_sprite_list("Bees"))
        # arcade.play_sound(self.sounds["hurt"])
        if collisions:
            for bee in collisions:
                bee.fluttering = True

        # Update all sprites
        for sprite_list in self.scene.sprite_lists:
            sprite_list.update()
        for bee in self.scene.get_sprite_list("Bees"):
            bee.update_animation()
        self.player.update_animation()
        self.physics_engine.update()

        self.edge_check(self.player)

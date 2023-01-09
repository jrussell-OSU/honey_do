
import arcade
import game.constants as c
from game.sprites import Player, Wasp, Scent
import random
from pyglet.math import Vec2


class OutsideSection(arcade.Section):
    def __init__(self, left: int, bottom: int, width: int, height: int,
                 **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        self.camera_scroll_y = c.INFO_BAR_HEIGHT

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
        view.window.setup()
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
            self.player.change_y = c.CAMERA_SPEED
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

    def update_player_speed(self):

        # Calculate speed based on the keys pressed
        self.player.change_x = 0
        self.player.change_y = c.CAMERA_SPEED * .50

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
    Player follows 'scent trail' of another hive's honey.
    """
    def __init__(self, left: int = 0,
                 bottom: int = c.INFO_BAR_HEIGHT,
                 width: int = c.MAIN_VIEW_WIDTH,
                 height: int = c.MAIN_VIEW_HEIGHT,
                 **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        self.name = "outside_leave"
        self.scene = arcade.Scene()
        self.player: Player = self.window.player
        self.camera = arcade.Camera(self.window.width, self.window.height)

        self.setup()

    def setup(self):

        # so player at rest keeps up with camera scroll
        self.player.change_y = c.CAMERA_SPEED

        self.scene_name = "outside"

        # Setup background image
        self.background = arcade.load_texture(
            c.OUTSIDE_IMAGE, width=800, height=c.OUTSIDE_HEIGHT)

        # Create sprite lists
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)

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
        self.player.position = (c.SCREEN_WIDTH/2, c.SCREEN_HEIGHT/2)
        self.player.angle = 0
        self.scene.add_sprite("Player", self.player)
        # self.player.hurt = False

        # start the scent trail
        self.scene.add_sprite_list("Scents")
        self.scent_creation_timer()
        self.first_scent_created = False

        # Set and apply physics engine
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene.name_mapping["Walls"]
        )

    def camera_auto_scroll(self):
        """Auto scroll camera vertically"""
        position = Vec2(0, self.camera_scroll_y)
        # if self.camera_scroll_y >= c.SCREEN_HEIGHT:  # for DEBUG
        if self.camera_scroll_y >= c.OUTSIDE_HEIGHT - c.SCREEN_HEIGHT:
            self.view.change_level("foreign_hive")
        self.camera_scroll_y += c.CAMERA_SPEED
        self.camera.move_to(position, c.CAMERA_SPEED / 2)

    def scent_creation_timer(self):
        arcade.schedule(self.scent_trail, c.SCENT_TRAIL_INTERVAL)

    def scent_trail(self, *args):
        """Trail of yellow sprites the player must follow and touch
        within timelimit to proceed to next level"""

        print("dropping scent..")
        scent = Scent()
        # Position scent in random x position, y = above screen top edge
        x, y = 0, 0
        y = self.camera_scroll_y + c.SCREEN_HEIGHT + 50
        if not self.first_scent_created:
            self.first_scent_created = True
            x = random.randint(50, c.SCREEN_WIDTH-50)
        else:
            scents = self.scene.get_sprite_list("Scents")
            if len(scents) > 0:
                x_prev = scents[-1].center_x
            else:
                x_prev = c.MAIN_VIEW_WIDTH / 2
            x = x_prev + random.randint(-1 * c.SCENT_DELTA_X_MAX,
                                        c.SCENT_DELTA_X_MAX)
            if x > c.SCREEN_WIDTH - c.PADDING:
                x = c.SCREEN_WIDTH - c.PADDING
            if x < c.PADDING:
                x = c.PADDING

        scent.position = (x, y)
        self.scene.add_sprite("Scents", scent)

    def on_draw(self):
        """Draws outside scene"""
        self.view.clear()
        arcade.draw_lrwh_rectangle_textured(0,
                                            c.SCREEN_HEIGHT-c.MAIN_VIEW_HEIGHT,
                                            c.MAIN_VIEW_WIDTH,
                                            c.OUTSIDE_HEIGHT,
                                            self.background)
        self.camera.use()
        self.scene.draw()

    def on_update(self, delta_time: float):

        self.player.update_animation()

        scent_collisions = arcade.check_for_collision_with_list(
                self.player, self.scene.name_mapping["Scents"])
        for scent in scent_collisions:
            scent.remove_from_sprite_lists()

        # if any scents fall off bottom of screen, player returns home
        for scent in self.scene.get_sprite_list("Scents"):
            if scent.center_y < self.camera_scroll_y + c.INFO_BAR_HEIGHT:
                arcade.unschedule(self.scent_trail)
                self.view.change_level("home")

        # Update all sprites
        for sprite_list in self.scene.sprite_lists:
            sprite_list.update()

        self.physics_engine.update()

        self.camera_auto_scroll()

        self.edge_check(self.player)


class OutsideReturn(OutsideSection):
    """
    View of outside, top-scrolling. Heading toward home.
    Wasps attack player and take their honey.
    """
    def __init__(self, left: int = 0,
                 bottom: int = c.INFO_BAR_HEIGHT,
                 width: int = c.MAIN_VIEW_WIDTH,
                 height: int = c.MAIN_VIEW_HEIGHT,
                 **kwargs):
        super().__init__(left, bottom, width, height, **kwargs)

        self.name = "outside_return"
        self.scene = arcade.Scene()
        # self.window.views["hive"] = HiveView()
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

        self.setup()

    def setup(self):

        # so player at rest keeps up with camera scroll
        self.player.change_y = c.CAMERA_SPEED

        # self.window.views["outside"] = self

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
        self.player.position = (c.SCREEN_WIDTH/2, c.SCREEN_HEIGHT/2)
        self.player.angle = 0
        self.scene.add_sprite("Player", self.player)
        # self.player.hurt = False

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
        # if self.camera_scroll_y >= c.SCREEN_HEIGHT:
        if self.camera_scroll_y >= c.OUTSIDE_HEIGHT - c.SCREEN_HEIGHT:
            self.view.change_level("home")
        self.camera_scroll_y += c.CAMERA_SPEED
        self.camera.move_to(position, c.CAMERA_SPEED / 2)

    def on_draw(self):
        """Draws outside scene"""
        self.view.clear()
        arcade.draw_lrwh_rectangle_textured(0,
                                            c.SCREEN_HEIGHT-c.MAIN_VIEW_HEIGHT,
                                            c.MAIN_VIEW_WIDTH,
                                            c.OUTSIDE_HEIGHT,
                                            self.background)
        self.camera.use()
        self.scene.draw()

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
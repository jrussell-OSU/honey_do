
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

    def randomly_position_sprite(self, sprite, padding=c.PADDING):
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

    def enforce_screen_edge_for_sprite(self, sprite: Player):
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

        self.background = arcade.load_texture(
            c.OUTSIDE_IMAGE, width=800, height=c.OUTSIDE_HEIGHT)

        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.key_press_state_setup()
        self.player_setup()
        self.scene.add_sprite_list("Scents")
        self.start_scent_creation_timer()
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene.name_mapping["Walls"]
        )

    def player_setup(self) -> None:
        """Set player attributes and position for this level"""

        # so player at rest keeps up with camera scroll
        self.player.change_y = c.CAMERA_SPEED

        self.player.outside = True
        self.player.hurt = False
        self.player.flying = False
        self.player.walking = False
        self.player.position = (c.SCREEN_WIDTH/2, c.SCREEN_HEIGHT/2)
        self.player.angle = 0
        self.scene.add_sprite("Player", self.player)

    def key_press_state_setup(self) -> None:
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

    def start_scent_creation_timer(self):
        arcade.schedule(self.place_scent_trail, c.SCENT_TRAIL_INTERVAL)

    def place_scent_trail(self, delta_time: float):
        """
        Trail of scent sprites player must collect to reach next level
        Note: delta_time arg required for arcade.schedule() method
        """
        # Place scent sprite position (x = random, y = above screen-top)
        x = self.get_random_x_for_scent()
        y = self.camera_scroll_y + c.SCREEN_HEIGHT + 50

        scent = Scent()
        scent.position = (x, y)
        self.scene.add_sprite("Scents", scent)

    def get_random_x_for_scent(self):
        """Get random x coordinate, without going past screen edges"""

        # Use previous scent's x coord and add random -/+ num
        scents = self.scene.get_sprite_list("Scents")
        if len(scents) > 0:
            previous_scent_x = scents[-1].center_x
        else:
            previous_scent_x = c.MAIN_VIEW_WIDTH / 2
        random_x_change = random.randint(-1 * c.SCENT_DELTA_X_MAX, c.SCENT_DELTA_X_MAX)
        x = previous_scent_x + random_x_change

        # If x past view edge, move other direction
        if x > c.MAIN_VIEW_WIDTH - c.PADDING:
            x = (c.MAIN_VIEW_WIDTH - c.PADDING) - random_x_change
        elif x < c.PADDING:
            x = c.PADDING + random_x_change

        return x

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

        if self.scent_has_reached_view_bottom():
            self.change_level("home")
        elif self.camera_at_level_end():
            self.change_level("hive")

        self.handle_scent_collisions_with_player()
        self.player.update_animation()
        self.update_all_sprites()
        self.physics_engine.update()
        self.camera_auto_scroll()
        self.enforce_screen_edge_for_sprite(self.player)

    def camera_at_level_end(self):
        # if self.camera_scroll_y >= c.SCREEN_HEIGHT:  # for DEBUG
        if self.camera_scroll_y >= c.OUTSIDE_HEIGHT - c.SCREEN_HEIGHT:
            return True
        return False

    def change_level(self, level_name: str) -> None:
        arcade.unschedule(self.place_scent_trail)
        self.view.change_level(level_name)

    def camera_auto_scroll(self):
        """Auto scroll camera vertically"""
        position = Vec2(0, self.camera_scroll_y)

        self.camera_scroll_y += c.CAMERA_SPEED
        self.camera.move_to(position, c.CAMERA_SPEED / 2)

    def update_all_sprites(self) -> None:
        for sprite_list in self.scene.sprite_lists:
            sprite_list.update()

    def handle_scent_collisions_with_player(self) -> None:
        scent_collisions = arcade.check_for_collision_with_list(
                self.player, self.scene.name_mapping["Scents"])
        for scent in scent_collisions:
            scent.remove_from_sprite_lists()

    def scent_has_reached_view_bottom(self) -> bool:
        for scent in self.scene.get_sprite_list("Scents"):
            if scent.center_y < self.camera_scroll_y + c.INFO_BAR_HEIGHT:
                return False
        return True


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
        self.player: Player = self.window.player
        self.physics_engine = None
        self.sounds = {
            "hurt": arcade.load_sound("assets/sounds/hurt.wav"),
            "honey": arcade.load_sound("assets/sounds/honey.wav"),
            "background": arcade.load_sound(
                "assets/sounds/background.wav", streaming=True),
            "jump": arcade.load_sound("assets/sounds/jump.wav")
        }
        self.camera = arcade.Camera(self.window.width, self.window.height, self.window)

        self.setup()

    def setup(self):

        self.background = arcade.load_texture(
            c.OUTSIDE_FLIPPED, width=800, height=c.OUTSIDE_HEIGHT)

        # no walls used, but arcade physics engine seems to require this list
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Wasps")
        self.wasp_attacks_setup()
        self.key_press_state_setup()
        self.player_setup()
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player, self.scene.name_mapping["Walls"]
        )

    def player_setup(self) -> None:
        """Set player attributes and position for this level"""

        # so player at rest keeps up with camera scroll
        self.player.change_y = c.CAMERA_SPEED

        self.player.outside = True
        self.player.hurt = False
        self.player.flying = False
        self.player.walking = False
        self.player.position = (c.SCREEN_WIDTH/2, c.SCREEN_HEIGHT/2)
        self.player.angle = 0
        self.scene.add_sprite("Player", self.player)

    def key_press_state_setup(self) -> None:
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

    def wasp_attacks_setup(self) -> None:
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

        if self.camera_at_level_end():
            self.change_level("home")

        self.handle_wasp_collisions_with_player()
        self.update_all_sprites()
        self.physics_engine.update()
        self.camera_auto_scroll()
        self.enforce_screen_edge_for_sprite(self.player)

    def camera_at_level_end(self):
        # if self.camera_scroll_y >= c.SCREEN_HEIGHT:  # for DEBUG
        if self.camera_scroll_y >= c.OUTSIDE_HEIGHT - c.SCREEN_HEIGHT:
            return True
        return False

    def update_all_sprites(self) -> None:
        for sprite_list in self.scene.sprite_lists:
            sprite_list.update()
        for wasp in self.scene.name_mapping["Wasps"]:
            wasp.update_animation()
        self.player.update_animation()

    def handle_wasp_collisions_with_player(self):
        """
        When player touches a WASP, decrement score
        if player isn't already being "hurt" by wasp
        """
        if arcade.check_for_collision_with_list(
                self.player, self.scene.name_mapping["Wasps"]):
            if not self.player.hurt and not self.player.flying:
                self.player.hurt = True
                if self.player.score > 0:  # score can't be negative
                    self.player.score -= 1
        else:
            self.player.hurt = False

    def change_level(self, level_name: str) -> None:
        arcade.unschedule(self.wasp_attack)
        self.view.change_level(level_name)

    def camera_auto_scroll(self):
        """Auto scroll camera vertically"""
        position = Vec2(0, self.camera_scroll_y)
        # if self.camera_scroll_y >= c.SCREEN_HEIGHT:  # for debugging
        if self.camera_scroll_y >= c.OUTSIDE_HEIGHT - c.SCREEN_HEIGHT:
            self.change_level("home")
        self.camera_scroll_y += c.CAMERA_SPEED
        self.camera.move_to(position, c.CAMERA_SPEED / 2)

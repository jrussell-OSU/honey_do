
import arcade
import constants as c
import random


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

        # approx. radius of the sprite
        self.radius = 16 * c.PLAYER_SPRITE_SCALING

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

        '''
        # Prevent player going past screen edge
        if self.center_x > (c.MAIN_VIEW_WIDTH - self.radius):
            self.center_x = (c.MAIN_VIEW_WIDTH - self.radius)
        if self.center_x < (0 + self.radius):
            self.center_x = (0 + self.radius)
        if self.center_y < (c.INFO_BAR_HEIGHT + self.radius):
            self.center_y = (c.INFO_BAR_HEIGHT + self.radius)
        if self.center_y > (c.SCREEN_HEIGHT - self.radius):
            self.center_y = (c.SCREEN_HEIGHT - self.radius)
        '''

        # player animation
        if self.hurt:
            if self.frame % (20 // c.ANIMATION_SPEED) == 0:
                self.texture = self.hurt_textures[self.texture_index]
                self.texture_index = (self.texture_index + 1)\
                    % len(self.hurt_textures)
        elif self.flying:
            if self.frame % (20 // c.ANIMATION_SPEED) == 0:
                self.texture = self.flying_textures[self.texture_index]
                self.texture_index = (self.texture_index + 1)\
                    % len(self.flying_textures)
        elif self.walking:
            if self.frame % (20 // c.ANIMATION_SPEED) == 0:
                self.texture = self.walking_textures[self.texture_index]
                self.texture_index = (self.texture_index + 1)\
                    % len(self.walking_textures)
        elif self.outside:
            if self.frame % (20 // c.ANIMATION_SPEED) == 0:
                self.texture = self.outside_textures[self.texture_index]
                self.texture_index = (self.texture_index + 1)\
                    % len(self.outside_textures)

        self.frame += 1


class BeeEnemy(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)

        self.fluttering = False
        self.frames = {
                  "idle": arcade.load_texture(c.BEE_ENEMY_IMAGE),
                  "moving1": arcade.load_texture(c.BEE_ENEMY_MOVING_1),
                  "moving2": arcade.load_texture(c.BEE_ENEMY_MOVING_2),
                  "moving3": arcade.load_texture(c.BEE_ENEMY_MOVING_3)
                  }

    def update_animation(self) -> None:
        if self.fluttering:
            self.texture = self.frames["moving2"]
            self.fluttering = False
        else:
            self.texture = self.frames["idle"]
            if random.randint(0, c.BEE_ROTATE_CHANCE) == c.BEE_ROTATE_CHANCE:
                delta_angle = random.randrange(-45, 45)
                self.angle = (self.angle + delta_angle) % 360


class BeeFriend(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)


class Wasp(arcade.Sprite):
    def __init__(self, sprite=c.WASP_IMAGE, scaling=c.WASP_SCALING,
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
        if self.frame % (20 // c.ANIMATION_SPEED) == 0:
            self.texture = self.flying_textures[self.texture_index]
            self.texture_index = (self.texture_index + 1)\
                % len(self.flying_textures)

        self.frame += 1


class Honey(arcade.Sprite):
    def __init__(self, sprite, scaling):
        super().__init__(sprite, scaling)


class Scent(arcade.Sprite):
    def __init__(self, sprite=c.SCENT_SPRITE_IMAGE,
                 scaling=c.SCENT_SPRITE_SCALING):
        super().__init__(sprite, scaling)

    def update_animation(self):
        pass

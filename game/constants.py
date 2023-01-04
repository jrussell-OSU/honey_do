
import arcade

# Window Settings:
BACKGROUND_COLOR = arcade.color.BLACK
FADE_RATE = 5  # TODO: do fading of views
GAME_TITLE = "Honey Thief"
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 750

# Main Game View Settings
BACKGROUND_IMAGE = "../assets/backgrounds/honeycomb.png"
CAMERA_SPEED = 2.0
EXIT_HOLE_YELLOW = "../assets/sprites/exit_hole_yellow.png"
EXIT_HOLE_PINK = "../assets/sprites/exit_hole_pink.png"
HOME_BACKGROUND = "../assets/backgrounds/honeycomb_map_pink_empty.png"
MAIN_VIEW_WIDTH = SCREEN_WIDTH
MAIN_VIEW_HEIGHT = 600
OUTSIDE_HEIGHT = 8896
OUTSIDE_IMAGE = "../assets/backgrounds/wilderness_neighborhood.png"
OUTSIDE_FLIPPED = "../assets/backgrounds/wilderness_neighborhood_flipped.png"
PADDING = 25  # how many pixels from edge of screen to place sprites

# Foreign Hive Settings
TIME_LIMIT = 30

# Info Bar Settings
INFO_BAR_HEIGHT = 150
INFO_BAR_WIDTH = SCREEN_WIDTH
TYPING_SPEED = 4

# Sprite Settings:
ANIMATION_SPEED = 3  # lower = slow, higher = faster
BEE_ENEMY_COUNT = 600
BEE_ENEMY_SCALING = 1.5
BEE_ENEMY_IMAGE = "../assets/sprites/bee.png"
BEE_FRIEND_COUNT = 20
BEE_FRIEND_SCALING = 1.0
BEE_ROTATE_CHANCE = 2000  # higher means bees less likely to change angle
BEE_FRIEND_IMAGE = "../assets/sprites/bee_player_move1_2.png"
BEE_ENEMY_MOVING_1 = "../assets/sprites/foreign_bees_moving1.png"
BEE_ENEMY_MOVING_2 = "../assets/sprites/foreign_bees_moving2.png"
BEE_ENEMY_MOVING_3 = "../assets/sprites/foreign_bees_moving3.png"

HONEY_SPRITE_SCALING = 1.25
HONEY_SPRITE_COUNT = 15
HONEY_SPRITE_IMAGE = "../assets/sprites/honey.png"

PLAYER_SPRITE_SCALING = 1.0
PLAYER_SPRITE_IMAGE = "../assets/sprites/bee_player_move1_2.png"
PLAYER_MOVE_SPEED = 1.75
PLAYER_ANGLE_SPEED = 3

WASP_SCALING = 1.5
WASP_IMAGE = "../assets/sprites/wasp_flying1.png"
WASP_SPEED_MIN = 7
WASP_SPEED_MAX = 8
WASP_ATTACK_INTERVAL = 3
WASP_SPACING = 150

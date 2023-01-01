
import arcade

# Screen Settings:
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 750
MAIN_VIEW_WIDTH = SCREEN_WIDTH
MAIN_VIEW_HEIGHT = 600
BOTTOM_VIEW_HEIGHT = 150
BOTTOM_VIEW_WIDTH = 800
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

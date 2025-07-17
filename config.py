import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


# Asset directories
PATH_CONFIG = {
    "run": os.path.join(BASE_PATH, "run"),
    "fly": os.path.join(BASE_PATH, "fly"), 
    "idle": os.path.join(BASE_PATH, "idle"),
    "sit": os.path.join(BASE_PATH, "sit"),
    "extras": os.path.join(BASE_PATH, "extras"),
}

# Frame counts for each animation
FRAME_COUNTS = {
    "run": 7,
    "fly": 4,
    "idle": 4,
    "sit": 10,
}

# Animation and movement settings
TICK_MS = 95  # Animation timer tick in milliseconds
WALK_SPEED = 160  # Walking speed in pixels per second
FLY_SPEED = 300  # Flying speed in pixels per second
WALK_INCREMENT = WALK_SPEED * TICK_MS / 1000.0  # Pixels to move per tick when walking
FLY_INCREMENT = FLY_SPEED * TICK_MS / 1000.0  # Pixels to move per tick when flying
CIRCLE_DURATION = 5.0  # Duration of circling animation in seconds
CIRCLE_RADIUS = 50  # Radius of circle flight pattern in pixels

# Tiredness parameters
TIREDNESS_DECREASE_RATE = 2.0  # Decrease per second when walking
TIREDNESS_RECOVERY_RATE = 1.0  # Recovery per 2 seconds when sitting
TIRED_THRESHOLD = 10  # Threshold to trigger sitting
RECOVERY_THRESHOLD = 30  # Threshold to return to idle after sitting

# Canvas size for sprite rendering
CANVAS_SIZE_WIDTH = 300
CANVAS_SIZE_HEIGHT = 300

# Sprite naming conventions
SPRITE_CONFIG = {
    "run": {
        "right": "tailsRun",
        "left": "tailsRunB"
    },
    "fly": {
        "right": "tailsFly",
        "left": "tailsFlyB"
    },
    "idle": {
        "right": "tailsIdle",
        "left": "tailsIdleB"
    },
    "sit": {
        "right": "tailsSit",
        "left": "tailsSitB"
    },
    "bubble": "bubble.png"
}

# State transition configuration for the FSM
STATE_TRANSITIONS = {
    "idle": {
        "right_click": ["walk", "fly"],  # Depends on click position
        "tired": "sit",
        "default": "idle"
    },
    "walk": {
        "target_reached": "idle",
        "right_click": ["walk", "fly"],  # Depends on click position
        "default": "walk"
    },
    "fly": {
        "target_reached": "circle",
        "right_click": ["walk", "fly"],  # Depends on click position
        "default": "fly"
    },
    "circle": {
        "circle_complete": "idle",
        "right_click": ["walk", "fly"],  # Depends on click position
        "default": "circle"
    },
    "sit": {
        "recovered": "idle",
        "right_click": ["walk", "fly"],  # Depends on click position
        "default": "sit"
    }
}
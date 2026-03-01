
# Simulation Configuration
GRID_SIZE = 10
CELL_SIZE = 50
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE + 100  # Extra space for dashboard

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 50, 50)     # Obstacle
GREEN = (50, 255, 50)   # Child
BLUE = (50, 50, 255)    # Target
YELLOW = (255, 255, 0)  # Highlight Action
ORANGE = (255, 165, 0)  # Arrow Action

# Q-Learning Hyperparameters
ALPHA = 0.1       # Learning Rate
GAMMA = 0.9       # Discount Factor
EPSILON_START = 1.0
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.995
NUM_EPISODES = 3000  # Increase for better training

# Actions
ACTION_NONE = 0      # Observe (Let child decide)
ACTION_ARROW = 1     # Show directional arrow
ACTION_HIGHLIGHT = 2 # Highlight target

ACTIONS = [ACTION_NONE, ACTION_ARROW, ACTION_HIGHLIGHT]

# Rewards
REWARD_GOAL = 100        # Reaching the target
REWARD_PROGRESS = 10     # Moving closer to target
REWARD_INDEPENDENCE = 50 # Making correct move without help (Action 0)
REWARD_PENALTY_HELP = -2 # Small penalty for using help
REWARD_COLLISION = -5    # Hitting wall/obstacle
REWARD_REGRESSION = -5   # Moving away from target
REWARD_STEP = -1         # Time penalty


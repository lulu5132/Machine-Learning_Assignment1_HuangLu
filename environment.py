import numpy as np
import random
from config import *
from child_model import Child

class SupermarketEnv:
    def __init__(self):
        self.grid = None
        self.child = None
        self.start_pos = (0, 0)
        self.target_pos = (GRID_SIZE - 1, GRID_SIZE - 1)
        self.num_obstacles = 15 # Approx 15% density
        self.steps = 0
        self.reset()

    def reset(self):
        """Generate a new random map for each episode."""
        self.grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        
        # Place random obstacles (avoiding start and target)
        count = 0
        # Reduced obstacle count slightly to prevent blocking too easily
        target_obstacles = int(GRID_SIZE * GRID_SIZE * 0.15) 
        
        while count < target_obstacles:
            ox, oy = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            # Ensure start (0,0) and its immediate neighbors are free
            if (ox, oy) == (0, 0): continue
            if (ox, oy) == (0, 1): continue
            if (ox, oy) == (1, 0): continue
            
            # Ensure target (bottom-right area) is somewhat free
            if (ox, oy) == (GRID_SIZE-1, GRID_SIZE-1): continue

            if self.grid[oy][ox] == 0:
                self.grid[oy][ox] = 1 # 1 represents obstacle
                count += 1
        
        self.start_pos = (0, 0)
        
        # Ensure target is reachable and not on obstacle
        while True:
            tx, ty = random.randint(GRID_SIZE//2, GRID_SIZE-1), random.randint(GRID_SIZE//2, GRID_SIZE-1)
            if self.grid[ty][tx] == 0 and (tx, ty) != (0, 0):
                self.target_pos = (tx, ty)
                break
        
        self.child = Child(self.start_pos, self.target_pos)
        self.steps = 0
        return self.get_state()

    def get_state(self):
        """
        State Space:
        1. Relative position (dx, dy)
        2. Local obstacle sensors (up, down, left, right)
        """
        cx, cy = self.child.position
        tx, ty = self.target_pos
        
        dx = tx - cx
        dy = ty - cy
        
        # Obstacle sensors (1 if blocked/wall, 0 if free)
        # Directions: Up, Down, Left, Right
        u = 1 if cy == 0 or self.grid[cy-1][cx] == 1 else 0
        d = 1 if cy == GRID_SIZE-1 or self.grid[cy+1][cx] == 1 else 0
        l = 1 if cx == 0 or self.grid[cy][cx-1] == 1 else 0
        r = 1 if cx == GRID_SIZE-1 or self.grid[cy][cx+1] == 1 else 0
        
        return (dx, dy, u, d, l, r)

    def step(self, action):
        """
        Execute one step.
        AI chooses action -> Env updates Child -> Calculate Reward
        """
        # Store previous position to calculate distance correctly
        prev_pos = list(self.child.position)
        prev_dist = abs(prev_pos[0] - self.target_pos[0]) + \
                   abs(prev_pos[1] - self.target_pos[1])
        
        # Execute action (Child moves based on guidance)
        new_pos, moved = self.child.move(action, self.grid)
        
        curr_dist = abs(new_pos[0] - self.target_pos[0]) + \
                    abs(new_pos[1] - self.target_pos[1])
        
        self.steps += 1
        reward = 0
        done = False
        
        # 1. Goal Reached
        if tuple(new_pos) == self.target_pos:
            reward += REWARD_GOAL
            done = True
            return self.get_state(), reward, done

        # 2. Progress Reward
        if curr_dist < prev_dist:
            reward += REWARD_PROGRESS
            # 3. Independence Bonus (Correct move with no help)
            if action == ACTION_NONE:
                reward += REWARD_INDEPENDENCE
        elif curr_dist > prev_dist:
             reward += REWARD_REGRESSION
        else:
             # Didn't move (stuck or hit wall)
             reward += REWARD_COLLISION

        # 4. Dependency Penalty
        if action != ACTION_NONE:
            reward += REWARD_PENALTY_HELP
            
        # Time penalty to encourage speed
        reward += REWARD_STEP
        
        # Timeout prevention
        if self.steps > 100:
            done = True
            
        return self.get_state(), reward, done

import random
from config import *

class Child:
    """
    Simulated Child Agent for the Environment.
    The child moves in the grid based on simple heuristics and randomness.
    """
    def __init__(self, position, target):
        self.position = list(position)
        self.target = list(target)
        self.directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Down, Up, Right, Left

    def move(self, guidance_action, grid):
        """
        Determines the child's next move based on guidance.
        
        Args:
            guidance_action (int): The action taken by the AI guide (0: None, 1: Arrow, 2: Highlight).
            grid (list): The current state of the grid (to check for obstacles).
            
        Returns:
            tuple: (new_position, made_move)
        """
        possible_moves = []
        best_moves = []
        
        # Identify valid moves (not hitting obstacles or walls)
        for dx, dy in self.directions:
            nx, ny = self.position[0] + dx, self.position[1] + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and grid[ny][nx] == 0: # 0 is empty
                possible_moves.append((nx, ny))
                
                # Check if this move gets closer to target (Manhattan distance)
                curr_dist = abs(self.target[0] - self.position[0]) + abs(self.target[1] - self.position[1])
                new_dist = abs(self.target[0] - nx) + abs(self.target[1] - ny)
                if new_dist < curr_dist:
                    best_moves.append((nx, ny))
        
        if not possible_moves:
            return tuple(self.position), False # Stuck

        # Decision making logic based on guidance
        next_pos = self.position
        
        if guidance_action == ACTION_NONE:
            # Without help: 60% chance best move, 40% random move
            if random.random() < 0.6 and best_moves:
                next_pos = random.choice(best_moves)
            else:
                next_pos = random.choice(possible_moves)
                
        elif guidance_action == ACTION_ARROW:
            # With arrow: 90% chance best move
            if random.random() < 0.9 and best_moves:
                next_pos = random.choice(best_moves)
            else:
                next_pos = random.choice(possible_moves)
                
        elif guidance_action == ACTION_HIGHLIGHT:
            # With highlight: 95% chance best move (strongest cue)
            if random.random() < 0.95 and best_moves:
                next_pos = random.choice(best_moves)
            else:
                next_pos = random.choice(possible_moves)

        self.position = list(next_pos)
        return tuple(self.position), True

    def get_pos(self):
        return tuple(self.position)

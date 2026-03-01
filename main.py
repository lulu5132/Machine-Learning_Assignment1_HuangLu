import pygame
import matplotlib.pyplot as plt
import numpy as np
import time
import os
import sys
import imageio
from config import *
from environment import SupermarketEnv
from agent import QLearningAgent
import visuals

# Determine if we are running in a headless environment (no display)
# On Windows, DISPLAY is never set, so we only check SDL_VIDEODRIVER explicitly
IS_HEADLESS = os.environ.get("SDL_VIDEODRIVER") == "dummy"

# Global Assets Dictionary
ASSETS = {}
OUTPUT_DIR = "outputs"


def output_path(filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return os.path.join(OUTPUT_DIR, filename)

def load_game_assets():
    """Initializes assets. Must be called after pygame.display.set_mode."""
    global ASSETS
    if not ASSETS:
        try:
            ASSETS['floor'] = visuals.create_floor_tile(CELL_SIZE)
            ASSETS['shelf'] = visuals.create_shelf_tile(CELL_SIZE)
            ASSETS['player'] = visuals.create_character_sprite(CELL_SIZE)
            ASSETS['target'] = visuals.create_target_item_sprite(CELL_SIZE)
            ASSETS['arrow'] = visuals.create_arrow_sprite(CELL_SIZE)
        except Exception as e:
            print(f"Error loading assets: {e}")

def draw_game_grid(screen, env, message=""):
    """Draws the game state using pixel art assets."""
    screen.fill(WHITE)
    
    # Draw Floor
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
    
            # Draw Floor Tiles
            screen.blit(ASSETS['floor'], (x * CELL_SIZE, y * CELL_SIZE))

    # Draw Obstacles (Shelves)
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if env.grid[y][x] == 1:
                screen.blit(ASSETS['shelf'], (x * CELL_SIZE, y * CELL_SIZE))

    # Draw Target
    tx, ty = env.target_pos
    pygame.draw.circle(screen, (255, 255, 200), 
                       (tx * CELL_SIZE + CELL_SIZE//2, ty * CELL_SIZE + CELL_SIZE//2), 
                       CELL_SIZE//2 + 5)
    screen.blit(ASSETS['target'], (tx * CELL_SIZE, ty * CELL_SIZE))
    
    # Draw Child
    cx, cy = env.child.position
    screen.blit(ASSETS['player'], (cx * CELL_SIZE, cy * CELL_SIZE))
    
    # Draw In-Game Message (Near Player)
    if message:
        font = pygame.font.SysFont(None, 24)
        text_surf = font.render(message, True, RED)
        
        # Calculate position relative to player
        screen_x = cx * CELL_SIZE + (CELL_SIZE - text_surf.get_width()) // 2
        screen_y = cy * CELL_SIZE - 25 # Default above head
        
        # Adjust if too close to edges
        if screen_y < 10: 
            screen_y = cy * CELL_SIZE + CELL_SIZE + 5 # Move below feet
        if screen_x < 5: 
            screen_x = 5
        if screen_x + text_surf.get_width() > SCREEN_WIDTH - 5: 
            screen_x = SCREEN_WIDTH - text_surf.get_width() - 5
            
        # Draw background box for text
        bg_rect = pygame.Rect(screen_x - 5, screen_y - 3, text_surf.get_width() + 10, text_surf.get_height() + 6)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect)
        pygame.draw.rect(screen, RED, bg_rect, 1) # Border
        
        screen.blit(text_surf, (screen_x, screen_y))

def draw_guidance(screen, action, child_pos, target_pos):
    """Draws the AI guidance overlay."""
    cx, cy = child_pos
    center_x = cx * CELL_SIZE + CELL_SIZE // 2
    center_y = cy * CELL_SIZE + CELL_SIZE // 2
    
    if action == ACTION_ARROW:
        # Calculate direction to target
        tx, ty = target_pos
        dx = tx - cx
        dy = ty - cy
        
        # Calculate angle (negative because y increases downwards in Pygame)
        angle = np.degrees(np.arctan2(-dy, dx))
        
        # Rotate arrow sprite
        arrow_surf = pygame.transform.rotate(ASSETS['arrow'], angle)
        rect = arrow_surf.get_rect(center=(center_x, center_y))
        screen.blit(arrow_surf, rect)
        
    elif action == ACTION_HIGHLIGHT:
        # Strong localized highlight around target
        tx, ty = target_pos
        padding = 5
        rect = (tx * CELL_SIZE - padding, ty * CELL_SIZE - padding, 
                CELL_SIZE + 2*padding, CELL_SIZE + 2*padding)
        pygame.draw.rect(screen, YELLOW, rect, 4)
        
        # Flashing effect
        s = pygame.Surface((CELL_SIZE, CELL_SIZE))
        s.set_alpha(100) # Transparency
        s.fill(YELLOW)
        screen.blit(s, (tx * CELL_SIZE, ty * CELL_SIZE))

def draw_ui(screen, steps, action, reward, total_reward, message=""):
    """Draws the dashboard."""
    font = pygame.font.SysFont(None, 24)
    y_offset = GRID_SIZE * CELL_SIZE + 10
    
    # Background for dashboard
    pygame.draw.rect(screen, (240, 240, 240), (0, GRID_SIZE * CELL_SIZE, SCREEN_WIDTH, 120))
    
    action_text = "AI: Observing..."
    if action == ACTION_ARROW: action_text = "AI Suggests: FOLLOW ARROW"
    elif action == ACTION_HIGHLIGHT: action_text = "AI Suggests: GO TO HIGHLIGHT"
    
    # Text Colors
    col_ai = (0, 100, 0) if action == ACTION_NONE else ORANGE
    col_msg = RED if "Blocked" in message else BLUE
    
    lines = [
        (f"Steps: {steps} | Score: {total_reward}", BLACK),
        (f"Last Reward: {reward}", BLACK),
        (action_text, col_ai),
        (message, col_msg)
    ]
    
    for i, (text, col) in enumerate(lines):
        img = font.render(text, True, col)
        screen.blit(img, (20, y_offset + i * 25))

def show_summary_screen(screen, total_steps, total_score, episodes_completed):
    """Displays a game summary report."""
    running = True
    font_title = pygame.font.SysFont(None, 40)
    font_text = pygame.font.SysFont(None, 28)
    
    while running:
        screen.fill(WHITE)
        
        # Title
        title = font_title.render("Session Summary", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        
        # Stats
        lines = [
            f"Episodes Completed: {episodes_completed}",
            f"Total Steps Taken: {total_steps}",
            f"Final Total Score: {total_score}",
            "",
            "Analysis:",
            "Good engagement with the environment.",
            "Remember to look for AI hints!",
            "",
            "Press ESC or Close to Exit"
        ]
        
        for i, line in enumerate(lines):
            col = BLACK
            if "Analysis" in line: col = BLUE
            text = font_text.render(line, True, col)
            screen.blit(text, (40, 80 + i * 35))
            
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

def run_simulation_demo(agent, env, save_gif=True, gif_name="demo.gif"):
    """Runs a simulated episode and saves it as a GIF."""
    # Setup Display
    if save_gif and IS_HEADLESS:
        # Only use dummy driver for GIF generation in headless environments
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    elif "SDL_VIDEODRIVER" in os.environ and os.environ["SDL_VIDEODRIVER"] == "dummy":
        del os.environ["SDL_VIDEODRIVER"]
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    if not IS_HEADLESS:
        pygame.display.set_caption("Autism Shopping Assistant (Demo)")
    
    load_game_assets()
    
    if save_gif:
        print(f"Running simulation demo (Saving to {gif_name})...")
    else:
        print("Running simulation demo (Watch mode, no GIF)...")
    
    state = env.reset()
    done = False
    total_reward = 0
    frames = []

    # Draw initial frame at start position before any movement
    initial_action = ACTION_NONE
    initial_reward = 0
    draw_game_grid(screen, env)
    draw_guidance(screen, initial_action, env.child.position, env.target_pos)
    draw_ui(screen, env.steps, initial_action, initial_reward, total_reward, "")
    pygame.display.flip()

    if save_gif:
        frame = pygame.surfarray.array3d(screen)
        frame = frame.swapaxes(0, 1)
        frames.append(frame)
    else:
        clock = pygame.time.Clock()
        clock.tick(10)
    
    # Run loop
    steps = 0
    clock = pygame.time.Clock()
    
    while not done and steps < 100:
        steps += 1
        
        # Monitor quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                
        # AI Decision
        # Use greedy (no exploration) for demo
        original_eps = agent.epsilon
        agent.epsilon = 0 
        action = agent.choose_action(state)
        agent.epsilon = original_eps
        
        # Environment Step
        next_state, reward, done = env.step(action)
        total_reward += reward
        state = next_state
        
        # Draw Frame
        draw_game_grid(screen, env)
        draw_guidance(screen, action, env.child.position, env.target_pos)
        draw_ui(screen, env.steps, action, reward, total_reward, "")
        pygame.display.flip()
        
        # Capture Frame
        if save_gif:
            frame = pygame.surfarray.array3d(screen)
            frame = frame.swapaxes(0, 1) # Rotate
            frames.append(frame)
        else:
            clock.tick(10) # 10 FPS for watching
            
        # Always pump events to keep window responsive
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                done = True
 
            
    # Save GIF
    if save_gif and frames:
        print(f"Saving GIF with {len(frames)} frames...")
        imageio.mimsave(gif_name, frames, fps=5)
        print("Done.")
        
    pygame.quit()

def play_interactive_mode(agent, env):
    """
    Experimental Interactive Mode.
    Allows user to control the child with arrow keys.
    """
    print("Launching Interactive Mode...")
    
    # Try to ensure windowed mode works (if local display available)
    if "SDL_VIDEODRIVER" in os.environ:
        del os.environ["SDL_VIDEODRIVER"]
        
    pygame.init()
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Interactive Mode: Use Arrow Keys to Move Child")
    except pygame.error:
        print("Could not initialize display for interactive mode.")
        return

    load_game_assets()
    
    state = env.reset()
    done = False
    clock = pygame.time.Clock()
    total_reward = 0
    episodes_completed = 0
    total_steps_session = 0
    
    # Instructions
    print("\n--- Controls ---")
    print("Arrow Keys: Move Child")
    print("ESC: Quit | AI will provide hints automatically.")
    
    running = True
    display_message = ""
    message_timer = 0
    
    while running:
        # 1. AI Suggests Action based on current state
        agent.epsilon = 0 # Be helpful
        action = agent.choose_action(state)
        
        # 2. Handle User Input
        user_moved = False
        dx, dy = 0, 0
        new_event_msg = ""
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                elif event.key == pygame.K_UP: dy = -1
                elif event.key == pygame.K_DOWN: dy = 1
                elif event.key == pygame.K_LEFT: dx = -1
                elif event.key == pygame.K_RIGHT: dx = 1
                
        # Move Logic
        if dx != 0 or dy != 0:
            cx, cy = env.child.position
            nx, ny = cx + dx, cy + dy
            
            # Check bounds and obstacles
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if env.grid[ny][nx] == 0:
                    env.child.position = [nx, ny]
                    user_moved = True
                else:
                    new_event_msg = "Blocked!"
            else:
                 new_event_msg = "Wall!"
        
        # Message Timer Logic
        if new_event_msg:
            display_message = new_event_msg
            message_timer = 15 # Show for 15 frames (~1 sec)
        elif message_timer > 0:
            message_timer -= 1
        else:
            display_message = ""
            
        # 3. Step Logic
        step_reward = REWARD_STEP
        if tuple(env.child.position) == env.target_pos:
            step_reward += REWARD_GOAL
            display_message = "GOAL!"
            message_timer = 30
            # ... (Goal reached logic same as before)
            print("GOAL REACHED!")
            episodes_completed += 1
            
            # Show goal briefly
            draw_game_grid(screen, env, display_message)
            draw_guidance(screen, action, env.child.position, env.target_pos)
            draw_ui(screen, env.steps, action, step_reward, total_reward, "")
            pygame.display.flip()
            time.sleep(1.0)
            
            state = env.reset()
            # total_reward = 0  # Optional reset
            display_message = ""
        else:
            state = env.get_state()
            
        total_reward += step_reward
        if user_moved: total_steps_session += 1
        
        # 4. Draw
        draw_game_grid(screen, env, display_message)
        draw_guidance(screen, action, env.child.position, env.target_pos)
        draw_ui(screen, env.steps, action, step_reward, total_reward, "")
        pygame.display.flip()
        
        clock.tick(15) # Cap FPS

        
    # Show Summary
    show_summary_screen(screen, total_steps_session, total_reward, episodes_completed)
    pygame.quit()

def train_agent(agent, env, episodes=3000):
    rewards_history = []
    print(f"Training Agent for {episodes} episodes...")
    for episode in range(episodes):
        state = env.reset()
        done = False
        total = 0
        while not done:
            action = agent.choose_action(state)
            next_state, reward, done = env.step(action)
            agent.update(state, action, reward, next_state)
            state = next_state
            total += reward
        agent.decay_epsilon()
        rewards_history.append(total)
        
        if (episode+1) % 500 == 0:
            print(f"Episode {episode+1}: Reward {total}, Epsilon {agent.epsilon:.2f}")
            
    return rewards_history

def plot_learning(rewards):
    plt.figure(figsize=(10, 5))
    plt.plot(rewards)
    plt.title("Learning Curve")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    curve_file = output_path("learning_curve.png")
    plt.savefig(curve_file)
    print(f"Learning curve saved to {curve_file}.")

if __name__ == "__main__":
    env = SupermarketEnv()
    agent = QLearningAgent()
    cli_args = set(sys.argv[1:])
    
    # Check arguments
    if "--play" in cli_args or "-play" in cli_args or "-p" in cli_args:
        # Interactive Mode
        if os.path.exists("q_table.npy"):
            agent.load_model()
            play_interactive_mode(agent, env)
        else:
            print("No trained model found! Run 'python main.py' first to train.")
            
    elif "--watch" in cli_args or "-watch" in cli_args or "-w" in cli_args:
        # Watch Mode: show trained agent in a live window, no GIF saved
        if os.path.exists("q_table.npy"):
            agent.load_model()
            run_simulation_demo(agent, env, save_gif=False)
        else:
            print("No trained model found! Run 'python main.py' first to train.")

    elif "--demo" in cli_args or "-demo" in cli_args or "-d" in cli_args:
        # Demo Mode: regenerate GIF from existing model without retraining
        if os.path.exists("q_table.npy"):
            agent.load_model()
            print("Regenerating demo GIF from saved model...")
            run_simulation_demo(agent, env, save_gif=True, gif_name=output_path("trained_agent_demo.gif"))
        else:
            print("No trained model found! Run 'python main.py' first to train.")
            
    else:
        # Default: Train & Demo
        rewards = train_agent(agent, env)
        agent.save_model()
        plot_learning(rewards) # Save plot
        
        # Generate Demo GIF with new visuals
        run_simulation_demo(agent, env, save_gif=True, gif_name=output_path("trained_agent_demo.gif"))

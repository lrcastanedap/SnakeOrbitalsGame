import pygame
import sys
import random

# --- Initialization ---
pygame.init()

# --- Constants ---

# Screen dimensions
GAME_WIDTH = 720
GAME_HEIGHT = 720
UI_WIDTH = 280
SCREEN_WIDTH = GAME_WIDTH + UI_WIDTH
SCREEN_HEIGHT = GAME_HEIGHT

GRID_SIZE = 30
GRID_W = GAME_WIDTH // GRID_SIZE
GRID_H = GAME_HEIGHT // GRID_SIZE

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (0, 200, 0)         # Snake
COLOR_ORBITAL_CORRECT = (0, 255, 255) # Cyan
COLOR_ORBITAL_WRONG = (255, 165, 0) # Orange
COLOR_ELECTRON_UP = (255, 0, 0)   # Red (Pair Up)
COLOR_ELECTRON_DOWN = (0, 0, 255) # Blue (Pair Down)
COLOR_UI_BG = (30, 30, 30)
COLOR_GRID = (40, 40, 40)
COLOR_PENALTY = (255, 0, 0)
COLOR_REWARD = (0, 255, 0)

# Game settings
FPS = 10

# --- Game Data ---

# Aufbau principle order
ORBITAL_ORDER = [
    "1s", "2s", "2p", "3s", "3p", "4s", "3d", "4p", "5s", "4d", "5p", 
    "6s", "4f", "5d", "6p", "7s", "5f", "6d", "7p"
]

# Max electrons (spin up, spin down) for each orbital type
# This implements Pauli Exclusion and Hund's Rule (fill up first)
ORBITAL_CAPACITIES = {
    's': {'max_up': 1, 'max_down': 1},
    'p': {'max_up': 3, 'max_down': 3},
    'd': {'max_up': 5, 'max_down': 5},
    'f': {'max_up': 7, 'max_down': 7},
}

# --- Screen and Font Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Orbital Snake")
clock = pygame.time.Clock()

font_large = pygame.font.SysFont('consolas', 30)
font_medium = pygame.font.SysFont('consolas', 20)
font_small = pygame.font.SysFont('consolas', 16)
font_micro = pygame.font.SysFont('arial', 20) # For arrows

# --- Game State Variables ---
game_state = {
    "score": 0,
    "orbitals_eaten_count": 0,
    "current_orbital_index": 0,
    "is_filling": False,
    "current_filling_orbital": None,
    "max_up": 0,
    "max_down": 0,
    "filling_up": 0,
    "filling_down": 0,
    "game_over": False,
    "win": False,
    "last_message": None,
    "message_timer": 0
}

# --- Helper Functions ---

def get_random_grid_pos(occupied_positions):
    """Gets a random grid position not occupied by the snake."""
    while True:
        pos = (
            random.randint(0, GRID_W - 1) * GRID_SIZE,
            random.randint(0, GRID_H - 1) * GRID_SIZE
        )
        if pos not in occupied_positions:
            return pos

def spawn_orbital_set(snake_body):
    """Spawns one correct orbital and two incorrect ones."""
    orbitals = []
    occupied = list(snake_body)
    
    # 1. Spawn Correct Orbital
    correct_orbital = ORBITAL_ORDER[game_state["current_orbital_index"]]
    pos = get_random_grid_pos(occupied)
    orbitals.append({"pos": pos, "name": correct_orbital, "type": "correct"})
    occupied.append(pos)
    
    # 2. Spawn Two Incorrect Orbitals
    for _ in range(2):
        while True:
            incorrect_orbital = random.choice(ORBITAL_ORDER)
            if incorrect_orbital != correct_orbital:
                break
        pos = get_random_grid_pos(occupied)
        orbitals.append({"pos": pos, "name": incorrect_orbital, "type": "wrong"})
        occupied.append(pos)
        
    return orbitals

def spawn_electron_set(snake_body):
    """Spawns two 'UP' and two 'DOWN' electrons."""
    electrons = []
    occupied = list(snake_body)
    
    for _ in range(2):
        pos_up = get_random_grid_pos(occupied)
        electrons.append({"pos": pos_up, "spin": "UP"})
        occupied.append(pos_up)
        
        pos_down = get_random_grid_pos(occupied)
        electrons.append({"pos": pos_down, "spin": "DOWN"})
        occupied.append(pos_down)
        
    return electrons

def respawn_item(item, snake_body, all_items):
    """Respawns a single item in a new valid location."""
    occupied = list(snake_body)
    for other_item in all_items:
        occupied.append(other_item["pos"])
        
    item["pos"] = get_random_grid_pos(occupied)

def reset_orbital_fill():
    """Resets the counters for filling an orbital."""
    game_state["filling_up"] = 0
    game_state["filling_down"] = 0

def set_flash_message(text, color, duration=FPS * 0.5):
    """Sets a temporary message to flash on the UI."""
    game_state["last_message"] = {"text": text, "color": color}
    game_state["message_timer"] = duration

def handle_electron_eat(spin_type):
    """Applies chemistry rules for eating an electron."""
    orbital_type = game_state["current_filling_orbital"][1] # 's', 'p', 'd', or 'f'
    max_up = game_state["max_up"]
    max_down = game_state["max_down"]
    
    reset_needed = False
    
    # For 's' orbitals, order doesn't matter (Pauli)
    if orbital_type == 's':
        if spin_type == "UP":
            if game_state["filling_up"] < max_up:
                game_state["filling_up"] += 1
            else:
                reset_needed = True # Tried to add > 1 'UP'
        elif spin_type == "DOWN":
            if game_state["filling_down"] < max_down:
                game_state["filling_down"] += 1
            else:
                reset_needed = True # Tried to add > 1 'DOWN'
                
    # For 'p', 'd', 'f', Hund's Rule applies (fill UP spins first)
    else:
        if spin_type == "UP":
            if game_state["filling_up"] < max_up:
                game_state["filling_up"] += 1
            else:
                reset_needed = True # Tried to add > max 'UP'
        elif spin_type == "DOWN":
            if game_state["filling_up"] < max_up:
                reset_needed = True # Must fill all UP spins first
            elif game_state["filling_down"] < max_down:
                game_state["filling_down"] += 1
            else:
                reset_needed = True # Tried to add > max 'DOWN'

    # Process results
    if reset_needed:
        game_state["score"] -= 10
        reset_orbital_fill()
        set_flash_message("-10 (Pairing Error)", COLOR_PENALTY)
    
    # Check for completion
    elif game_state["filling_up"] == max_up and game_state["filling_down"] == max_down:
        game_state["score"] += 15
        set_flash_message("+15 (Orbital Full!)", COLOR_REWARD)
        game_state["is_filling"] = False
        game_state["current_orbital_index"] += 1
        
        # Check for win
        if game_state["current_orbital_index"] >= len(ORBITAL_ORDER):
            game_state["win"] = True
            game_state["game_over"] = True
        else:
            # Spawn next set of orbitals
            global orbitals
            orbitals = spawn_orbital_set(snake_body)

# --- Drawing Functions ---

def draw_grid():
    """Draws the game grid."""
    for x in range(0, GAME_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, GAME_HEIGHT))
    for y in range(0, GAME_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, COLOR_GRID, (0, y), (GAME_WIDTH, y))

def draw_snake(snake_body):
    """Draws the snake."""
    for i, segment in enumerate(snake_body):
        rect = pygame.Rect(segment[0], segment[1], GRID_SIZE, GRID_SIZE)
        # Head is a brighter green
        color = (0, 255, 0) if i == 0 else COLOR_GREEN
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, COLOR_GRID, rect, 1) # Border

def draw_food(orbitals, electrons):
    """Draws all orbitals and electrons."""
    # Draw Orbitals (if not filling)
    if not game_state["is_filling"]:
        for orb in orbitals:
            rect = pygame.Rect(orb["pos"][0], orb["pos"][1], GRID_SIZE, GRID_SIZE)
            color = COLOR_ORBITAL_CORRECT if orb["type"] == "correct" else COLOR_ORBITAL_WRONG
            pygame.draw.ellipse(screen, color, rect)
            
            # Draw text on orbital
            text_surf = font_small.render(orb["name"], True, COLOR_BLACK)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

    # Draw Electrons (always on screen)
    for elec in electrons:
        rect = pygame.Rect(elec["pos"][0], elec["pos"][1], GRID_SIZE, GRID_SIZE)
        if elec["spin"] == "UP":
            color = COLOR_ELECTRON_UP
            symbol = "↑"
        else:
            color = COLOR_ELECTRON_DOWN
            symbol = "↓"
            
        pygame.draw.rect(screen, color, rect, border_radius=5)
        
        # Draw symbol
        sym_surf = font_micro.render(symbol, True, COLOR_WHITE)
        sym_rect = sym_surf.get_rect(center=rect.center)
        screen.blit(sym_surf, sym_rect)

def draw_ui():
    """Draws the information panel on the right."""
    ui_rect = pygame.Rect(GAME_WIDTH, 0, UI_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, COLOR_UI_BG, ui_rect)
    
    # Title
    title_surf = font_large.render("Orbital Snake", True, COLOR_WHITE)
    screen.blit(title_surf, (GAME_WIDTH + 20, 20))
    
    # Score
    score_surf = font_medium.render(f"Score: {game_state['score']}", True, COLOR_WHITE)
    screen.blit(score_surf, (GAME_WIDTH + 20, 80))
    
    # Orbitals Eaten
    eaten_surf = font_medium.render(f"Orbitals Eaten: {game_state['orbitals_eaten_count']}", True, COLOR_WHITE)
    screen.blit(eaten_surf, (GAME_WIDTH + 20, 110))
    
    pygame.draw.line(screen, COLOR_WHITE, (GAME_WIDTH + 20, 150), (SCREEN_WIDTH - 20, 150), 1)

    # Current Objective
    obj_title_surf = font_medium.render("Objective:", True, COLOR_WHITE)
    screen.blit(obj_title_surf, (GAME_WIDTH + 20, 170))
    
    if game_state["is_filling"]:
        # Show filling status
        name = game_state["current_filling_orbital"]
        obj_surf = font_medium.render(f"Fill {name}", True, COLOR_ORBITAL_CORRECT)
        screen.blit(obj_surf, (GAME_WIDTH + 40, 200))
        
        # Draw filling visualization (e.g., "p: [↑][↑][ ] [↓][ ][ ]")
        vis_y = 240
        orbital_type = name[1]
        max_up = game_state['max_up']
        
        up_text = "↑ " * game_state['filling_up'] + "· " * (max_up - game_state['filling_up'])
        down_text = "↓ " * game_state['filling_down'] + "· " * (max_up - game_state['filling_down'])
        
        up_surf = font_medium.render(up_text, True, COLOR_ELECTRON_UP)
        down_surf = font_medium.render(down_text, True, COLOR_ELECTRON_DOWN)
        
        screen.blit(up_surf, (GAME_WIDTH + 40, vis_y))
        screen.blit(down_surf, (GAME_WIDTH + 40, vis_y + 30))
        
    else:
        # Show orbital to find
        name = ORBITAL_ORDER[game_state["current_orbital_index"]]
        obj_surf = font_medium.render(f"Find {name}", True, COLOR_ORBITAL_CORRECT)
        screen.blit(obj_surf, (GAME_WIDTH + 40, 200))

    # Flash Message
    if game_state["message_timer"] > 0:
        msg = game_state["last_message"]
        msg_surf = font_medium.render(msg["text"], True, msg["color"])
        screen.blit(msg_surf, (GAME_WIDTH + 20, 350))
        game_state["message_timer"] -= 1
        
    # Controls
    controls_y = SCREEN_HEIGHT - 100
    ctrl_title = font_small.render("Controls:", True, COLOR_WHITE)
    ctrl_keys = font_small.render("Arrow Keys or W/A/S/D", True, COLOR_WHITE)
    screen.blit(ctrl_title, (GAME_WIDTH + 20, controls_y))
    screen.blit(ctrl_keys, (GAME_WIDTH + 20, controls_y + 25))

def draw_game_over(win=False):
    """Displays the game over or win screen."""
    overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    if win:
        text = "YOU WIN! Electron Master!"
        color = (0, 255, 128)
    else:
        text = "GAME OVER"
        color = (255, 0, 0)
        
    text_surf = font_large.render(text, True, color)
    text_rect = text_surf.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 40))
    screen.blit(text_surf, text_rect)
    
    score_surf = font_medium.render(f"Final Score: {game_state['score']}", True, COLOR_WHITE)
    score_rect = score_surf.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 10))
    screen.blit(score_surf, score_rect)
    
    restart_surf = font_medium.render("Press 'R' to Restart", True, COLOR_WHITE)
    restart_rect = restart_surf.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 60))
    screen.blit(restart_surf, restart_rect)


# --- Game Setup ---
snake_pos = (GAME_WIDTH // 2, GAME_HEIGHT // 2)
snake_body = [snake_pos, 
              (snake_pos[0] - GRID_SIZE, snake_pos[1]), 
              (snake_pos[0] - (2 * GRID_SIZE), snake_pos[1])]
direction = "RIGHT"
change_to = direction

# Spawn initial food
orbitals = spawn_orbital_set(snake_body)
electrons = spawn_electron_set(snake_body)

# --- Main Game Loop ---
while True:
    
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if not game_state["game_over"]:
                if event.key in (pygame.K_UP, pygame.K_w):
                    change_to = "UP"
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    change_to = "DOWN"
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    change_to = "LEFT"
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    change_to = "RIGHT"
            else:
                if event.key == pygame.K_r:
                    # Reset game
                    game_state = {
                        "score": 0, "orbitals_eaten_count": 0, "current_orbital_index": 0,
                        "is_filling": False, "current_filling_orbital": None,
                        "max_up": 0, "max_down": 0, "filling_up": 0, "filling_down": 0,
                        "game_over": False, "win": False,
                        "last_message": None, "message_timer": 0
                    }
                    snake_pos = (GAME_WIDTH // 2, GAME_HEIGHT // 2)
                    snake_body = [snake_pos, 
                                  (snake_pos[0] - GRID_SIZE, snake_pos[1]), 
                                  (snake_pos[0] - (2 * GRID_SIZE), snake_pos[1])]
                    direction = "RIGHT"
                    change_to = direction
                    orbitals = spawn_orbital_set(snake_body)
                    electrons = spawn_electron_set(snake_body)

    if game_state["game_over"]:
        # Keep drawing screen but don't update logic
        draw_game_over(game_state["win"])
        pygame.display.flip()
        clock.tick(FPS)
        continue

    # --- Game Logic ---
    
    # Validate direction change (prevent 180-degree turn)
    if change_to == "UP" and direction != "DOWN":
        direction = "UP"
    if change_to == "DOWN" and direction != "UP":
        direction = "DOWN"
    if change_to == "LEFT" and direction != "RIGHT":
        direction = "LEFT"
    if change_to == "RIGHT" and direction != "LEFT":
        direction = "RIGHT"

    # Move snake head
    if direction == "UP":
        snake_pos = (snake_pos[0], snake_pos[1] - GRID_SIZE)
    if direction == "DOWN":
        snake_pos = (snake_pos[0], snake_pos[1] + GRID_SIZE)
    if direction == "LEFT":
        snake_pos = (snake_pos[0] - GRID_SIZE, snake_pos[1])
    if direction == "RIGHT":
        snake_pos = (snake_pos[0] + GRID_SIZE, snake_pos[1])

    # Insert new head
    snake_body.insert(0, snake_pos)
    grew_this_frame = False

    # --- Collision Detection ---
    
    # Game Over: Wall collision
    if (snake_pos[0] < 0 or snake_pos[0] >= GAME_WIDTH or 
        snake_pos[1] < 0 or snake_pos[1] >= GAME_HEIGHT):
        game_state["game_over"] = True
    
    # Game Over: Self collision
    for segment in snake_body[1:]:
        if snake_pos == segment:
            game_state["game_over"] = True
            
    if game_state["game_over"]:
        continue # Skip rest of loop if dead

    # Food Collision
    all_items = electrons
    if not game_state["is_filling"]:
        all_items = all_items + orbitals

    # Check for Orbital collision (only if we are NOT filling)
    if not game_state["is_filling"]:
        eaten_orbital = None
        for orb in orbitals:
            if snake_pos == orb["pos"]:
                eaten_orbital = orb
                break
        
        if eaten_orbital:
            grew_this_frame = True
            game_state["orbitals_eaten_count"] += 1
            
            if eaten_orbital["type"] == "correct":
                # CORRECT ORBITAL
                game_state["is_filling"] = True
                name = eaten_orbital["name"]
                game_state["current_filling_orbital"] = name
                
                # Set up filling parameters
                type_char = name[1]
                caps = ORBITAL_CAPACITIES[type_char]
                game_state["max_up"] = caps['max_up']
                game_state["max_down"] = caps['max_down']
                reset_orbital_fill()
                
                set_flash_message(f"Find {name}!", COLOR_REWARD)
                orbitals.clear() # Remove all orbitals from screen
                
            else:
                # WRONG ORBITAL
                game_state["score"] -= 10
                set_flash_message("-10 (Wrong Orbital)", COLOR_PENALTY)
                # Respawn just the one orbital that was eaten
                all_food_for_respawn = snake_body + [o['pos'] for o in orbitals if o != eaten_orbital] + [e['pos'] for e in electrons]
                
                # Replace it with a new random WRONG one
                correct_orbital = ORBITAL_ORDER[game_state["current_orbital_index"]]
                while True:
                    eaten_orbital["name"] = random.choice(ORBITAL_ORDER)
                    if eaten_orbital["name"] != correct_orbital:
                        break
                eaten_orbital["pos"] = get_random_grid_pos(all_food_for_respawn)
        
    # Check for Electron collision
    eaten_electron = None
    for elec in electrons:
        if snake_pos == elec["pos"]:
            eaten_electron = elec
            break
            
    if eaten_electron:
        grew_this_frame = True
        
        if game_state["is_filling"]:
            # CORRECT: We are filling and we ate an electron
            handle_electron_eat(eaten_electron["spin"])
        else:
            # PENALTY: Ate electron when we should be finding an orbital
            game_state["score"] -= 10
            set_flash_message("-10 (Must eat orbital first!)", COLOR_PENALTY)
        
        # Respawn the eaten electron
        all_food_for_respawn = snake_body + [e['pos'] for e in electrons if e != eaten_electron]
        if not game_state["is_filling"]:
             all_food_for_respawn += [o['pos'] for o in orbitals]
        
        eaten_electron["pos"] = get_random_grid_pos(all_food_for_respawn)

    # --- Update Snake Body ---
    if not grew_this_frame:
        snake_body.pop() # Remove tail if we didn't eat

    # --- Drawing ---
    screen.fill(COLOR_BLACK)
    
    # Draw game area
    draw_grid()
    draw_snake(snake_body)
    draw_food(orbitals, electrons)
    
    # Draw UI
    draw_ui()
    
    # Update display
    pygame.display.flip()
    
    # Cap FPS
    clock.tick(FPS)
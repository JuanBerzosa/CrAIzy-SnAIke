# Instructions to Create the Snake Game

## Game Description

This project involves implementing the classic Snake game in a terminal environment using Python and the curses library. In this game, the player controls a continuously moving snake on the screen. The goal is to eat as much food as possible to increase the score and the size of the snake, while avoiding collisions with the walls or the snake’s own body.

## Game Features

1. **Colorful Snake**:
- Each segment of the snake has a color based on the value of the food consumed.
- The snake's head displays a directional indicator (>, v, <, ^) according to the movement direction.

2. **Advanced Food System**:
- Foods with different numerical values (represented by numbers).
- Countdown timers (3-9 seconds) for each piece of food.
- Food disappears and reappears in new locations when the timer expires.

3. **Movement Mechanics**:
- Control via arrow keys.
- Speed increases when pressing the arrow key that matches the current direction of the snake’s movement.
- Realistic physics for snake movement.

4. **Scoring System**:
- Score tracking based on the food consumed.
- Game over screen with the final score.
- Option to restart the game after losing.

5. **Sound Effects**:
- Sounds for collision and food consumption using winsound (for Windows).

6. **Collision Detection**:
- Collision with the edges of the play area.
- Collision with the snake’s own body.

## Step-by-Step Implementation Instructions

### Step 1: Initial Setup

1. Import the necessary libraries:
```python
import curses
import random
import time
import winsound  # For sound effects on Windows
import copy
```

2. Initialize the curses environment:
```python
stdscr = curses.initscr()
curses.start_color()
curses.use_default_colors()
curses.curs_set(0)
sh, sw = stdscr.getmaxyx()
w = curses.newwin(sh, sw, 0, 0)
w.keypad(1)
w.timeout(100)  # Refresh every 100ms
```

3. Define the colors for the game:
```python
for i in range(1, 8):
    curses.init_pair(i, i, -1)
```

### Step 2: Game Variable Initialization

1. Set up the initial snake:
```python
snake_x = sw // 4
snake_y = sh // 2
snake = [
    [snake_y, snake_x],
    [snake_y, snake_x - 1],
    [snake_y, snake_x - 2]
]
snake_colors = [1, 1, 1]  # Initial colors for segments
```

2. Define the initial direction:
```python
direction = curses.KEY_RIGHT
last_direction = direction
direction_chars = {
    curses.KEY_UP: '^',
    curses.KEY_DOWN: 'v',
    curses.KEY_LEFT: '<',
    curses.KEY_RIGHT: '>'
}
```

3. Set up the initial food:
```python
foods = []
food_values = list(range(1, 10))
create_new_food(w, snake, foods, sh, sw, food_values)  # Function to implement
```

### Step 3: Main Game Loop

```python
score = 0
speed_increase = 1.0
same_direction_count = 0
game_over = False

while not game_over:
    # Get user input
    next_key = w.getch()
    
    # Update direction
    if next_key in [curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_UP, curses.KEY_DOWN]:
        if (next_key == curses.KEY_RIGHT and last_direction != curses.KEY_LEFT) or \
        (next_key == curses.KEY_LEFT and last_direction != curses.KEY_RIGHT) or \
        (next_key == curses.KEY_UP and last_direction != curses.KEY_DOWN) or \
        (next_key == curses.KEY_DOWN and last_direction != curses.KEY_UP):
            direction = next_key
    
    # Increase speed if moving in the same direction
    if direction == last_direction:
        same_direction_count += 1
        if same_direction_count > 5:
            speed_increase = min(2.0, 1.0 + same_direction_count * 0.05)
    else:
        same_direction_count = 0
        speed_increase = 1.0
    
    last_direction = direction
    
    # Update snake position
    new_head = [snake[0][0], snake[0][1]]
    
    if direction == curses.KEY_DOWN:
        new_head[0] += 1
    if direction == curses.KEY_UP:
        new_head[0] -= 1
    if direction == curses.KEY_LEFT:
        new_head[1] -= 1
    if direction == curses.KEY_RIGHT:
        new_head[1] += 1
    
    snake.insert(0, new_head)
    
    # Check for collisions
    if (
        new_head[0] in [0, sh-1] or 
        new_head[1] in [0, sw-1] or 
        new_head in snake[1:]
    ):
        game_over = True
        winsound.Beep(200, 200)  # Collision sound
        continue
    
    # Check if the snake eats food
    for i, food in enumerate(foods):
        if snake[0] == food["pos"]:
            score += food["value"]
            snake_colors.insert(0, food["value"] % 7 + 1)  # Assign color based on the value
            winsound.Beep(500, 100)  # Eating sound
            foods.pop(i)
            create_new_food(w, snake, foods, sh, sw, food_values)
            break
    else:
        # If no food is eaten, remove the last segment
        tail = snake.pop()
        snake_colors.pop()
        w.addch(tail[0], tail[1], ' ')
    
    # Update food timers and recreate if necessary
    for i in range(len(foods) - 1, -1, -1):
        foods[i]["time"] -= 0.1
        if foods[i]["time"] <= 0:
            pos = foods[i]["pos"]
            w.addch(pos[0], pos[1], ' ')
            foods.pop(i)
            create_new_food(w, snake, foods, sh, sw, food_values)
    
    # Draw the snake
    w.addch(snake[0][0], snake[0][1], direction_chars[direction], curses.color_pair(snake_colors[0]))
    for i in range(1, len(snake)):
        w.addch(snake[i][0], snake[i][1], '#', curses.color_pair(snake_colors[i]))
    
    # Draw food
    for food in foods:
        w.addch(food["pos"][0], food["pos"][1], str(food["value"]), curses.A_BOLD)
    
    # Show score
    w.addstr(0, sw // 2 - 10, f"Score: {score}", curses.A_BOLD)
    
    # Set timeout for the next iteration (adjusted by speed)
    w.timeout(int(100 / speed_increase))
```

### Step 4: Helper Functions

1. Create new food:
```python
def create_new_food(w, snake, foods, sh, sw, food_values):
    if len(foods) >= 5:  # Limit the number of food items on the screen
        return
    
    while True:
        food_y = random.randint(1, sh - 2)
        food_x = random.randint(1, sw - 2)
        
        # Ensure food does not appear on the snake
        if [food_y, food_x] not in snake and not any(food["pos"] == [food_y, food_x] for food in foods):
            value = random.choice(food_values)
            food_time = random.uniform(3, 9)  # Timer between 3 and 9 seconds
            foods.append({
                "pos": [food_y, food_x],
                "value": value,
                "time": food_time
            })
            break
```

2. Show game over screen:
```python
def show_game_over(w, sh, sw, score):
    w.clear()
    message = "GAME OVER!"
    w.addstr(sh // 2 - 2, sw // 2 - len(message) // 2, message, curses.A_BOLD)
    
    score_msg = f"Final Score: {score}"
    w.addstr(sh // 2, sw // 2 - len(score_msg) // 2, score_msg)
    
    restart_msg = "Press 'r' to restart or 'q' to quit"
    w.addstr(sh // 2 + 2, sw // 2 - len(restart_msg) // 2, restart_msg)
    
    w.refresh()
    
    while True:
        key = w.getch()
        if key == ord('r'):
            return True  # Restart
        elif key == ord('q'):
            return False  # Quit
```

### Step 5: Handling Restart and Exit

```python
try:
    while True:
        # Initialize game variables
        snake_x = sw // 4
        snake_y = sh // 2
        snake = [
            [snake_y, snake_x],
            [snake_y, snake_x - 1],
            [snake_y, snake_x - 2]
        ]
        snake_colors = [1, 1, 1]
        direction = curses.KEY_RIGHT
        last_direction = direction
        foods = []
        score = 0
        
        # Start game
        w.clear()
        w.border
```

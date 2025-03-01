#!/usr/bin/env python3
import curses
import random
import time
import winsound  # For playing sound on Windows

def generate_food(stdscr, snake, foods):
    screen_height, screen_width = stdscr.getmaxyx()
    # Ensure we stay well within bounds to avoid issues
    # Generate random position (avoiding borders)
    # Use sh-3 and sw-3 to add extra safety margin from borders
    food_y = random.randint(1, screen_height-3)
    food_x = random.randint(1, screen_width-3)
    # Generate random countdown value between 3 and 9
    counter = random.randint(3, 9)
    # Make sure food isn't on the snake or other food items
    if (food_y, food_x) not in [(s[0], s[1]) for s in snake] and \
    (food_y, food_x) not in [(f[0], f[1]) for f in foods]:
        return (food_y, food_x, counter, time.time())

def game_over(stdscr, score):
    screen_height, screen_width = stdscr.getmaxyx()
    stdscr.clear()
    
    game_over_text = "GAME OVER!"
    score_text = f"Final Score: {score}"
    restart_text = "Press 'r' to restart or 'q' to quit"
    
    try:
        stdscr.addstr(screen_height//2-2, screen_width//2-len(game_over_text)//2, game_over_text, curses.color_pair(11) | curses.A_BOLD)
        stdscr.addstr(screen_height//2, screen_width//2-len(score_text)//2, score_text)
        stdscr.addstr(screen_height//2+2, screen_width//2-len(restart_text)//2, restart_text)
    except curses.error:
        # Handle potential error when writing game over text
        pass
    
    stdscr.refresh()
    
    # Wait for restart or quit
    while True:
        key = stdscr.getch()
        if key == ord('r'):
            init_game(stdscr)
            return
        elif key == ord('q'):
            return

def init_game(stdscr):
    # Setup
    stdscr.clear()  # Clear the screen completely before starting a new game
    stdscr.refresh()  # Refresh to show the cleared screen
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(50)  # Faster refresh rate (50ms instead of 150ms)
    stdscr.nodelay(True)  # Non-blocking input
    screen_height, screen_width = stdscr.getmaxyx()  # Screen height and width
    
    # Colors
    curses.start_color()
    # Define color pairs for snake segments based on food values
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)     # Value 1
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # Value 2
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)      # Value 3
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Value 4
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)      # Value 5
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Value 6
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)       # Value 7
    curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLUE)      # Value 8 (unique)
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_GREEN)     # Value 9 (unique)
    # Special color pairs
    curses.init_pair(10, curses.COLOR_RED, curses.COLOR_BLACK)      # Food
    curses.init_pair(11, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Text/UI elements
    
    # Create border
    stdscr.border(0)
    stdscr.refresh()
    
    # Initialize snake position
    snake_head_y = screen_height // 2
    snake_head_x = screen_width // 2
    
    # Initialize snake as a list of (y, x, color_pair) tuples
    # Start with a snake of length 3
    snake = [
        (snake_head_y, snake_head_x, 1),
        (snake_head_y, snake_head_x - 1, 1),
        (snake_head_y, snake_head_x - 2, 1)
    ]
    
    # Draw initial snake
    for segment in snake:
        try:
            stdscr.addch(segment[0], segment[1], curses.ACS_BLOCK, curses.color_pair(segment[2]))
        except curses.error:
            pass
    
    # Initial direction ('right', 'down', 'left', 'up')
    direction = 'right'
    # Direction character mapping for snake head
    dir_chars = {'right': '>', 'down': 'v', 'left': '<', 'up': '^'}
    
    # Generate multiple food items
    foods = []
    max_foods = 1  # Only one food item at a time
    for _ in range(max_foods):
        new_food = generate_food(stdscr, snake, foods)
        if new_food:
            foods.append(new_food)
            try:
                stdscr.addch(new_food[0], new_food[1], str(new_food[2]), curses.color_pair(10))
            except curses.error:
                pass
    
    # Initial score
    score = 0

    # Make score accessible within nested functions
    nonlocal_dict = {'score': score}

    # Timing variables
    last_move_time = time.time()
    last_food_update_time = time.time()
    move_delay = 0.07  # Faster movement (was ~0.1)
    base_move_delay = 0.07  # The starting move delay value
    last_direction_change = time.time()
    same_direction_start_time = time.time()  # Track when snake started moving in current direction
    direction_change_delay = 0.05  # Minimum time between direction changes
    buffered_key = None  # Store the last pressed key

    # Variables for increasing speed when direction key is held down
    min_move_delay = 0.03  # Minimum threshold for move_delay
    max_speed_increase_time = 2.0  # Time (in seconds) to reach maximum speed

    # Game loop
    while True:
        # Display score
        # Display score
        score_text = f"Score: {nonlocal_dict['score']}"
        try:
            stdscr.addstr(0, screen_width//2 - len(score_text)//2, score_text, curses.color_pair(11))
        except curses.error:
            pass
            
        # Check for key presses (non-blocking)
        key = stdscr.getch()

        # Store the key if it's a valid input
        if key != -1:  # -1 means no key was pressed
            if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT, ord('q')]:
                buffered_key = key
                buffered_key = key
        # Process the buffered key when enough time has passed
        current_time = time.time()
        if buffered_key is not None and current_time - last_direction_change >= direction_change_delay:
            old_direction = direction
            if buffered_key == curses.KEY_UP and direction != 'down':
                direction = 'up'
                last_direction_change = current_time
            elif buffered_key == curses.KEY_DOWN and direction != 'up':
                direction = 'down'
                last_direction_change = current_time
            elif buffered_key == curses.KEY_LEFT and direction != 'right':
                direction = 'left'
                last_direction_change = current_time
            elif buffered_key == curses.KEY_RIGHT and direction != 'left':
                direction = 'right'
                last_direction_change = current_time
            
            # Reset the same_direction_start_time if direction has changed
            if old_direction != direction:
                same_direction_start_time = current_time
            elif buffered_key == ord('q'):
                break
            buffered_key = None  # Clear the buffer after processing

        # Update food countdown every second
        current_time = time.time()
        if current_time - last_food_update_time >= 1.0:
            last_food_update_time = current_time
            # Decrease counter for each food
            for i in range(len(foods)-1, -1, -1):  # Iterate backwards to safely remove items
                y, x, counter, _ = foods[i]
                counter -= 1
                # Play sound when food timer decreases
                winsound.Beep(800, 100)  # 800Hz frequency, 100ms duration
                if counter <= 0:
                    # Remove food that reached 0
                    try:
                        stdscr.addch(y, x, ' ')  # Clear the food
                    except curses.error:
                        pass
                    foods.pop(i)
                    # Generate a replacement food if below max
                    if len(foods) < max_foods:
                        new_food = generate_food(stdscr, snake, foods)
                        if new_food:
                            foods.append(new_food)
                            try:
                                stdscr.addch(new_food[0], new_food[1], str(new_food[2]), curses.color_pair(10))
                            except curses.error:
                                pass
                else:
                    # Update the counter display
                    foods[i] = (y, x, counter, foods[i][3])
                    try:
                        stdscr.addch(y, x, str(counter), curses.color_pair(10))
                    except curses.error:
                        pass

        # Only move the snake according to move_delay
        if current_time - last_move_time < move_delay:
            stdscr.refresh()
            continue

        # Calculate how long we've been moving in the same direction
        direction_duration = current_time - same_direction_start_time

        # Adjust move_delay based on direction duration (gradually increase speed)
        # Formula creates smooth speedup over time until max_speed_increase_time is reached
        speed_factor = min(direction_duration / max_speed_increase_time, 1.0)
        move_delay = max(base_move_delay - (base_move_delay - min_move_delay) * speed_factor, min_move_delay)

        # Update move time
        last_move_time = current_time
        # Calculate new head position
        head_y, head_x, _ = snake[0]
        if direction == 'right':
            head_x += 1
        elif direction == 'down':
            head_y += 1
        elif direction == 'left':
            head_x -= 1
        elif direction == 'up':
            head_y -= 1
        
        # Check for collision with walls
        if head_y <= 0 or head_y >= screen_height-1 or head_x <= 0 or head_x >= screen_width-1:
            game_over(stdscr, nonlocal_dict['score'])
            return
        
        # Check for collision with self
        if (head_y, head_x) in [(s[0], s[1]) for s in snake]:
            game_over(stdscr, nonlocal_dict['score'])
            return
        
        # Check if snake eats any food
        food_eaten = False
        for i in range(len(foods)-1, -1, -1):
            if head_y == foods[i][0] and head_x == foods[i][1]:
                # Increase score
                nonlocal_dict['score'] += foods[i][2]
                
                # Add new head with food value color
                # Add new head with food value color
                food_color = min(foods[i][2], 9)  # Limit to defined color pairs
                snake.insert(0, (head_y, head_x, food_color))
                # Remove eaten food
                foods.pop(i)
                
                # Generate new food
                new_food = generate_food(stdscr, snake, foods)
                if new_food:
                    foods.append(new_food)
                    try:
                        stdscr.addch(new_food[0], new_food[1], str(new_food[2]), curses.color_pair(10))
                    except curses.error:
                        pass
                
                food_eaten = True
                break
        if not food_eaten:
            # Move snake: add new head, remove tail
            snake.insert(0, (head_y, head_x, snake[0][2]))
            tail = snake.pop()
            try:
                stdscr.addch(tail[0], tail[1], ' ')
            except curses.error:
                pass
        
        # Draw new head
        # Draw new head with direction indicator
        try:
            head_char = dir_chars[direction]  # Get directional character for head
            stdscr.addch(head_y, head_x, head_char, curses.color_pair(snake[0][2]))
        except curses.error:
            pass
        # Refresh screen
        # Refresh screen
        stdscr.refresh()

def main(stdscr):
    # Initialize and start the game
    init_game(stdscr)

# Start the game using curses wrapper
if __name__ == "__main__":
    curses.wrapper(main)

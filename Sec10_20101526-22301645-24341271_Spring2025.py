
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

player2_pos = [-540, -540, 80]  
player2_angle = 0
player2_current_cell = 1
player2_dice_value = 1
player2_dice_rolling = False
player2_last_roll_time = 0
player2_roll_duration = 0
player2_target_cell = 1
player2_moving_to_target = False
player2_move_start_time = 0
player2_move_duration = 1.0
player2_move_start_pos = None
player2_game_score = 0
current_player = 1  # Track turns 

reward_angle = 0  
reward_color = [1.0, 0.8, 0.0]  # Gold 
reward_spin_speed = 90  # 90degree ps

player1_health = 5  
player2_health = 5  
max_health = 5  
health_bar_width = 100  
health_bar_height = 15  

#snake properties
snake_visible = False  
snake_points = []
snake_target_points = []
snake_head_pos = [-600, -600] #bottom left corner theke enters
snake_direction = [1, 0]  
snake_base_speed = 150  
snake_speed = snake_base_speed  
snake_base_length = 25 
snake_length = snake_base_length  
snake_segment_length = 30  
snake_last_move_time = time.time()
snake_move_interval = 0.05  # Time between snake updates
snake_color = [0.5, 0.0, 0.8]  
snake_growth_interval = 5 
snake_speed_increase_interval = 2 
snake_speed_multiplier = 1.0 
last_snake_growth_time = time.time()  
last_speed_increase_time = time.time()  

camera_position = [0, 0, 800] 
camera_target = [0, 0, 0]      
camera_angle_x = 0             
camera_angle_y = 30            
camera_distance = 800          
camera_mode = "free" 

GRID_SIZE = 600
PLAYER_HEIGHT = 80

elevated_cells = []  # List to store elevated cell numbers
elevation_height = 150  
ladder_cells = {} 
elevated_cell_count = 12  
quadric = None

def initialize_game():
    global player_pos, player_angle, game_score, is_game_over, current_cell
    global quadric, dice_value, dice_rolling, target_cell, moving_to_target
    global snake_points, snake_head_pos, snake_direction
    global game_start_time, snake_length, snake_speed, snake_speed_multiplier
    global last_snake_growth_time, last_speed_increase_time
    global elevated_cells, ladder_cells
    global player2_pos, player2_angle, player2_current_cell, player2_game_score
    global player2_dice_value, player2_target_cell, player2_moving_to_target
    global current_player, last_frame_time, move_duration
    global move_is_from_snake_collision, player2_move_is_from_snake_collision
    global move_start_pos, player2_move_start_pos, player2_move_duration, player2_move_start_time
    global last_roll_time, player2_last_roll_time, roll_duration, player2_roll_duration
    global is_mouse_dragging, last_mouse_x, last_mouse_y
    global player1_health, player2_health
    global snake_visible  
    global player1_immunity, player2_immunity, immunity_effect_angle
    
    player1_immunity = False
    player2_immunity = False
    immunity_effect_angle = 0

    player1_health = max_health  
    player2_health = max_health  
    is_mouse_dragging = False
    last_mouse_x = 0
    last_mouse_y = 0

    # tracking variables
    snake_visible = False 
    is_mouse_dragging = False
    last_mouse_x = 0
    last_mouse_y = 0
    move_is_from_snake_collision = False
    player2_move_is_from_snake_collision = False
    move_duration = 1.0
    player2_move_duration = 1.0
    last_frame_time = time.time()
    
    quadric = gluNewQuadric()
    player_pos = [-540, -540, PLAYER_HEIGHT]  #cell 1
    player_angle = 0
    game_score = 0
    is_game_over = False
    current_cell = 1
    dice_value = 1
    dice_rolling = False
    last_roll_time = 0
    roll_duration = 1.0
    target_cell = 1
    moving_to_target = False
    move_start_pos = player_pos.copy()
    
    # player 2
    player2_pos = [-540 + 40, -540, PLAYER_HEIGHT]  # to stand beside p1
    player2_angle = 0
    player2_current_cell = 1
    player2_game_score = 0
    player2_dice_value = 1
    player2_dice_rolling = False
    player2_last_roll_time = 0
    player2_roll_duration = 1.0
    player2_target_cell = 1
    player2_moving_to_target = False
    player2_move_start_pos = player2_pos.copy()
    player2_move_start_time = 0
    
    current_player = 1  
    
    game_start_time = time.time()
    last_snake_growth_time = time.time()
    last_speed_increase_time = time.time()
    snake_length = snake_base_length
    snake_speed = snake_base_speed
    snake_speed_multiplier = 1.0
    
    setup_elevated_cells()
    initialize_snake()

def handle_snake_entry():
    global snake_visible
    if player_pos[1] >= -420 and player2_pos[1] >= -420:  # -540 + 120 = -420 (2nd row)
        snake_visible = True

def setup_elevated_cells():   #random 
    global elevated_cells, ladder_cells
    elevated_cells = []   
    ladder_cells = {}
    potential_cells = list(range(5, 100))  #keeping shurur koyta khali for a smooth start 
    elevated_cells = random.sample(potential_cells, elevated_cell_count)    # Select random cells to be elevated

    for elevated_cell in elevated_cells:    
        row = (elevated_cell - 1) // 10        
        col = (elevated_cell - 1) % 10  #elev cell loc to place ladder
        potential_ladder_cells = []
        
        if col > 0:# Check  left
            left_cell = elevated_cell - 1
            if left_cell not in elevated_cells:
                potential_ladder_cells.append(left_cell)
        
        if col < 9:# Check right
            right_cell = elevated_cell + 1
            if right_cell not in elevated_cells:
                potential_ladder_cells.append(right_cell)
        
        if row > 0:# Check below
            below_cell = elevated_cell - 10
            if below_cell not in elevated_cells:
                potential_ladder_cells.append(below_cell)
        
        if row < 9:# Check above
            above_cell = elevated_cell + 10
            if above_cell not in elevated_cells:
                potential_ladder_cells.append(above_cell)
        
        for i in potential_ladder_cells: 
            if elevated_cell - 1 == i:
                ladder_cell=i
                ladder_cells[ladder_cell] = elevated_cell

def get_ladder_position(start_cell, end_cell):
    """Get the x,y position where the ladder is located between two cells"""
    end_pos = get_cell_center(end_cell)
    cell_size = 120
    
    if not end_pos:
        return (0, 0)  
    
    # Calculate row for end cell
    end_row = (end_cell - 1) // 10
    
    # Initialize ladder position
    ladder_x = 0
    ladder_y = 0
    
    # Place ladder based on row parity
    if end_row % 2 == 0:
        # Place ladder on the left side of the elevated cell
        ladder_x = end_pos[0] - cell_size/4
        ladder_y = end_pos[1]
    else:
        # Place ladder on the right side of the elevated cell
        ladder_x = end_pos[0] + cell_size/4
        ladder_y = end_pos[1]
    
    return (ladder_x, ladder_y)

def render_ladders():
    cell_size = 120
    ladder_width = 30
    rung_count = 5  
    
    for start_cell, end_cell in ladder_cells.items():
        start_pos = get_cell_center(start_cell)
        end_pos = get_cell_center(end_cell)
        
        if not start_pos or not end_pos:
            continue
            
        end_row = (end_cell - 1) // 10
        end_col = (end_cell - 1) % 10
        
        if end_col == 0 or end_col == 9:  # Leftmost or rightmost column
            if end_row % 2 == 0:  # Even row
                ladder_x = end_pos[0]
                ladder_y = end_pos[1] - cell_size/2  # Front wall
            else:  # Odd row
                ladder_x = end_pos[0]
                ladder_y = end_pos[1] + cell_size/2  # Back wall
            ladder_direction = "horizontal"
        else:
            if end_row % 2 == 0:  # Even row
                ladder_x = end_pos[0] - cell_size/2  # Left wall
                ladder_y = end_pos[1]
            else:  # Odd row
                ladder_x = end_pos[0] + cell_size/2  # Right wall
                ladder_y = end_pos[1]
            ladder_direction = "vertical"
        
        # Draw the ladder sides 
        glColor3f(0.6, 0.4, 0.2)  # Brown 
        glLineWidth(5.0)
        
        if ladder_direction == "vertical":
            # Left side
            glBegin(GL_LINES)
            glVertex3f(ladder_x, ladder_y - ladder_width/2, 0)
            glVertex3f(ladder_x, ladder_y - ladder_width/2, elevation_height)
            # Right side
            glVertex3f(ladder_x, ladder_y + ladder_width/2, 0)
            glVertex3f(ladder_x, ladder_y + ladder_width/2, elevation_height)
            glEnd()
            
            # Draw the rungs
            for i in range(rung_count):
                t = (i + 1) / (rung_count + 1)
                z = t * elevation_height
                glBegin(GL_LINES)
                glVertex3f(ladder_x, ladder_y - ladder_width/2, z)
                glVertex3f(ladder_x, ladder_y + ladder_width/2, z)
                glEnd()
        else:  # horizontal
            # Bottom side
            glBegin(GL_LINES)
            glVertex3f(ladder_x - ladder_width/2, ladder_y, 0)
            glVertex3f(ladder_x - ladder_width/2, ladder_y, elevation_height)
            # Top side
            glVertex3f(ladder_x + ladder_width/2, ladder_y, 0)
            glVertex3f(ladder_x + ladder_width/2, ladder_y, elevation_height)
            glEnd()
            
            # Draw the rungs
            for i in range(rung_count):
                t = (i + 1) / (rung_count + 1)
                z = t * elevation_height
                glBegin(GL_LINES)
                glVertex3f(ladder_x - ladder_width/2, ladder_y, z)
                glVertex3f(ladder_x + ladder_width/2, ladder_y, z)
                glEnd()
                
        glLineWidth(1.0)

def initialize_snake():
    global snake_points, snake_target_points, snake_head_pos, snake_direction
    
    snake_head_pos = [-600, -600] #cell 1 er kachh theke
    snake_direction = [1, 0]  
    snake_points = []  #initial snake body points (straight line)
    for i in range(snake_length):
        x = snake_head_pos[0] - i * snake_segment_length * snake_direction[0]
        y = snake_head_pos[1] - i * snake_segment_length * snake_direction[1]
        snake_points.append([x, y])
    snake_target_points = snake_points.copy() # Copy points to target points

def update_snake():
    global snake_points, snake_target_points, snake_head_pos, snake_direction
    global snake_last_move_time, snake_move_interval, snake_length
    global last_snake_growth_time, last_speed_increase_time, snake_speed, snake_speed_multiplier
    
    current_time = time.time()
    
    if current_time - last_snake_growth_time >= snake_growth_interval:
      if snake_length < snake_base_length * 2: 
        last_snake_growth_time = current_time
        snake_length += 1
        
        # Add a new segment at snake end
        if len(snake_points) > 0:
            tail_pos = snake_points[-1].copy()
            snake_points.append(tail_pos)
            snake_target_points.append(tail_pos)
    
    if current_time - last_speed_increase_time >= snake_speed_increase_interval:
        last_speed_increase_time = current_time
        snake_speed_multiplier += 0.1  # Increase speed by 10%
        snake_speed = snake_base_speed * snake_speed_multiplier
    
    if current_time - snake_last_move_time >= snake_move_interval:
        snake_last_move_time = current_time
        actual_speed = snake_speed
        
        snake_head_pos[0] += snake_direction[0] * actual_speed * snake_move_interval
        snake_head_pos[1] += snake_direction[1] * actual_speed * snake_move_interval
        
        # Check grid boundaries and change direction
        if snake_head_pos[0] < -600:
            snake_head_pos[0] = -600
            snake_direction = [0, 1]  # Go up
        elif snake_head_pos[0] > 600:
            snake_head_pos[0] = 600
            snake_direction = [0, -1]  # Go down
        elif snake_head_pos[1] < -600:
            snake_head_pos[1] = -600
            snake_direction = [1, 0]  # Go right
        elif snake_head_pos[1] > 600:
            snake_head_pos[1] = 600
            snake_direction = [-1, 0]  # Go left
            
        #change direction randomly
        if random.random() < 0.1:  # 5% chance per update to change direction
            directions = [
                [1, 0],   # Right
                [-1, 0],  # Left
                [0, 1],   # Up
                [0, -1]   # Down
            ]
            opposite_dir = [-snake_direction[0], -snake_direction[1]]
            valid_directions = [d for d in directions if d != opposite_dir]
            
            # Choose a random new direction
            snake_direction = random.choice(valid_directions)
        
        snake_target_points = [[snake_head_pos[0], snake_head_pos[1]]]
        prev_point = snake_target_points[0]
        
        for i in range(1, snake_length):
            if i >= len(snake_points):
                snake_points.append(prev_point.copy())
                snake_target_points.append(prev_point.copy())
                continue
            dx = prev_point[0] - snake_points[i-1][0]
            dy = prev_point[1] - snake_points[i-1][1]
            
            # Normalize direction
            length = math.sqrt(dx*dx + dy*dy)
            if length > 0:
                dx /= length
                dy /= length
            next_x = prev_point[0] - dx * snake_segment_length
            next_y = prev_point[1] - dy * snake_segment_length
            snake_target_points.append([next_x, next_y])
            prev_point = [next_x, next_y]
        
        for i in range(min(snake_length, len(snake_points))):
            dx = snake_target_points[i][0] - snake_points[i][0]
            dy = snake_target_points[i][1] - snake_points[i][1]
            
            snake_points[i][0] += dx * 0.5
            snake_points[i][1] += dy * 0.5

def render_snake():
    if not snake_visible:  
        return
    if not snake_points:
        return
    glLineWidth(10.0) #    #snake body - connected segments
    glBegin(GL_LINE_STRIP)
    
    for i, point in enumerate(snake_points):
        if i >= snake_length:
            break
            
        t = i / (snake_length - 1) if snake_length > 1 else 0
        r = snake_color[0] * (1 - t * 0.7)  
        g = snake_color[1] * (1 - t * 0.5)
        b = snake_color[2] * (1 - t * 0.3)
        glColor3f(r, g, b)
        glVertex3f(point[0], point[1], 5)
    
    glEnd()
    glLineWidth(1.0)
    glPushMatrix()
    glTranslatef(snake_points[0][0], snake_points[0][1], 10)
    # Rotate the head based on snake direction
    if snake_direction[0] != 0:  # Moving horizontally
        glRotatef(90, 0, 1, 0)  # Rotate around Y-axis
    elif snake_direction[1] != 0:  # Moving vertically
        glRotatef(90, 1, 0, 0)  # Rotate around X-axis
    
    glColor3f(snake_color[0], snake_color[1], snake_color[2])
    # Scale to create oval shape (stretched in movement direction)
    glScalef(1.0, 0.6, 0.6)  # Make it longer in one direction
    glutSolidSphere(25, 20, 15)  #  sphere but scale it to make an oval
    glPopMatrix()
    
def get_cell_center(cell_number):
    cell_size = 120
    grid_divisions = 10  
    start_x = -600     
    start_y = -600
    
    if cell_number < 1 or cell_number > 100:
        return None
    
    row = (cell_number - 1) // grid_divisions
    if row % 2 == 0:
        col = (cell_number - 1) % grid_divisions
    else:
        col = grid_divisions - 1 - ((cell_number - 1) % grid_divisions)
    
    x = start_x + col * cell_size + cell_size / 2
    y = start_y + row * cell_size + cell_size / 2
    
    return [x, y]

def get_cell_height(cell_number):
    if cell_number in elevated_cells:
        return elevation_height
    return 0

def is_player_on_elevated_cell():
    return current_cell in elevated_cells

def roll_dice():
    global dice_rolling, last_roll_time, roll_duration
    global player2_dice_rolling, player2_last_roll_time, player2_roll_duration
    global current_player, moving_to_target, player2_moving_to_target
    
    if current_player == 1:
        if not dice_rolling and not moving_to_target:
            dice_rolling = True
            last_roll_time = time.time()
            roll_duration = 1.0  
    else:  # Player 2's turn
        if not player2_dice_rolling and not player2_moving_to_target:
            player2_dice_rolling = True
            player2_last_roll_time = time.time()
            player2_roll_duration = 1.0  
def render_player():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 0, 1)

    # Body
    glPushMatrix()
    glColor3f(0.0, 0.5, 0.0)
    glTranslatef(0, 0, 40)
    glScalef(40, 20, 80)
    glutSolidCube(1)
    glPopMatrix()

    # Head
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.0)
    glTranslatef(0, 0, 90)
    glutSolidSphere(12, 20, 20)
    glPopMatrix()

    # Arms
    for side in [-1, 1]:
        glPushMatrix()
        glColor3f(1.0, 0.8, 0.6)
        glTranslatef(17 * side, 0, 65)
        glRotatef(90, 0, side, 0)
        gluCylinder(quadric, 3, 3, 15, 10, 10)
        glPopMatrix()

    # Legs
    for side in [-1, 1]:
        glPushMatrix()
        glColor3f(0.0, 0.0, 1.0)
        glTranslatef(5 * side, 0, -20)
        glScalef(8, 8, 30)
        glutSolidCube(1)
        glPopMatrix()

    glPopMatrix()

def render_player2():
    glPushMatrix()
    glTranslatef(player2_pos[0], player2_pos[1], player2_pos[2])
    glRotatef(player2_angle, 0, 0, 1)
    
    # Body
    glPushMatrix()
    glColor3f(0.8, 0.0, 0.0)  
    glTranslatef(0, 0, 40)
    glScalef(40, 20, 80)
    glutSolidCube(1)
    glPopMatrix()
    
    # Head
    glPushMatrix()
    glColor3f(0.0, 0.0, 0.0)
    glTranslatef(0, 0, 90)
    glutSolidSphere(12, 20, 20)
    glPopMatrix()
    
    # Arms
    for side in [-1, 1]:
        glPushMatrix()
        glColor3f(1.0, 0.8, 0.6)
        glTranslatef(17 * side, 0, 65)
        glRotatef(90, 0, side, 0)
        gluCylinder(quadric, 3, 3, 15, 10, 10)
        glPopMatrix()
    
    # Legs
    for side in [-1, 1]:
        glPushMatrix()
        glColor3f(0.8, 0.5, 0.0)  
        glTranslatef(5 * side, 0, -20)
        glScalef(8, 8, 30)
        glutSolidCube(1)
        glPopMatrix()    
    glPopMatrix()

def handle_keyboard(key, x, y):
    global player_pos, player_angle, dice_rolling, moving_to_target, is_game_over
    global player1_immunity, player2_immunity, current_player

    if is_game_over and key == b'r':
        initialize_game()
        return

    if is_game_over:
        return
    
    key = key.decode('utf-8').lower()
    
    if key == 'd':
        roll_dice()
    elif key == 'w':  # Cheat code
        if current_player == 1:
            player1_immunity = not player1_immunity
        else:
            player2_immunity = not player2_immunity

def handle_special_keys(key, x, y):
    global camera_position, camera_target, camera_angle_x, camera_angle_y, camera_distance
    move_speed = 20
    
    if camera_mode == "free":
        if key == GLUT_KEY_UP:
            #  up
            camera_target[2] += move_speed
            update_camera_position()
        elif key == GLUT_KEY_DOWN:
            #  down
            camera_target[2] -= move_speed
            if camera_target[2] < 0:
                camera_target[2] = 0
            update_camera_position()
        elif key == GLUT_KEY_LEFT:
            #  left
            camera_angle_x -= 5
            update_camera_position()
        elif key == GLUT_KEY_RIGHT:
            #  right
            camera_angle_x += 5
            update_camera_position()
    else:
        # camera non-free modes
        if key == GLUT_KEY_UP:
            camera_position[2] -= 50  # Zoom in
            if camera_position[2] < 300:
                camera_position[2] = 300
        elif key == GLUT_KEY_DOWN:
            camera_position[2] += 50  # Zoom out
            if camera_position[2] > 1200:
                camera_position[2] = 1200

def handle_mouse_motion(x, y):
    global camera_angle_x, camera_angle_y, last_mouse_x, last_mouse_y, is_mouse_dragging, camera_mode
    
    if is_mouse_dragging and camera_mode == "free":
        dx = x - last_mouse_x
        dy = y - last_mouse_y
        
        camera_angle_x += dx * 0.5  # Horizontal 
        camera_angle_y -= dy * 0.5  # Vertical 
        
        # Limit vertical angle to avoid flipping
        if camera_angle_y < 5:
            camera_angle_y = 5
        elif camera_angle_y > 170:
            camera_angle_y = 170
            
        update_camera_position()
        
    last_mouse_x = x
    last_mouse_y = y
    glutPostRedisplay()

def handle_mouse(button, state, x, y):
    global dice_rolling, is_mouse_dragging, last_mouse_x, last_mouse_y
    global current_player, moving_to_target, player2_dice_rolling, player2_moving_to_target
    
    if button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            switch_camera()
    elif button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            if 850 <= x <= 950 and 50 <= y <= 150:
                roll_dice()
            elif 850 <= x <= 950 and 150 <= y <= 200:
                if not dice_rolling and not moving_to_target and not player2_dice_rolling and not player2_moving_to_target:
                    current_player = 2 if current_player == 1 else 1
            
            is_mouse_dragging = True
            last_mouse_x = x
            last_mouse_y = y
        else:
            is_mouse_dragging = False

def switch_camera():
    global camera_mode, camera_position, camera_angle_x, camera_angle_y
    global is_mouse_dragging, last_mouse_x, last_mouse_y

    if camera_mode == "top_down":
        camera_mode = "angled"
        camera_position = [0, -600, 600]  
    elif camera_mode == "angled":
        camera_mode = "free"
        camera_angle_x = 45   
        camera_angle_y = 45   
        camera_distance = 800
        update_camera_position()
    else:
        camera_mode = "top_down"
        camera_position = [0, 0, 800]  

is_mouse_dragging = False
last_mouse_x = 0
last_mouse_y = 0

def update_camera_position():
    """Update camera position based on angles and distance"""
    global camera_position
    rad_x = math.radians(camera_angle_x)
    rad_y = math.radians(camera_angle_y)
    
    x = camera_target[0] + camera_distance * math.sin(rad_y) * math.cos(rad_x)
    y = camera_target[1] + camera_distance * math.sin(rad_y) * math.sin(rad_x)
    z = camera_target[2] + camera_distance * math.cos(rad_y)
    
    camera_position = [x, y, z]

def configure_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.25, 1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == "top_down":
        gluLookAt(
            0, 0, camera_position[2],  # Camera position
            0, 0, 0,                   # Look at center of grid
            0, 1, 0                    # Up vector
        )
    elif camera_mode == "angled":
        gluLookAt(
            camera_position[0], camera_position[1], camera_position[2],
            0, 0, 0,  
            0, 0, 1   
        )
    else:  
        
        gluLookAt(
            camera_position[0], camera_position[1], camera_position[2],
            camera_target[0], camera_target[1], camera_target[2],
            0, 0, 1   
        )

def draw_cell_number(x, y, z, number):
    """Draw cell number at the center of each grid cell with bold appearance"""
    glPushMatrix()
    glTranslatef(x, y, z + 1) 
    
    scale_factor = 0.3
    glScalef(scale_factor, scale_factor, scale_factor)
    
    number_str = str(number)
    text_width = len(number_str) * 104  
    text_height = 119  
    glTranslatef(-text_width / 2, -text_height / 2, 0)
    
    glColor3f(0, 0, 0) 
    
    glPushMatrix()
    for ch in number_str:
        glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(ch))
    glPopMatrix()
    
    # Second pass 
    glPushMatrix()
    glTranslatef(2, 0, 0)
    for ch in number_str:
        glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(ch))
    glPopMatrix()
    
    glPopMatrix()

def render_grid():
    cell_size = 120
    grid_divisions = 10 
    start_x = -600
    start_y = -600
    
    # Draw checkerboard 
    glBegin(GL_QUADS)
    for row in range(grid_divisions):
        for col in range(grid_divisions):
            x = start_x + col * cell_size
            y = start_y + row * cell_size
            
            # Even rows: left to right, Odd rows: right to left
            if row % 2 == 0:
                cell_number = row * grid_divisions + col + 1
            else:
                cell_number = (row + 1) * grid_divisions - col
                
            z = get_cell_height(cell_number)
            
            #  cell color pattern
            if (row + col) % 2 == 0:
                if cell_number in elevated_cells:
                    glColor3f(0.9, 0.9, 1.0) # for elevated cells
                else:
                    glColor3f(1.0, 1.0, 1.0) # White
            else:
                if cell_number in elevated_cells:
                    glColor3f(0.8, 0.8, 1.0) # for elevated cells
                else:
                    glColor3f(1.0, 1.0, 0.5) # Light yellow
                    
            # cell top surface
            glVertex3f(x, y, z)
            glVertex3f(x + cell_size, y, z)
            glVertex3f(x + cell_size, y + cell_size, z)
            glVertex3f(x, y + cell_size, z)
            
            #  elevated cell sides for 3D effect
            if cell_number in elevated_cells:
                # Left side
                glColor3f(0.7, 0.7, 0.9) 
                glVertex3f(x, y, 0)
                glVertex3f(x, y, z)
                glVertex3f(x, y + cell_size, z)
                glVertex3f(x, y + cell_size, 0)
                
                # Right side
                glVertex3f(x + cell_size, y, 0)
                glVertex3f(x + cell_size, y, z)
                glVertex3f(x + cell_size, y + cell_size, z)
                glVertex3f(x + cell_size, y + cell_size, 0)
                
                # Front side
                glVertex3f(x, y, 0)
                glVertex3f(x, y, z)
                glVertex3f(x + cell_size, y, z)
                glVertex3f(x + cell_size, y, 0)
                
                # Back side
                glVertex3f(x, y + cell_size, 0)
                glVertex3f(x, y + cell_size, z)
                glVertex3f(x + cell_size, y + cell_size, z)
                glVertex3f(x + cell_size, y + cell_size, 0)
    glEnd()
    
    # Draw cell numbers
    for row in range(grid_divisions):
        for col in range(grid_divisions):
            x = start_x + col * cell_size + cell_size / 2
            y = start_y + row * cell_size + cell_size / 2
            
            # Even rows: left to right, Odd rows: right to left
            if row % 2 == 0:
                cell_number = row * grid_divisions + col + 1
            else:
                cell_number = (row + 1) * grid_divisions - col
                
            z = get_cell_height(cell_number)    
                
            draw_cell_number(x, y, z, cell_number)
            
    #  grid border
    glColor3f(0.5, 0.5, 0.8) 
    glLineWidth(3.0)
    glBegin(GL_LINE_LOOP)
    glVertex3f(start_x, start_y, 0)
    glVertex3f(start_x + grid_divisions * cell_size, start_y, 0)
    glVertex3f(start_x + grid_divisions * cell_size, start_y + grid_divisions * cell_size, 0)
    glVertex3f(start_x, start_y + grid_divisions * cell_size, 0)
    glEnd()
    glLineWidth(1.0)
    
    # current cells with blue glow 
    current_pos = get_cell_center(current_cell)
    if current_pos:
        glPushMatrix()
        glTranslatef(current_pos[0], current_pos[1], 2)
        glColor4f(0.0, 0.5, 1.0, 0.5) 
        glScalef(cell_size * 0.8, cell_size * 0.8, 1)
        glutSolidCube(1)
        glPopMatrix()
    
    player2_pos = get_cell_center(player2_current_cell)
    if player2_pos:
        glPushMatrix()
        glTranslatef(player2_pos[0], player2_pos[1], 2)
        glColor4f(0.0, 0.5, 1.0, 0.5) 
        glScalef(cell_size * 0.8, cell_size * 0.8, 1)
        glutSolidCube(1)
        glPopMatrix()

def render_dice():
    glMatrixMode(GL_PROJECTION)     # Save previous matrices
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)  #  2D coordinates for UI
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    
    # player turn indicator
    if current_player == 1:
        glColor3f(0.0, 0.5, 0.0)  
    else:
        glColor3f(0.8, 0.0, 0.0)  
    
    glBegin(GL_QUADS)
    glVertex2f(850, 200)
    glVertex2f(950, 200)
    glVertex2f(950, 250)
    glVertex2f(850, 250)
    glEnd()
    
    glColor3f(1.0, 1.0, 1.0) 
    display_text_2d(855, 220, f"Player {current_player}'s Turn", GLUT_BITMAP_HELVETICA_12)
    
    # dice -clickable area)
    glColor3f(0.8, 0.8, 0.8)
    glBegin(GL_QUADS)
    glVertex2f(850, 650)
    glVertex2f(950, 650)
    glVertex2f(950, 750)
    glVertex2f(850, 750)
    glEnd()
    
    # dice border
    glColor3f(0.2, 0.2, 0.2)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(850, 650)
    glVertex2f(950, 650)
    glVertex2f(950, 750)
    glVertex2f(850, 750)
    glEnd()
    glLineWidth(1.0)
    
    glColor3f(0.0, 0.0, 0.0)  # Black dots
    dot_radius = 8  
    
    def draw_dot(x, y):
        glBegin(GL_POLYGON)
        for i in range(20):  # segments for smoother circle
            angle = 2.0 * math.pi * i / 20
            dx = dot_radius * math.cos(angle)
            dy = dot_radius * math.sin(angle)
            glVertex2f(x + dx, y + dy)
        glEnd()
    
    current_dice_value = dice_value if current_player == 1 else player2_dice_value
    
    if current_dice_value == 1 or current_dice_value == 3 or current_dice_value == 5:
        draw_dot(900, 700) 
    
    if current_dice_value >= 2:
        draw_dot(870, 730)  
        draw_dot(930, 670) 
    
    if current_dice_value >= 4:
        draw_dot(870, 670)  
        draw_dot(930, 730)  
    
    if current_dice_value == 6:
        draw_dot(870, 700)  
        draw_dot(930, 700) 
    
    glColor3f(0.0, 0.0, 0.0)
    display_text_2d(875, 630, "Click to Roll", GLUT_BITMAP_HELVETICA_12)
    
    # Restore previous state
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def display_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1.0, 0.5, 0.0)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def display_text_2d(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

def check_snake_collision():
    global player1_health, player2_health
    collisions = [False, False]  
    health_decreased = [False, False]

    # Check player 1
    if not current_cell in elevated_cells and not player1_immunity:  
        player1_cell_center = get_cell_center(current_cell)
        if player1_cell_center: 
            cell_size = 120
            
            # Define current cell boundaries
            cell_left = player1_cell_center[0] - cell_size/2
            cell_right = player1_cell_center[0] + cell_size/2
            cell_top = player1_cell_center[1] + cell_size/2
            cell_bottom = player1_cell_center[1] - cell_size/2
            
            # if any snake segment is within the current cell
            for i, segment in enumerate(snake_points):
                if i >= snake_length:
                    break
                snake_x, snake_y = segment[0], segment[1]
                
                # if snake segment is within the cell boundaries
                if (cell_left <= snake_x <= cell_right and cell_bottom <= snake_y <= cell_top):
                    
                    player1_health -= 1  
                    health_decreased[0] = True
                    
                    if player1_health <= 0:
                        player1_health = max_health
                        collisions[0] = 1
                    else:
                        collisions[0] = max(1, current_cell - 5)
                    break

    # Check player 2
    if not player2_current_cell in elevated_cells and not player2_immunity:  
        player2_cell_center = get_cell_center(player2_current_cell)
        if player2_cell_center: 
            cell_size = 120

            #current cell boundaries
            cell_left = player2_cell_center[0] - cell_size/2
            cell_right = player2_cell_center[0] + cell_size/2
            cell_top = player2_cell_center[1] + cell_size/2
            cell_bottom = player2_cell_center[1] - cell_size/2
            
            for i, segment in enumerate(snake_points):
                if i >= snake_length:
                    break
                snake_x, snake_y = segment[0], segment[1]
                
                if (cell_left <= snake_x <= cell_right and cell_bottom <= snake_y <= cell_top):
                    
                    player2_health -= 1  
                    health_decreased[1] = True
                    
                    if player2_health <= 0:
                        player2_health = max_health
                        collisions[1] = 1
                    else:
                        collisions[1] = max(1, player2_current_cell - 5)
                    break
                  
    return collisions, health_decreased

def render_immunity_effect():
    global immunity_effect_angle
    
    immunity_effect_angle = (immunity_effect_angle + 2) % 360
    
    # player 1 
    if player1_immunity:
        glPushMatrix()
        glTranslatef(player_pos[0], player_pos[1], player_pos[2] + 20)
        glRotatef(immunity_effect_angle, 0, 0, 1)
        
        glColor4f(0.0, 1.0, 0.7, 0.5)  
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0) 
        num_segments = 20
        radius = 50
        for i in range(num_segments + 1):
            angle = math.pi * 2 * i / num_segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glColor4f(0.0, 1.0, 0.7, 0.3 + 0.2 * math.sin(immunity_effect_angle * 0.05 + i * 0.5))
            glVertex3f(x, y, 0)
        glEnd()
        glPopMatrix()
    
    if player2_immunity:
        glPushMatrix()
        glTranslatef(player2_pos[0], player2_pos[1], player2_pos[2] + 20)
        glRotatef(-immunity_effect_angle, 0, 0, 1)  
        
        glColor4f(1.0, 0.5, 0.0, 0.5)  
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0) 
        num_segments = 20
        radius = 50
        for i in range(num_segments + 1):
            angle = math.pi * 2 * i / num_segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            glColor4f(1.0, 0.5, 0.0, 0.3 + 0.2 * math.sin(immunity_effect_angle * 0.05 + i * 0.5))
            glVertex3f(x, y, 0)
        glEnd()
        glPopMatrix()

def render_health_bars():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)  
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    
    # health bar positions 
    p1_bar_x = 850
    p1_bar_y = 600
    p2_bar_x = 850
    p2_bar_y = 550
    
    # player 1 
    glBegin(GL_QUADS)
    glVertex2f(p1_bar_x, p1_bar_y)
    glVertex2f(p1_bar_x + health_bar_width, p1_bar_y)
    glVertex2f(p1_bar_x + health_bar_width, p1_bar_y + health_bar_height)
    glVertex2f(p1_bar_x, p1_bar_y + health_bar_height)
    glEnd()
    
    p1_health_width = (player1_health / max_health) * health_bar_width
    glColor3f(0.0, 0.8, 0.0) 
    glBegin(GL_QUADS)
    glVertex2f(p1_bar_x, p1_bar_y)
    glVertex2f(p1_bar_x + p1_health_width, p1_bar_y)
    glVertex2f(p1_bar_x + p1_health_width, p1_bar_y + health_bar_height)
    glVertex2f(p1_bar_x, p1_bar_y + health_bar_height)
    glEnd()
    
    # player 2 
    glBegin(GL_QUADS)
    glVertex2f(p2_bar_x, p2_bar_y)
    glVertex2f(p2_bar_x + health_bar_width, p2_bar_y)
    glVertex2f(p2_bar_x + health_bar_width, p2_bar_y + health_bar_height)
    glVertex2f(p2_bar_x, p2_bar_y + health_bar_height)
    glEnd()
    
    p2_health_width = (player2_health / max_health) * health_bar_width
    glColor3f(0.0, 0.8, 0.0)  
    glBegin(GL_QUADS)
    glVertex2f(p2_bar_x, p2_bar_y)
    glVertex2f(p2_bar_x + p2_health_width, p2_bar_y)
    glVertex2f(p2_bar_x + p2_health_width, p2_bar_y + health_bar_height)
    glVertex2f(p2_bar_x, p2_bar_y + health_bar_height)
    glEnd()
    
    glColor3f(1.0, 0.5, 0.0) 
    display_text_2d(p1_bar_x , p1_bar_y + 17, f"Player 1 Health:", GLUT_BITMAP_HELVETICA_10)
    display_text_2d(p2_bar_x , p2_bar_y + 17, f"Player 2 Health:", GLUT_BITMAP_HELVETICA_10)
    
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def render_reward():
    #center of the 100th cell
    final_cell_pos = get_cell_center(100)
    if not final_cell_pos:
        return
    
    final_cell_height = get_cell_height(100)
    
    glPushMatrix()
    glTranslatef(final_cell_pos[0], final_cell_pos[1], final_cell_height + 120)
    
    # continuous rotation
    glRotatef(reward_angle, 0, 0, 1)  # around Z axis
    
    glPushMatrix()
    glTranslatef(0, 0, 55)
    glRotatef(reward_angle * 2, 0, 0, 1)  # Double rotation speed for star
    
    glColor3f(1.0, 1.0, 0.0) 
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0) 
    
    star_points = 5
    outer_radius = 50
    inner_radius = 20
    
    for i in range(star_points * 2 + 1):
        if i % 2 == 0:
            radius = outer_radius
        else:
            radius = inner_radius
            
        angle = math.pi * i / star_points
        x = radius * math.sin(angle)
        y = radius * math.cos(angle)
        
        glVertex3f(x, y, 0)
    
    glEnd()
    glPopMatrix()
    glPointSize(3.0)    #glowing particles
    glBegin(GL_POINTS)
    
    num_particles = 20 #particle pos
    particle_radius = 60
    for i in range(num_particles):
        angle = (i / num_particles) * 2 * math.pi + (reward_angle * 0.03)
        radius = particle_radius + 5 * math.sin(reward_angle * 0.05 + i)
        
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = 20 + 10 * math.sin(reward_angle * 0.03 + i * 0.5)
        
        # Particle color transitions
        brightness = 0.7 + 0.3 * math.sin(reward_angle * 0.05 + i * 0.2)
        glColor3f(brightness, brightness, 0.0)  
        
        glVertex3f(x, y, z)
    
    glEnd()
    glPointSize(1.0)
    
    glPopMatrix()

def update_game_state():
    global dice_value, dice_rolling, last_roll_time, roll_duration
    global current_cell, target_cell, moving_to_target, move_start_time
    global player_pos, move_start_pos, is_game_over, last_frame_time
    global game_score, reward_angle
    global player2_dice_value, player2_dice_rolling, player2_last_roll_time
    global player2_roll_duration, player2_current_cell, player2_target_cell
    global player2_moving_to_target, player2_move_start_time, player2_move_duration
    global player2_pos, player2_move_start_pos, player2_game_score
    global current_player, move_is_from_snake_collision, player2_move_is_from_snake_collision
    global player_angle, snake_visible,immunity_effect_angle

    current_time = time.time()
    delta_time = current_time - last_frame_time
    last_frame_time = current_time
    
    # Update spinning 
    reward_angle += reward_spin_speed * delta_time
    if reward_angle > 360:
        reward_angle -= 360

    # Update immunity 
    immunity_effect_angle += 180 * delta_time
    if immunity_effect_angle > 360:
        immunity_effect_angle -= 360
    
    if is_game_over:
        return
    
    handle_snake_entry()
    if snake_visible:
        update_snake()
    
    # Check for snake collisions for both players
        if not moving_to_target and not player2_moving_to_target:
           collision_results, health_decreased = check_snake_collision()
        
        # Handle Player 1 collision
           if collision_results[0]:
               target_cell = collision_results[0]
               move_start_pos = player_pos.copy()
               move_start_time = current_time
               moving_to_target = True
               move_is_from_snake_collision = True
        
        # Handle Player 2 collision
           if collision_results[1]:
               player2_target_cell = collision_results[1]
               player2_move_start_pos = player2_pos.copy()
               player2_move_start_time = current_time
               player2_moving_to_target = True
               player2_move_is_from_snake_collision = True
    
    # Handle Player 1 updates
    if current_player == 1:
        if dice_rolling:
            if current_time - last_roll_time < roll_duration:
                if random.random() < 0.2:  # Change value with 20% chance per frame
                    dice_value = random.randint(1, 6)
            else:
                dice_rolling = False
                dice_value = random.randint(1, 6)
                
                target_cell = current_cell + dice_value
                
                if target_cell > 100:
                    target_cell = current_cell  
                
                move_start_pos = player_pos.copy()
                move_start_time = current_time
                moving_to_target = True
                move_is_from_snake_collision = False  
                game_score += dice_value
    
    # Handle Player 2 updates
    else:  
        if player2_dice_rolling:
            if current_time - player2_last_roll_time < player2_roll_duration:
                if random.random() < 0.2:  # Change value with 20% chance per frame
                    player2_dice_value = random.randint(1, 6)
            else:
                player2_dice_rolling = False
                player2_dice_value = random.randint(1, 6)
                
                player2_target_cell = player2_current_cell + player2_dice_value
                
                if player2_target_cell > 100:
                    player2_target_cell =  player2_current_cell
                
                player2_move_start_pos = player2_pos.copy()
                player2_move_start_time = current_time
                player2_moving_to_target = True
                player2_move_is_from_snake_collision = False 
                player2_game_score += player2_dice_value
    
    # Handle player 1 movement to target cell
    if moving_to_target:
        progress = min(1.0, (current_time - move_start_time) / move_duration)
        target_pos = get_cell_center(target_cell)
        
        if target_pos:
            player_pos[0] = move_start_pos[0] + (target_pos[0] - move_start_pos[0]) * progress
            player_pos[1] = move_start_pos[1] + (target_pos[1] - move_start_pos[1]) * progress
            
            start_height = move_start_pos[2]
            end_height = PLAYER_HEIGHT + get_cell_height(target_cell)
            
            if progress < 0.5:
                vertical_progress = progress * 2  # Scale to 0-1 range
                player_pos[2] = start_height + (end_height - start_height + 100) * vertical_progress
            else:
                vertical_progress = (progress - 0.5) * 2  
                player_pos[2] = end_height + 100 * (1 - vertical_progress)
            
            # Check if movement is complete
            if progress >= 1.0:
                moving_to_target = False
                current_cell = target_cell
                player_pos[2] = PLAYER_HEIGHT + get_cell_height(current_cell)
                
                # Check if player landed on a ladder cell
                if current_cell in ladder_cells.values():
                    # Move to the elevated cell
                  for start_cell, end_cell in ladder_cells.items():
                    if end_cell == current_cell:
                      pass
                else:
                    if current_cell == 100:
                        is_game_over = True
                    
                    if not is_game_over and not move_is_from_snake_collision:
                        current_player = 2
    
    # Handle player 2 movement to target cell
    if player2_moving_to_target:
        progress = min(1.0, (current_time - player2_move_start_time) / player2_move_duration)
        target_pos = get_cell_center(player2_target_cell)
        
        if target_pos:
            player2_pos[0] = player2_move_start_pos[0] + (target_pos[0] - player2_move_start_pos[0]) * progress
            player2_pos[1] = player2_move_start_pos[1] + (target_pos[1] - player2_move_start_pos[1]) * progress
            
            start_height = player2_move_start_pos[2]
            end_height = PLAYER_HEIGHT + get_cell_height(player2_target_cell)
            
            if progress < 0.5:
                vertical_progress = progress * 2  # Scale to 0-1 range
                player2_pos[2] = start_height + (end_height - start_height + 100) * vertical_progress
            else:
                vertical_progress = (progress - 0.5) * 2 
                player2_pos[2] = end_height + 100 * (1 - vertical_progress)
            
            if progress >= 1.0:
                player2_moving_to_target = False
                player2_current_cell = player2_target_cell
                player2_pos[2] = PLAYER_HEIGHT + get_cell_height(player2_current_cell)
                
                if player2_current_cell in ladder_cells.values():
                    pass

                else:
                    if player2_current_cell == 100:
                        is_game_over = True
                    
                    if not is_game_over and not player2_move_is_from_snake_collision:
                        current_player = 1


def main_display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    configure_camera()
    render_grid()
    render_ladders()
    render_snake()

    render_immunity_effect()

    render_player()
    render_player2() 
    render_reward()
    render_dice()
    render_health_bars()
    
    # Left side - Player 1 information
    display_text(10, 770, f"Player 1 Cell: {current_cell}")
    display_text(10, 740, f"Player 1 Score: {game_score}")
    display_text(10, 710, f"Player 1 Health: {player1_health}/{max_health}")
    
    # Right side - Player 2 information
    display_text(250, 770, f"Player 2 Cell: {player2_current_cell}")
    display_text(250, 740, f"Player 2 Score: {player2_game_score}")
    display_text(250, 710, f"Player 2 Health: {player2_health}/{max_health}")
    
    # Game stats - middle section
    game_time = time.time() - game_start_time
    display_text(10, 620, f"Game Time: {int(game_time)} secs")
    display_text(10, 590, f"Snake Length: {snake_length}")
    display_text(10, 560, f"Snake Speed: {int(snake_speed)} px/s")
    
    # Instructions - right side
    display_text(600, 770, "Click Dice to Roll")
    display_text(600, 740, "Right Click: Switch Camera")
    display_text(600, 710, "Arrow Keys: Adjust View")
    
    if is_game_over:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, 1000, 0, 800, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        winner = "1" if current_cell == 100 else "2" if player2_current_cell == 100 else "None"
        
        game_over_text = f"GAME OVER - Player {winner} wins!"
        restart_text = "Press R to Restart"
        
        glColor3f(0.6, 0.3, 0.8)  
        
        # Calculate center position for game over text
        x_pos = 500 - (len(game_over_text) * 9 / 2)  
        glRasterPos2f(x_pos, 420)
        for char in game_over_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        
        # Calculate center position for restart text
        x_pos = 500 - (len(restart_text) * 9 / 2)  
        glRasterPos2f(x_pos, 370)
        for char in restart_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Snake and Ladder 3D Adventure")
    glutMotionFunc(handle_mouse_motion)  

    glEnable(GL_DEPTH_TEST)
    initialize_game()

    glutDisplayFunc(main_display)
    glutKeyboardFunc(handle_keyboard)
    glutSpecialFunc(handle_special_keys)
    glutMouseFunc(handle_mouse)
    glutIdleFunc(lambda: [update_game_state(), glutPostRedisplay()])
    glutMainLoop()

if __name__ == "__main__":
    main()
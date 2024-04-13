import pygame
import sys
import socket
import threading
import json

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'localhost'
port = 3000
client, addr = None, None

# Define colors
NAVY_BLUE = (3, 31, 64)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 130 , 13)

# Define screen dimensions
WIDTH = 800
HEIGHT = 800

# Grid size and margin
GRID_SIZE = 50
MARGIN = 5

# Calculate the total size of the grid
TOTAL_SIZE = GRID_SIZE * 10 + MARGIN * 11

# Calculate the starting coordinates of the grid to center it
START_X = (WIDTH - TOTAL_SIZE) // 2
START_Y = (HEIGHT - TOTAL_SIZE) // 2

# Initialize the grid matrix
grid = [[0] * 10 for _ in range(10)]

tag_player1 = None
tag_player2 = None
current_player = None
scores_player1 = 0
scores_player2 = 0

# Function to draw the grid
def draw_grid():
    for row in range(10):
        for column in range(10):
            if grid[row][column] == 0:
                color = WHITE
            elif grid[row][column] == 1:
                color = RED
            elif grid[row][column] == 2:
                color = YELLOW
            # color = WHITE if grid[row][column] == 0 else RED
            pygame.draw.rect(screen, color, [(MARGIN + GRID_SIZE) * column + START_X,
                                              (MARGIN + GRID_SIZE) * row + START_Y,
                                              GRID_SIZE, GRID_SIZE])

# Function to display the sunk ships counter
def display_counter():
    font = pygame.font.Font(None, 36)
    counter_player1 = font.render(f"Player 1: {scores_player1}", True, WHITE)
    screen.blit(counter_player1, (20, 20))
    counter_player2 = font.render(f"Player 2: {scores_player2}", True, WHITE)
    screen.blit(counter_player2, (WIDTH - counter_player2.get_width() - 20, 20))

# def handle_timer_event():
#     global total_time
#     total_time -= 1
#     if total_time <= 0:
#         end_game()

# def draw_timer():
#     font = pygame.font.Font(None, 36)
#     timer_surface = font.render(f"Time Left: {total_time} s", True, pygame.Color('white'))
#     screen.blit(timer_surface, (WIDTH - 200, 30))

# def end_game():
#     print("Game Over")
#     pygame.quit()
#     sys.exit()

def handle_client(role):
    global grid, current_player, client, addr
    s.bind((host, port))
    s.listen(1)
    print("Waiting for a connection...")
    client, addr = s.accept()
    print("Connected to", addr)
    current_player = 1  # Identificador para el servidor es 1 (Rojo)
    client.sendall("Server".encode())  # Envía el rol al cliente
    
    while True:
        data = client.recv(1024)
        if not data:
            break
        data = json.loads(data.decode())
        grid[data['row']][data['column']] = 2  # Actualizar la cuadrícula con amarillo
        print("Received from client:", data)
    client.close()

def connect_to_server(role):
    global grid, current_player
    c.connect((host, port))
    current_player = 2  # Identificador para el cliente es 2 (Amarillo)
    role = c.recv(1024).decode()
    print("Connected as", role)

    while True:
        data = c.recv(1024)
        if not data:
            break
        data = json.loads(data.decode())
        grid[data['row']][data['column']] = 1
        print("Received from server: ", data)
    c.close()

# Main function for the game
def play():
    global current_player, scores_player1, scores_player2

    # TIMER_EVENT = pygame.USEREVENT
    while True:
        # Draw the background
        screen.fill(NAVY_BLUE)

        # Draw the grid
        draw_grid()

        # Display the sunk ships counter
        display_counter()

        # Update the screen
        pygame.display.flip()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                column = (event.pos[0] - START_X) // (GRID_SIZE + MARGIN)
                row = (event.pos[1] - START_Y) // (GRID_SIZE + MARGIN)
                if 0 <= row < 10 and 0 <= column < 10 and grid[row][column] == 0:
                    grid[row][column] = current_player
                    data = json.dumps({'row': row, 'column': column}).encode()
                    if current_player == 1:
                        client.send(data)
                    else:
                        c.send(data)
                    scores_player1 += 1 if current_player == 1 else 0
                    scores_player2 += 1 if current_player == 2 else 0

                    pygame.display.flip()

# Function to display the menu
def display_menu():
    global tag_player1, tag_player2, current_player
    # Initialize pygame
    pygame.init()
    
    while True:
        # Draw the background
        screen.fill(NAVY_BLUE)

        # Display menu text
        font = pygame.font.Font(None, 36)
        title = font.render("Menu", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

        # Create button for Player One
        button_player_one = pygame.Rect(WIDTH//2 - 100, 200, 200, 50)
        pygame.draw.rect(screen, WHITE, button_player_one)
        text_player_one = font.render("Create game", True, NAVY_BLUE)
        screen.blit(text_player_one, (button_player_one.centerx - text_player_one.get_width()//2, button_player_one.centery - text_player_one.get_height()//2))

        # Create button for Player Two
        button_player_two = pygame.Rect(WIDTH//2 - 100, 275, 200, 50)
        pygame.draw.rect(screen, WHITE, button_player_two)
        text_player_two = font.render("Join game", True, NAVY_BLUE)
        screen.blit(text_player_two, (button_player_two.centerx - text_player_two.get_width()//2, button_player_two.centery - text_player_two.get_height()//2))

        # Create button for Exit
        button_exit = pygame.Rect(WIDTH//2 - 100, 350, 200, 50)
        pygame.draw.rect(screen, WHITE, button_exit)
        text_exit = font.render("Exit", True, NAVY_BLUE)
        screen.blit(text_exit, (button_exit.centerx - text_exit.get_width()//2, button_exit.centery - text_exit.get_height()//2))

        # Update the screen
        pygame.display.flip()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Check if Player One button was clicked
                    if button_player_one.collidepoint(event.pos):
                        threading.Thread(target=handle_client, args=("Server",)).start()
                        play()
                    elif button_player_two.collidepoint(event.pos):
                        # c.send("Client".encode())
                        threading.Thread(target=connect_to_server, args=("Client",)).start()
                        play()
                    elif button_exit.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()



# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battleship")

# Run the menu
display_menu()
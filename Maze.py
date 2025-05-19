import pygame
import numpy as np
import sys

CELL_SIZE = 60
ROWS, COLS = 20, 20
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)

ACTIONS = {
    0: (-1, 0),  # למעלה
    1: (1, 0),   # למטה
    2: (0, -1),  # שמאלה
    3: (0, 1),   # ימינה
}

class Maze:
    def __init__(self):
        self.maze = np.array([
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1],
    [1,0,1,2,0,0,0,1,0,0,0,1,0,0,0,1,0,1,0,1],
    [1,0,1,1,1,1,0,1,1,1,0,1,1,1,0,1,0,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,2,0,1,0,0,0,1,0,1],
    [1,1,1,1,0,1,1,1,0,1,1,1,0,1,0,1,0,1,1,1],
    [1,0,0,0,0,0,2,1,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,0,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,0,0,0,1,1,0,1,0,1,0,1],
    [1,1,1,1,0,1,0,1,0,1,1,1,0,1,0,1,0,1,0,1],
    [1,0,0,0,0,1,0,1,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,0,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1],
    [1,0,1,0,0,0,0,1,2,0,0,1,0,0,0,1,0,0,0,1],
    [1,0,1,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,2,1,0,1],
    [1,1,1,1,0,1,1,1,0,1,1,1,0,1,0,1,0,1,0,1],
    [1,0,0,1,0,1,0,1,0,0,0,1,0,1,0,1,0,0,0,1],
    [1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
])
        self.start_pos = (1, 1)
        self.goal_pos = (18, 18)
        self.wall_colors = [(255, 0, 0), (255, 255, 255)]
        self.last_action = 3

        # בונה מיפוי ממצבים חוקיים למספרים רציפים לטובת למידת חיזוקים
        self.coord_to_index, self.index_to_coord = self.build_state_mappings()
        self.reset()

        self.car_img_original = None
        self.flag_img = None
        self.hole_img = None

    def build_state_mappings(self):
        coord_to_index = {}
        index_to_coord = {}
        index = 0
        for i in range(self.maze.shape[0]):
            for j in range(self.maze.shape[1]):
                if self.maze[i, j] == 0 or self.maze[i, j] == 2:
                    coord_to_index[(i, j)] = index
                    index_to_coord[index] = (i, j)
                    index += 1
        return coord_to_index, index_to_coord

    def load_images(self):
        self.car_img_original = pygame.image.load("assets/car.png").convert_alpha()
        self.flag_img = pygame.image.load("assets/flag.png").convert_alpha()
        self.hole_img = pygame.image.load("assets/hole.png").convert_alpha()
        
        self.car_img_original = pygame.transform.scale(self.car_img_original, (CELL_SIZE, CELL_SIZE))
        self.flag_img = pygame.transform.scale(self.flag_img, (CELL_SIZE, CELL_SIZE))
        self.hole_img = pygame.transform.scale(self.hole_img, (CELL_SIZE, CELL_SIZE))

    def reset(self):
        self.agent_pos = self.start_pos
        self.game_over = False
        return self.get_state()

    def get_state(self):
        return self.coord_to_index[self.agent_pos]

    def get_coord_from_state(self, index):
        return self.index_to_coord[index]

    def step(self, action):
        self.last_action = action
        dx, dy = ACTIONS[action]
        new_x = self.agent_pos[0] + dx
        new_y = self.agent_pos[1] + dy

        if 0 <= new_x < ROWS and 0 <= new_y < COLS and self.maze[new_x, new_y] != 1:
            self.agent_pos = (new_x, new_y)

        fell_in_hole = self.maze[self.agent_pos[0], self.agent_pos[1]] == 2
        reached_goal = self.agent_pos == self.goal_pos

        done = reached_goal or fell_in_hole
        self.game_over = done

        if reached_goal:
            reward = 10
        elif fell_in_hole:
            reward = -10  
        else:
            reward = -0.1

        return self.get_state(), reward, done

    def render(self, screen):
        screen.fill(WHITE)


        for i in range(ROWS):
            for j in range(COLS):
                rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                val = self.maze[i, j]

                if val == 0:
                    pygame.draw.rect(screen, GRAY, rect)
                elif val == 2:  # בור
                    pygame.draw.rect(screen, GRAY, rect)
                    if self.hole_img:
                        screen.blit(self.hole_img, rect)
                else:  # קירות
                    color_index = (i + j) % 2
                    wall_color = self.wall_colors[color_index]
                    pygame.draw.rect(screen, wall_color, rect)

                if (i, j) == self.goal_pos and self.flag_img:
                    screen.blit(self.flag_img, rect)
                    
        # צייר את המכונית
        if not self.game_over and self.car_img_original:
            rect = pygame.Rect(self.agent_pos[1] * CELL_SIZE, self.agent_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if self.last_action == 0:
                car_rotated = pygame.transform.rotate(self.car_img_original, 90)
            elif self.last_action == 1:
                car_rotated = pygame.transform.rotate(self.car_img_original, -90)
            elif self.last_action == 2:
                car_rotated = pygame.transform.rotate(self.car_img_original, 180)
            else:
                car_rotated = self.car_img_original
            screen.blit(car_rotated, rect)
            
        # אם נפלנו לבור, הצג הודעה על המסך
        if self.game_over and self.maze[self.agent_pos[0], self.agent_pos[1]] == 2:
            font = pygame.font.SysFont(None, 72)
            text = font.render("!נפלת לבור", True, (255, 0, 0))
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(text, text_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Project RL - MAZE")
    clock = pygame.time.Clock()

    env = Maze()
    env.load_images()

    state = env.reset()
    done = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        action = None
        if keys[pygame.K_UP]:
            action = 0
        elif keys[pygame.K_DOWN]:
            action = 1
        elif keys[pygame.K_LEFT]:
            action = 2
        elif keys[pygame.K_RIGHT]:
            action = 3

        if action is not None and not done:
            state, reward, done = env.step(action)
            print(f"State (index): {state}, Reward: {reward}, Done: {done}")
            if done:
                if reward > 0:
                    pygame.quit()
                    sys.exit()
                else:
                    # נפילה לבור
                    pygame.quit()
                    sys.exit()

        env.render(screen)
        pygame.display.flip()
        clock.tick(10)


if __name__ == "__main__":
    # הרצת המשחק הרגיל (שליטה ידנית)
    main()
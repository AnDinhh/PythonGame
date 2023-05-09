import pygame as pg
import random as rnd
import turtle
import time
import math
from pygame import mixer
from dataclasses import dataclass

pg.init()
game_state = "start_menu"
#Set chiều rộng, số cột, dòng
width, columns, rows = 400, 15, 30

distance = width // columns # 400/15 = 26
#Set chiều cao
height = distance * rows

#Set lưới
grid = [0] * columns * rows

#Set kích thước cho button 
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_COLOR = (255, 0, 0)
BUTTON_TEXT_COLOR = (255, 255, 255)

#Set tốc độ, điểm, cấp
speed, score, level, temp = 1000, 0, 1, 0

#Âm thanh trò chơi
mixer.init()
start = pg.mixer.Sound("start.wav" )
point = pg.mixer.Sound("score.wav" )
fullrow = pg.mixer.Sound("fullrow.wav" )
rotateSound = pg.mixer.Sound("rotateSound.wav" )

gameOver = 0;

# load hình 
picture = [] # 
for n in range(9):
  picture.append(pg.transform.scale(pg.image.load(f'T_{n}.jpg'), (distance, distance)))

#Khung hình
screen = pg.display.set_mode([width, height])
#Title
pg.display.set_caption('Tetris Game')

#Tạo các sự kiện
tetroromino_down = pg.USEREVENT+1
#speedup = pg.USEREVENT+2
pg.time.set_timer(tetroromino_down, speed)
#pg.time.set_timer(speedup, 30_000) # tốc độ rơi xuống
pg.key.set_repeat(0, 100)
#Pause game
paused = False

#Màn hình chính
show_start_screen = True
screen_start = pg.image.load(r'start.jpg')
screen_start = pg.transform.scale(screen_start, (width, height))
screen_start_rect = screen_start.get_rect(center = (screen.get_rect().center))

#Tetroromino cho các chữ cái O, I, J, L, S, Z, T
tetrorominos = [
              #O
              [0, 1, 1, 0, 
               0, 1, 1, 0, 
               0, 0, 0, 0, 
               0, 0, 0, 0],
              #I
               [0, 2, 0, 0, 
                0, 2, 0, 0, 
                0, 2, 0, 0,
                0, 2, 0, 0], 
               #J
               [0, 0, 3, 0, 
                0, 0, 3, 0, 
                0, 3, 3, 0, 
                0, 0, 0, 0], 
               #L 
               [0, 4, 0, 0, 
                0, 4, 0, 0,
                0, 4, 4, 0, 
                0, 0, 0, 0],
               #S
               [0, 5, 5, 0, 
                5, 5, 0, 0, 
                0, 0, 0, 0, 
                0, 0, 0, 0], 
               #Z
               [6, 6, 0, 0, 
                0, 6, 6, 0, 
                0, 0, 0, 0, 
                0, 0, 0, 0], 
               #T
               [0, 0, 0, 0, 
                7, 7, 7, 0,
                0, 7, 0, 0,
                0, 0, 0, 0]
               ] 
#Font chữ và button
font = pg.font.Font(None, 36)
start_button = pg.Rect((width - BUTTON_WIDTH) // 2, height // 2, BUTTON_WIDTH, BUTTON_HEIGHT)
start_text = font.render("START GAME", True, BUTTON_COLOR)

#Tạo lớp và định nghĩa các hàm
@dataclass

class tetroromino():
  tetro: list
  row: int = 0 # vị trí xuất hiện đầu tiên
  column: int = 5
  def show(self):
    #Màu background
    screen.fill((255, 255, 255))
    
    #Set điểm và cấp cho chúng hiện lên màn hình
    textsurface = pg.font.SysFont('consolas', 40).render(f'{score:,}', False, (255, 255, 255))
    screen.blit(textsurface, (width // 2 - textsurface.get_width() // 2, 5))
    textsurface = pg.font.SysFont('consolas', 20).render(f'Level: {level}', False, (255, 255, 255))
    screen.blit(textsurface, (width // 2 - textsurface.get_width() // 2, 55))
    
    # enumerate tạo list dạng liệt kê
    for n, color in enumerate(self.tetro):
      if color > 0:
        x = (self.column + n % 4) * distance
        y = (self.row + n // 4) * distance
        screen.blit(picture[color], (x, y))

  #Kiểm tra xem một tetromino đã cho có thể được đặt trong một lưới trò chơi được xác định trước hay không
  def check(self, r, c):
    for n, color in enumerate(self.tetro):
      if color > 0:
        rs = r + n // 4
        cs = c + n % 4
        if rs >= rows or cs < 0 or cs >= columns or grid[rs * columns + cs] > 0:
          return False
    return True

  #Cập nhập vị trí mới
  def update(self, r, c):
    if self.check(self.row + r, self.column + c):
      self.row += r
      self.column += c
      return True
    return False

  #Xoay khối gạch
  def rotate(self):
    savetetro = self.tetro.copy()
    for n, color in enumerate(savetetro):
      #Công thức
      self.tetro[(2-(n % 4))*4+(n // 4)] = color
    if not self.check(self.row, self.column):
      self.tetro = savetetro.copy()

  #Dưa các khối trong tetromino xuống lưới và đặt chúng vào vị trí cuối cùng của lưới.
def ObjectOnGridline():
  for n, color in enumerate(character.tetro):
    if color > 0:
      grid[(character.row + n // 4)*columns+(character.column + n % 4)] = color

  #Xoá các dòng đầy 
def DeleteFullRows():
  fullrows = 0
  pg.mixer.Sound.play(point)
  for row in range(rows):
    for column in range(columns):
      #kiểm tra nếu dòng nào có ô rỗng thì bỏ qua
      if grid[row*columns+column] == 0: 
        break
    else:
      del grid[row*columns:row*columns+columns] # [2, 1, 1, 1, 1, 7, 7, 7, 2, 2, 2, 2, 7, 7, 7]
      grid[0:0] = [0]*columns 
      pg.mixer.Sound.play(fullrow) # trả về []
      fullrows += 1
      # xóa càng nhiều dòng cùng lúc điểm càng lũy thừa cao lên nhiều lần
  return fullrows**2*100 

  #Kiểm tra bất kì cột nào đã đầy
def CheckFullColumns():
  count = 0
  for column in range(columns):
        has_empty_cell = False
        for row in range(rows):
            if grid[row*columns+column] == 0:
                has_empty_cell = True
                break
        if not has_empty_cell:
            count += 1
  return count

  #Game Over 
def is_game_over():
    # Kiểm tra xem có cột nào đầy đủ không
    if CheckFullColumns() > 0:
        return True

    # Kiểm tra xem có ô trống ở hàng đầu tiên không
    for column in range(columns):
        if grid[column] == 0:
            return True
    return False
character = tetroromino(rnd.choice(tetrorominos))
  #Vẽ nút "Start game" trên màn hình của trò chơi
def draw_start_button():
    button_x = (width - BUTTON_WIDTH) // 2
    button_y = (height - BUTTON_HEIGHT) // 2
    pg.draw.rect(screen, BUTTON_COLOR, (button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT))

    font = pg.font.Font(None, 36)
    text = font.render("START GAME", True, BUTTON_TEXT_COLOR)
    text_rect = text.get_rect(center=(button_x + BUTTON_WIDTH // 2, button_y + BUTTON_HEIGHT // 2))
    screen.blit(screen_start, screen_start_rect)
    screen.blit(text, text_rect)
    pg.mixer.Sound.play(start)
    
status = True
clock = pg.time.Clock()

def pause_game():
    global paused
    paused = True
    while paused:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p:
                    paused = False
        # Hiển thị một thông báo "Paused" lên màn hình
        textsurface = pg.font.SysFont('consolas', 40).render(f'Paused!', False, (0, 0, 0))
        screen.blit(textsurface, (width // 2 - textsurface.get_width() // 2, 390))
        # Cập nhật màn hình
        pg.display.update()
        clock.tick(10)

status2 = True
while status:
        # Lắng nghe các sự kiện từ bàn phím và chuột
  for event in pg.event.get():
    if event.type == pg.QUIT:
      pg.quit()
    elif event.type == pg.MOUSEBUTTONUP:
      # Bắt đầu trò chơi nếu nhấn chuột trái vào nút "START GAME"
      if start_button.collidepoint(event.pos):
        while status2:
          clock.tick(80)
          pg.time.delay(100)
          for event in pg.event.get():
            if event.type == pg.QUIT:
              pg.quit()
              status2 = False
            if event.type == tetroromino_down:
              
              # kiểm tra khi mỗi chữ cái được đặt xong tại một vị trí
              if not character.update(1, 0):
                ObjectOnGridline()
                
                gameOver = CheckFullColumns()
                if gameOver > 0 :
                  pg.quit()
                score += DeleteFullRows() 
                if score > 0 and score//500 >= level and temp != score:
                  speed = int(speed * 0.8)
                  pg.time.set_timer(tetroromino_down, speed)
                  level = score // 500 + 1
                  temp = score 
                character = tetroromino(rnd.choice(tetrorominos))
            if event.type == pg.KEYDOWN:
              if event.key == pg.K_LEFT:
                #dòng không đổi, cột giảm 1
                character.update(0, -1) 
              if event.key == pg.K_RIGHT:
                character.update(0, 1)
              if event.key == pg.K_DOWN:
                character.update(1, 0)
              if event.key == pg.K_SPACE:
                character.rotate()
                pg.mixer.Sound.play(rotateSound)
              if event.key == pg.K_p:
                pause_game()
          character.show()
          for n, color in enumerate(grid):
            if color > 0:
              x = n % columns * distance
              y = n // columns * distance
              screen.blit(picture[color], (x, y))
          pg.display.flip()


  # Vẽ nút bắt đầu trò chơi lên màn hình
  draw_start_button()
  # Cập nhật màn hình
  pg.display.update()
              
pg.quit()
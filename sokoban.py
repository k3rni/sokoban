#! /usr/bin/env python
# encoding: utf-8

import curses, os, atexit

class Board:
  def __init__(self, screen, width, height, lines):
    self.screen = screen
    self.height = height
    self.width = width
    self.lines = lines

  def at(self, x, y):
    return self.lines[y][x]

  def set(self, x, y, value):
    # w pythonie stringi są immutable
    # self.lines[y][x] = value
    self.lines[y] = self.lines[y][:x] + value + self.lines[y][x+1:]

  def player_x(self):
    line = self.lines[self.player_y()]
    return line.index('*')

  def player_y(self):
    for i in range(self.height):
      if '*' in self.lines[i]:
        return i

  def can_move(self, direction):
    # w danym kierunku jest puste
    # lub ciag kamieni i puste
    x = self.player_x()
    y = self.player_y()
    if direction == 'left':
      for i in range(x - 1, 0, -1):
        p = self.at(i, y)
        if p == '.': return True
        elif p == '#': return False
    elif direction == 'right':
      for i in range(x + 1, self.width):
        p = self.at(i, y)
        if p == '.': return True
        elif p == '#': return False
    elif direction == 'up':
      for i in range(y - 1, 0, -1):
        p = self.at(x, i)
        if p == '.': return True
        elif p == '#': return False
    elif direction == 'down':
      for i in range(y + 1, self.height):
        p = self.at(x, i)
        if p == '.': return True
        elif p == '#': return False


  def move(self, direction):
    x = self.player_x()
    y = self.player_y()
    if direction == 'up':
      wy = y
      while self.at(x, wy) != '.': wy -= 1
      for i in range(wy, y):
        self.set(x, i, self.at(x, i+1))
      self.set(x, y, '.')
    elif direction == 'down':
      wy = y
      while self.at(x, wy) != '.': wy += 1
      for i in range(wy, y, -1):
        self.set(x, i, self.at(x, i-1))
      self.set(x, y, '.')
    elif direction == 'left':
      wx = x
      while self.at(wx, y) != '.': wx -= 1
      for i in range(wx, x):
        self.set(i, y, self.at(i+1, y))
      self.set(x, y, '.')
    elif direction == 'right':
      wx = x
      # 1.znajdz pierwsze puste z prawej
      while self.at(wx, y) != '.': wx += 1
      # 2.wszystko pomiedzy graczem a tym pustym przesun o 1 w prawo (to przesunie rowniez gracza)
      for i in range(wx, x, -1):
        self.set(i, y, self.at(i-1, y))
      # 3. za gracza postaw puste
      self.set(x, y, '.')


  def draw(self, x):
    for i in range(self.height):
      screen.addstr(i, x, self.lines[i])

  def __eq__(self, other):
    for i in range(self.height):
      for j in range(self.width):
        if self.at(j, i) != other.at(j, i):
          return False
    return True

class Sokoban:
  def __init__(self, screen, filename):
    self.screen = screen
    self.load_boards(filename)

  def load_boards(self, filename):
    with open(filename) as f:
      line = f.readline()
      width, height = [int(val) for val in line.split()]
      start_lines = []
      for i in range(height):
        start_lines.append(f.readline())
      f.readline() # separator
      dest_lines = []
      for i in range(height):
        dest_lines.append(f.readline())
      self.board = Board(self.screen, width, height, start_lines)
      self.target = Board(self.screen, width, height, dest_lines)

  def draw(self):
    self.screen.clear()
    h, w = screen.getmaxyx()
    self.board.draw(0)
    self.target.draw(w/2)

  def handle_key(self, key):
    if key == curses.KEY_UP:
      return self.move('up')
    elif key == curses.KEY_DOWN:
      return self.move('down')
    elif key == curses.KEY_LEFT:
      return self.move('left')
    elif key == curses.KEY_RIGHT:
      return self.move('right')
    elif key == ord('S'):
      return SaveGamePrompt(self.screen)
    elif key == 27: # escape
      return 'quit'

  def move(self, direction):
    if self.board.can_move(direction):
      self.board.move(direction)
    if self.check_victory():
      self.screen.clear()
      h, w = self.screen.getmaxyx()
      text = 'Udalo sie! Wygrales'
      self.screen.addstr(h/2, w/2 - len(text)/2, text)
      self.screen.getch()
      return 'quit'

  def check_victory(self):
    return (self.board == self.target)


class FileBrowser(object):
  def __init__(self, parent, screen, pattern):
    self.screen = screen
    self.current_option = 0
    self.files = [filename for filename in os.listdir('.') if filename.endswith(pattern)]

  def draw(self):
    screen.clear()
    h, w = screen.getmaxyx()
    h0 = h /2 - len(self.files) / 2
    for i, filename in enumerate(self.files):
      if i == self.current_option:
        text = "> %s <" % filename
      else:
        text = filename
      screen.addstr(h0 + i, w/2 - len(text)/2, text)

  def handle_key(self, key):
    if key == curses.KEY_UP:
      self.current_option = max(0, self.current_option - 1)
    elif key == curses.KEY_DOWN:
      self.current_option = min(self.current_option + 1, len(self.files) - 1)
    elif key == 27: # escape
      return 'quit'
    elif key == 10:
      return self.files[self.current_option]


class LevelBrowser(FileBrowser):
  def __init__(self, parent, screen):
    FileBrowser.__init__(self, parent, screen, '.sbl')

  def handle_cmd(self, filename):
    return Sokoban(self.screen, filename)

class SaveGameBrowser(FileBrowser):
  def __init__(self, parent, screen):
    FileBrowser.__init__(self, parent, screen, '.sbs')

  def handle_cmd(self, filename):
    return Sokoban(self.screen, filename)

class Menu:
  def __init__(self, screen):
    self.options = [
        ('Nowa gra', 'new_game'),
        ('Wczytaj', 'load_game'),
        ('Wyjdz', 'quit')
        ]
    self.current_option = 0
    self.screen = screen

  def draw(self):
     screen.clear()
     h, w = screen.getmaxyx()
     h0 = h / 2 - len(self.options) / 2
     for (i, (opt, cmd)) in enumerate(self.options):
       if i == self.current_option:
         text = "> %s <" % opt
       else:
         text = opt
       screen.addstr(h0+i, w/2 - len(text)/2, text)

  def handle_key(self, key):
    if key == curses.KEY_UP:
      self.current_option = max(0, self.current_option - 1)
    elif key == curses.KEY_DOWN:
      self.current_option = min(self.current_option + 1, len(self.options) - 1)
    elif key == 27: # escape
      return 'quit'
    elif key == 10:
      return self.options[self.current_option][1]


  def handle_cmd(self, cmd):
    if cmd == 'new_game':
      return LevelBrowser(self, screen)
    elif cmd == 'load_game':
      return SaveGameBrowser(self, screen)


def interact(obj, screen):
  while True:
    obj.draw()
    key = screen.getch()
    result = obj.handle_key(key)
    if result == 'quit':
      return
    elif result:
      interact(obj.handle_cmd(result), screen)
    

if __name__ == "__main__":
  # atexit.register(curses.endwin)
  screen = curses.initscr()
  curses.curs_set(0)
  screen.immedok(True)
  screen.keypad(True)
  menu = Menu(screen)
  interact(menu, screen)
  curses.endwin()



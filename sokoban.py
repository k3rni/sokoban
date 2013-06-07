#! /usr/bin/env python
# encoding: utf-8

import curses, os, atexit

class Board:
  def __init__(self, screen):
    self.screen = screen

  def draw(self):
    pass

class Sokoban:
  def __init__(self, filename):
    self.board, self.target_board = load_boards(filename)

  def move(self, direction):
    pass

  def can_move(self, direction):
    pass

  def check_victory(self):
    return (self.board == self.target_board)


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
      self.current_option = min(self.current_option + 1, len(self.options) - 1)
    elif key == 27: # escape
      return 'quit'
    elif key == 10:
      return self.files[self.current_option]


class LevelBrowser(FileBrowser):
  def __init__(self, parent, screen):
    FileBrowser.__init__(self, parent, screen, '.sbl')

  def handle_cmd(self, filename):
    return Sokoban(filename)

class SaveGameBrowser(FileBrowser):
  def __init__(self, parent, screen):
    FileBrowser.__init__(self, parent, screen, '.sbs')

  def handle_cmd(self, filename):
    return Sokoban(filename)

class Menu:
  def __init__(self, screen):
    self.options = [
        ('Nowa gra', 'new_game'),
        ('Wczytaj', 'load_game'),
        ('Wyjdź', 'quit')
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
  screen.immedok(True)
  screen.keypad(True)
  menu = Menu(screen)
  interact(menu, screen)
  curses.endwin()



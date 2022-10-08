import curses
import random
import numpy

class Tile:
    def __init__(self, is_hidden = True, is_bomb = False, bombs_around = 0):
        self.is_bomb = is_bomb
        self.is_hidden = is_hidden
        self.is_marked = False
        self.bombs_around = bombs_around
    
    def show(self):
        draw = ' ' if self.bombs_around == 0 else str(self.bombs_around)
        draw = '*' if self.is_bomb   else draw
        draw = '~' if self.is_hidden else draw
        draw = '!' if self.is_marked else draw
        return draw

class Field:
    def __init__(self, size: list, bomb_count: int):
        self.size = size
        self.bomb_count = bomb_count
        self.bombs = []
        self.generate_bombs()
        self.generate_field()


    def generate_bombs(self):
        #generating bomb list to write to field data
        self.bombs.clear()
        counter = 0
        while counter < self.bomb_count:
            this_bomb = (
                        random.randint(0, self.size[0]-1), 
                        random.randint(0, self.size[1]-1),
                        )
            if this_bomb not in self.bombs:
                self.bombs.append(this_bomb)
                counter+=1
            else:
                pass
    
    def valid_surroundings(self, coords: tuple):
        #includes both valid and not valid neighbours
        surroundings = [
                        (x, y) for x in range(coords[0]-1, coords[0]+2) 
                               for y in range(coords[1]-1, coords[1]+2)
                       ]
        print(surroundings)
        surroundings.remove(coords) #remove coord we got as an input
        #replacing all invalid coords with None
        for xypair in surroundings:
            notvalid = ((xypair[0] < 0) or (xypair[0] >= self.size[0]) or (xypair[1] < 0) or (xypair[1] >= self.size[1]))
            print(xypair, notvalid)
            if notvalid:
                surroundings[surroundings.index(xypair)] = None
        return [item for item in surroundings if item != None] #returns everything but None

    def count_neighbours(self, coords: tuple): # counts all bombs around given coords
        #generates all possible surrounding coordinates (even those out of bound since we don't really care)
        surroundings = [
                        (x, y) for x in range(coords[0]-1, coords[0]+2) 
                               for y in range(coords[1]-1, coords[1]+2)
                       ]
        bombs_around = sum([1 for i in surroundings if i in self.bombs])
        return bombs_around

    def generate_field(self):
        self.field = []
        for y in range(self.size[1]):
            self.field.append([])
            for x in range(self.size[0]):
                tile = Tile(is_bomb = (x, y) in self.bombs, bombs_around = self.count_neighbours((x, y)))
                self.field[y].append(tile)
        self.field = numpy.array(self.field)
    
    def show(self, cheats = False):
        fieldstr = '\n'.join([''.join([self.field[x, y].show() for x in range(len(self.field[y]))]) for y in range(len(self.field))])
        return fieldstr

    #TODO:
    def dig(self, coords: tuple):
        if not self.field[coords].is_hidden:
            return 'bruh'
        if self.field[coords].is_bomb:
            #bomb go boom here
            return 69
        self.field[coords].is_hidden = False
        if self.field[coords].bombs_around == 0:
            surroundings = self.valid_surroundings(coords)
            for coord in surroundings:
                self.dig(coord) #recursive part that allowes to do continious digging until we get closer to bombs
            return
    def mark(self, coords: tuple):
        if self.field[coords].is_hidden:
            self.field[coords].is_marked = True
        return
        
class App:
    def __init__(self):
        screen = curses.initscr()
        curses.noecho()
        curses.cbreak()

        
        
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    def field_box(self, field):
        pass

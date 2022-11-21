import curses
import field
import logging

logging.basicConfig(filename='latest.log', encoding='utf-8', level=logging.DEBUG)

class App:
    def __init__(self, stdsrc, start_from='menu'):
        curses.curs_set(0)
        curses.mousemask(1)
        self.screen = stdsrc
        self.appsize = (45,30)
        self.panels = {
                'menu':Menu(),
                'game':Field(),
                'settings':Settings(),
                }

        
        if start_from in self.panels.keys():
            panel = self.panels[start_from]

        self.screen.refresh()
        event = None
        while event != curses.KEY_EXIT:
            reply = panel.update(event)
            if reply is not None:
                if 'changepanel' in reply.keys():
                    panel = self.panels[reply['changepanel']]
                    panel.takedata(reply['callback_data'])
                    panel.update('genericupdate')
                if 'gamestatus' in reply.keys():
                    if reply['gamestatus'] == 69:
                        break
            event = self.screen.getch()
        
    def chksize(self): # checks if app can fit in available terminal size. Returns False if it can't
        available_size = (curses.COLS, curses.LINES)
        print(available_size, self.appsize)
        for dim in range(2):
            if available_size[dim]<self.appsize[dim]:
                return False
        return True


class Menu:
    def __init__(self):
        self.init_colors()
        self.size = (16, 5)
        self.posx = (curses.COLS - self.size[0])//2
        self.posy = (curses.LINES - self.size[1])//2
        self.selection_tree = {
                'new game':
                    {
                    '9x9-10*':{
                        'callback_data':((9, 9), 10),
                        'callback':self.new_game,
                        },
                    '16x16-40*':{
                        'callback_data':((16, 16), 40),
                        'callback':self.new_game,
                        },
                    '30x16-99*':{
                        'callback_data':((30, 16), 99),
                        'callback':self.new_game,
                        },
		    	    },

                'continue':{
		    	    },

                'settings':{
		    	    },
                }
        self.window = curses.newwin(self.size[1], self.size[0], self.posy, self.posx)
        self.rooted = self.selection_tree
        self.options = list(self.rooted.keys())
        self.selection = 0
    def takedata(self, data):
        pass

    def init_colors(self):
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        self.DEFAULT = curses.color_pair(1)
        self.SELECTED = curses.color_pair(2)

    def new_game(self, callback_data):
        return {'changepanel':'game', 'callback_data':callback_data}
        

    def update(self, event): #changes some internal state according to event where event is some key being pressed
        #logging.debug(f'Menu.update() - {self.selection, self.options, self.rooted}')
        reply = None
        valid_keys = {
                curses.KEY_UP    : -1,
                curses.KEY_DOWN  :  1,
                ord('w') : -1,
                ord('s') : 1
                }
        if event in valid_keys.keys():
            self.selection += valid_keys[event]
            self.selection = len(self.options)-1 if self.selection < 0 else self.selection # lower border tresspassing prevention
            self.selection = 0 if self.selection >= len(self.options) else self.selection # upper border tresspassing prevention
        #if event == curses.KEY_ENTER:
        keys_next = [10, ord('d')]
        keys_prev = [ord('a'), curses.KEY_BACKSPACE]
        if event in keys_next:
            reply = self.select()
        if event in keys_prev:
            self.deselect()
        self.render()
        return reply
        
    def select(self):
        if not ('callback' in self.rooted[self.options[self.selection]].keys()):
            self.rooted = self.rooted[self.options[self.selection]]
            self.options = list(self.rooted.keys())
        else: 
            return self.new_game(callback_data = self.rooted[self.options[self.selection]]['callback_data'])
    def deselect(self):
        self.rooted = self.selection_tree
        self.options = list(self.rooted.keys())

    def render(self):
        self.window.erase()
        self.window.box()
        for idx, item in enumerate(self.options):
            if idx != self.selection:
                self.window.addstr(idx+1, 1, item, self.DEFAULT)
            else:
                self.window.addstr(idx+1, 1, f'>{item}', self.SELECTED)
        self.window.refresh()
                

class Field:
    def __init__(self):
        self.size = (45,30) # aka default values before game starts (Field is initiated from the start)
        self.bombs = 0
        self.field = None
    def takedata(self, callback_data):
        self.size = callback_data[0]
        self.bombs = callback_data[1]
        self.posx = (curses.COLS - self.size[0])//2
        self.posy = (curses.LINES - self.size[1])//2
        self.window = curses.newwin(self.size[1]+2, self.size[0]+2, self.posy, self.posx) # +2 adds space for box chars
        self.field = field.Field(size = self.size, bomb_count = self.bombs)
    def update(self, event):
        if event == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse() #coords are relative to stdsrc, not window this class creates
            finx, finy = mx-self.posx-1, my-self.posy-1 # and here we convert them into something related to our window
            if not (0<finx<self.size[0] and 0<finy<self.size[1]): 
                return None
            response = self.field.dig((finx,finy))
            render_data = self.field.show()
            if response == 69:
                render_data.append('BOOM!')
            self.render(render_data)
            return {'gamestatus':response}
        if event == 'genericupdate':
            self.render(self.field.show())
    def render(self, render_data: list):
        self.window.erase()
        self.window.box()
        for idx, row in enumerate(render_data):
            #self.window.addstr(self.posy+1+idx, self.posx+1, row)
            self.window.addstr(idx+1,1,row)
        self.window.refresh()
        
class Settings:
    def __init__(self):
        pass

#curses.wrapper(App)


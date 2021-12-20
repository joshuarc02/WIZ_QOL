import subprocess
import win32gui
import pyautogui
import time
import cv2
from PIL import Image, ImageDraw
#stole a lot of code from https://github.com/Jacob124/wizAPI 


class Wiz_Bot:
    def __init__(self):
        self.handle = 0
        self.path = "C:\ProgramData\KingsIsle Entertainment\Wizard101\Wizard101.exe"
        self.name = "Wizard101"
        self.threshold = .05
        self.handle_cord = None
        self.width = 1
        self.height = 1
        self.screen = None
        with open('login_info') as f:
            self.username = f.readline().strip()
            self.password = f.readline().strip()


    def open_program(self):
        self.find_window()
        if self.handle == 0:
            subprocess.run(self.path)

    def find_window(self):
        self.handle = win32gui.FindWindow(None, self.name)
    
    def wait_for_window(self):
        while self.handle == 0:
            self.find_window()

    def set_active(self):
        self.find_window()
        if self.handle != win32gui.GetForegroundWindow():
            pyautogui.press('alt')
            win32gui.SetForegroundWindow(self.handle)
            pyautogui.press('alt')

    def get_dimensions(self):
        self.set_active()
        dim = win32gui.GetWindowRect(self.handle)
        self.width = dim[2]
        self.height = dim[3]
        self.handle_cord = (dim[0], dim[1])
        return (dim[0], dim[1], dim[2] - dim[0], dim[3] - dim[1])

    def screenshot(self):
        path = self.name + ".PNG"
        self.set_active()

        dim = self.get_dimensions()
        pyautogui.screenshot(path, region=dim)

        self.screen = cv2.imread(path)
        return self.screen

    def match_img(self, sml_img, lrg_img):
        method = cv2.TM_SQDIFF_NORMED

        h, w, = sml_img.shape[:-1]

        result = cv2.matchTemplate(sml_img, lrg_img, method)

        # We want the minimum squared difference
        mn, _, mnLoc, _ = cv2.minMaxLoc(result)

        print(mn)
        if (mn >= self.threshold):
            return False

        cords = self.handle_cord
        x, y = (mnLoc[0] + cords[0], mnLoc[1] + cords[1])
        return (x + (w * 0.5), y + (h * 0.5))

    def fix_img_path(path):
        print("imgs\\" + path + ".PNG")
        return "imgs\\" + path + ".PNG"

    def wait_for_load(self, path):
        path = Wiz_Bot.fix_img_path(path)
        img = cv2.imread(path)
        window = self.screenshot()
        cords = False
        while not cords:
            window = self.screenshot()
            cords = self.match_img(img, window)
            time.sleep(.25)
        return cords

    def click_img(self, path):
        path = Wiz_Bot.fix_img_path(path)
        img = cv2.imread(path)
        self.set_active()
        window = self.screenshot()
        cords = self.match_img(img, window)
        pyautogui.click(cords)
        pyautogui.click()
    
    def click_when_loaded(self, path):
        cords = self.wait_for_load(path)
        pyautogui.click(cords)
        pyautogui.click()
        
    def start(self):
        self.open_program()
        self.wait_for_window()

    def login(self):
        self.set_active()

        self.click_when_loaded("login_bar")

        pyautogui.press('tab')
        pyautogui.write(self.username)

        pyautogui.press('tab')
        pyautogui.write(self.password)

        self.click_img("login_button")

        self.click_when_loaded("play_button")

    def wait_for_window_changes(self):
        changes = 0
        old_handle = self.handle
        while changes < 2:
            self.find_window()
            if self.handle != old_handle:
                changes+=1
            old_handle = self.handle

    def load_game(self):
        self.wait_for_window_changes()
        self.set_active()
        self.click_when_loaded("star")
        pyautogui.click()
        time.sleep(2)
        self.click_when_loaded("character_play_button")
        pyautogui.click()


    def run(self):
        self.start()
        self.login()
        self.load_game()

    def warp_home(self):
        self.set_active()
        self.click_when_loaded("home_warp")
        pyautogui.click()

    def go_to_home_world_gate(self):
        self.set_active()
        self.wait_for_load("home")
        world_gate = cv2.imread(Wiz_Bot.fix_img_path("world_gate"))
        pyautogui.keyDown("s")
        while not self.match_img(world_gate, self.screenshot()):
            time.sleep(.5)
        pyautogui.keyUp("s")
        pyautogui.press("x")

    def go_to_world(self, world):
        self.set_active()
        self.click_when_loaded("wizard_city")
        self.click_img("go_to_world")

    def go_to_wiz_commons(self):
        self.set_active()
        mr_licncoln = cv2.imread(Wiz_Bot.fix_img_path("mr_licncoln"))
        pyautogui.keyDown("w")
        while not self.match_img(mr_licncoln, self.screenshot()):
            time.sleep(.1)
        time.sleep(1)
        pyautogui.keyUp("w")
        
    def press_key(key, t):
        pyautogui.keyDown(key)
        time.sleep(t)
        pyautogui.keyUp(key)

    def go_to_minigames(self):
        self.set_active()
        self.wait_for_load("commons_roof")
        pyautogui.keyDown("w")
        Wiz_Bot.press_key("d", .3)
        time.sleep(1)
        Wiz_Bot.press_key("d", .2)
        time.sleep(3)
        Wiz_Bot.press_key("a", .5)
        time.sleep(.5)
        Wiz_Bot.press_key("a", .4)
        time.sleep(.5)
        pyautogui.keyUp("w")

    def select_potion_minigame(self):
        self.set_active()
        self.click_when_loaded("minigame_start")
        pyautogui.press("x")
        self.click_when_loaded("potion_motion")
    
    def play_potion_motion(self, num_potions):

        x_count = 6
        y_count = 6

        def get_colors():
            img = self.screenshot()

            square = [[1] * x_count for t in range(y_count)]
            
            square_size = self.width / 19.5
            start_x = int(self.width / 3 + self.width / 72)
            start_y = int(self.height / 3)

            y = start_y
            for _y in range(y_count):
                x = start_x
                for _x in range(x_count):
                    cords = int(y),int(x)
                    color = img[cords]
                    square[_y][_x] = ((color[0] << 16) + (color[1] << 8) + (color[2]), (int(x), int(y)))
                    x += square_size
                y += square_size

            print(square)
            return square

        def drag_nearest_similar():
            def equals(color1, color2, threshold=1000):
                return abs(color1-color2) < threshold
            checked = []

            def check_neighbors(cords, color):
                x, y = cords[0], cords[1]
                if cords in checked:
                    return
                checked.append(cords)
                #check N
                N_y = (cur_y + y_count - 1) % y_count
                N_cords = (x, N_y)
                N_color = square[N_y][x][0]
                if equals(color, N_color):
                    check_neighbors(N_cords, color)
                
                #check E
                E_x = (cur_x + x_count - 1) % x_count
                E_cords = (E_x, y)
                E_color = square[y][E_x][0]
                if equals(color, E_color):
                    check_neighbors(E_cords, color)

                #check S
                S_y = (cur_y + y_count + 1) % y_count
                S_cords = (x, S_y)
                S_color = square[S_y][x][0]
                if equals(color, S_color):
                    check_neighbors(S_cords, color)
                print(S_cords, S_cords in checked)
                print(checked)

                #check W
                W_x = (cur_x + x_count + 1) % x_count
                W_cords = (W_x, y)
                W_color = square[y][W_x][0]
                if equals(color, W_color):
                    check_neighbors(W_cords, color)

            delay = .14

            square = get_colors()
            for cur_y in range(y_count):
                for cur_x in range(x_count):
                    cur_potion = square[cur_y][cur_x]
                    cur_cords = cur_potion[1]
                    cur_color = cur_potion[0]
                    #checking nearby rows?
                    for x in range(x_count):
                        checked = [(cur_x, cur_y)]
                        cords = (x, cur_y)
                        check_neighbors(cords, cur_color)
                        if len(checked) > 2:
                            pix_x, pix_y = square[cur_y][x][1]
                            pyautogui.moveTo(cur_cords)
                            pyautogui.dragTo(pix_x, pix_y, delay, button="left")

                    #checking neareby cols?
                    for y in range(y_count):
                        checked = [(cur_x, cur_y)]
                        cords = (cur_x, y)
                        check_neighbors(cords, cur_color)
                        if len(checked) > 2:
                            pix_x, pix_y = square[y][cur_x][1]
                            pyautogui.moveTo(cur_cords)
                            pyautogui.dragTo(pix_x, pix_y, delay, button="left")
                        

        for i in range(num_potions):
            self.click_when_loaded("play_minigame")

            level_3_minigame = cv2.imread(Wiz_Bot.fix_img_path("level_3_minigame"))
            while not self.match_img(level_3_minigame, self.screen):
                drag_nearest_similar()
            self.click_img("minigame_x")
            self.click_when_loaded("minigame_continue")

    def auto_potion_up(self):
        self.warp_home()
        self.go_to_home_world_gate()
        self.go_to_world("wizard_city")
        self.go_to_wiz_commons()
        self.go_to_minigames()
        self.select_potion_minigame()
        #self.play_potion_motion(3)
        

def main():
    wb = Wiz_Bot()
    wb.run()
    wb.auto_potion_up()



main()
""" import cProfile, pstats, io
from pstats import SortKey
pr = cProfile.Profile()
pr.enable()
main()
pr.disable()
s = io.StringIO()
sortby = SortKey.CUMULATIVE
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue()) """
import subprocess
import win32gui
import pyautogui
import time
import cv2
#stole a lot of code from https://github.com/Jacob124/wizAPI 


class Wiz_Bot:
    def __init__(self):
        self.handle = 0
        self.path = "C:\ProgramData\KingsIsle Entertainment\Wizard101\Wizard101.exe"
        self.name = "Wizard101"
        self.threshold = .1
        self.handle_cord = None
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
        if self.handle != win32gui.GetForegroundWindow():
            pyautogui.press('alt')
            win32gui.SetForegroundWindow(self.handle)
            pyautogui.press('alt')

    def get_dimensions(self):
        self.set_active()
        dim = win32gui.GetWindowRect(self.handle)
        self.handle_cord = (dim[0], dim[1])
        return (dim[0], dim[1], dim[2] - dim[0], dim[3] - dim[1])

    def screenshot(self):
        path = self.name + ".PNG"
        self.set_active()

        dim = self.get_dimensions()
        pyautogui.screenshot(path, region=dim)
        image = cv2.imread(path)
        return image

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

    def wait_for_load(self, img):
        window = self.screenshot()
        cords = False
        while not cords:
            window = self.screenshot()
            cords = self.match_img(img, window)
            time.sleep(.5)
        return cords

    def click_img(self, img):
        self.set_active()
        window = self.screenshot()
        cords = self.match_img(img, window)
        pyautogui.click(cords)
    
    def click_when_loaded(self, path):
        img = cv2.imread(path)
        cords = self.wait_for_load(img)
        pyautogui.click(cords)

        
    def start(self):
        self.open_program()
        self.wait_for_window()

    def login(self):
        self.set_active()

        self.click_when_loaded("imgs\\login_bar.PNG")

        pyautogui.press('tab')
        pyautogui.write(self.username)

        pyautogui.press('tab')
        pyautogui.write(self.password)

        img = cv2.imread("imgs\\login_button.PNG")
        self.click_img(img)

        self.click_when_loaded("imgs\\play_button.PNG")

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
        self.click_when_loaded("imgs\\star.PNG")
        pyautogui.click()
        time.sleep(2)
        self.click_when_loaded("imgs\\character_play_button.PNG")
        pyautogui.click()


    def run(self):
        self.start()
        self.login()
        self.load_game()


WB = Wiz_Bot()
WB.run()




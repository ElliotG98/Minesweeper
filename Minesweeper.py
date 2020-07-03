from tkinter import *
from tkinter import messagebox
from collections import deque
import platform
import random
from datetime import datetime

SIZE_X = 10
SIZE_Y = 10

STATE_DEFAULT = 0
STATE_CLICKED = 1
STATE_FLAGGED = 2

BTN_CLICK = "<Button-1>"
BTN_FLAG = "<Button-2>" if platform.system() == 'Darwin' else '<Button-3>'

DIFFICULTY = [
    "EASY",
    "MEDIUM",
    "HARD"
]

master = Tk()
variable = StringVar()
variable.set(DIFFICULTY[0])


class Minesweeper:
    def __init__(self, tk):
        # SET UP FRAME
        self.tk = tk
        self.frame = Frame(self.tk)
        self.frame.pack()

        # INIT assets
        self.assets = {
            "plain": PhotoImage(file="assets/tile_plain.gif"),
            "clicked": PhotoImage(file="assets/tile_clicked.gif"),
            "mine": PhotoImage(file="assets/tile_mine.gif"),
            "flag": PhotoImage(file="assets/tile_flag.gif"),
            "wrong": PhotoImage(file="assets/tile_wrong.gif"),
            "numbers": []
        }
        for i in range(1, 9):
            self.assets["numbers"].append(PhotoImage(file="assets/tile_" + str(i) + ".gif"))

        # SET UP LABELS
        self.labels = {
            "time": Label(self.frame, text="00:00:00"),
            "difficulty": Label(self.frame, text=OptionMenu(master, variable, *DIFFICULTY, command=self.difficulty_options).pack(anchor=E)),
            "mines": Label(self.frame, text="Mines: 0"),
            "flags": Label(self.frame, text="Flags: 0")
        }
        self.labels["time"].grid(row=0, column=0, columnspan=int(SIZE_Y/2))  # TOP LEFT
        self.labels["difficulty"].grid(row=0, column=int(SIZE_Y/2-1), columnspan=int(SIZE_Y/2))  # TOP RIGHT
        self.labels["mines"].grid(row=SIZE_X+1, column=0, columnspan=int(SIZE_Y/2))  # BOTTOM LEFT
        self.labels["flags"].grid(row=SIZE_X+1, column=int(SIZE_Y/2-1), columnspan=int(SIZE_Y/2))  # BOTTOM RIGHT

        # CREATE FLAG AND CLICKED TILE VARIABLES
        self.flag_count = 0
        self.correct_flag_count = 0
        self.clicked_count = 0
        self.start_time = None

        # CREATE BUTTONS
        self.tiles = dict({})
        self.mines = 0

        self.restart()  # START GAME
        self.update_timer()  # INIT TIMER

    # SET DIFFICULTY OPTIONS
    @staticmethod
    def difficulty_options(value):
        if value is DIFFICULTY[0]:
            pass
        elif value is DIFFICULTY[1]:
            pass
        else:
            pass

    def setup(self):
        # CREATE BUTTONS
        for i in range(0, SIZE_X):
            for j in range(0, SIZE_Y):
                # RESET X ON NEW Y ROW
                if j == 0:
                    self.tiles[i] = {}

                tile_id = str(i) + "_" + str(j)
                is_mine = False

                # TILE ASSET CHANGEABLE
                default_tile = self.assets["plain"]

                # RANDOM AMOUNT OF MINES
                if random.uniform(0.0, 1.0) < 0.1:
                    is_mine = True
                    self.mines += 1

                tile = {
                    "id": tile_id,
                    "is_mine": is_mine,
                    "state": STATE_DEFAULT,
                    "coords": {
                        "x": i,
                        "y": j
                    },
                    "button": Button(self.frame, image=default_tile),
                    "mines": 0  # CALCULATED LATER
                }

                tile["button"].bind(BTN_CLICK, self.on_click_wrapper(i, j))
                tile["button"].bind(BTN_FLAG, self.on_right_click_wrapper(i, j))
                tile["button"].grid(row=i+1, column=j)  # OFF SET BY 1 ROW FOR TIMER

                self.tiles[i][j] = tile

        for i in range(0, SIZE_X):
            for j in range(0, SIZE_Y):
                mine_count = 0
                for n in self.get_neighbours(i, j):
                    mine_count += 1 if n["is_mine"] else 0
                self.tiles[i][j]["mines"] = mine_count

    def restart(self):
        self.setup()
        self.refresh_labels()

    def refresh_labels(self):
        self.labels["flags"].config(text="Flags: " + str(self.flag_count))
        self.labels["mines"].config(text="Mines: " + str(self.mines))

    def on_click_wrapper(self, x, y):
        return lambda button: self.on_click(self.tiles[x][y])

    def on_right_click_wrapper(self, x, y):
        return lambda button: self.on_right_click(self.tiles[x][y])

    def update_timer(self):
        ts = "00:00:00"
        if self.start_time is not None:
            delta = datetime.now() - self.start_time
            ts = str(delta).split('.')[0]  # drop ms
            if delta.total_seconds() < 36000:
                ts = "0" + ts  # zero-pad
        self.labels["time"].config(text=ts)
        self.frame.after(100, self.update_timer)

    def on_click(self, tile):
        if self.start_time is None:
            self.start_time = datetime.now()

        if tile["is_mine"]:
            # GAME OVER
            self.game_over(False)
            return

        # CHANGE ASSET
        if tile["mines"] == 0:
            tile["button"].config(image=self.assets["clicked"])
            self.clear_surrounding_tiles(tile["id"])
        else:
            tile["button"].config(image=self.assets["numbers"][tile["mines"]-1])
        if tile["state"] is not STATE_CLICKED:
            tile["state"] = STATE_CLICKED
            self.clicked_count += 1
        if self.clicked_count == (SIZE_X * SIZE_Y) - self.mines:
            self.game_over(True)

    def on_right_click(self, tile):
        if self.start_time is None:
            self.start_time = datetime.now()

        # IF NOT CLICKED
        if tile["state"] is STATE_DEFAULT:
            tile["button"].config(image=self.assets["flag"])
            tile["state"] = STATE_FLAGGED
            tile["button"].unbind(BTN_CLICK)
            # IF A MINE
            if tile["is_mine"]:
                self.correct_flag_count += 1
            self.flag_count += 1
            self.refresh_labels()
        # IF FLAGGED, UN-FLAG
        elif tile["state"] is STATE_FLAGGED:
            tile["button"].config(image=self.assets["plain"])
            tile["state"] = 0
            tile["button"].bind(BTN_CLICK, self.on_click_wrapper(tile["coords"]["x"], tile["coords"]["y"]))
            # IF A MINE
            if tile["is_mine"]:
                self.correct_flag_count -= 1
            self.flag_count -= 1
            self.refresh_labels()

    def get_neighbours(self, x, y):
        neighbours = []
        coords = [
            {"x": x-1, "y": y-1},
            {"x": x-1, "y": y},
            {"x": x-1, "y": y+1},
            {"x": x, "y": y - 1},
            {"x": x, "y": y + 1},
            {"x": x + 1, "y": y - 1},
            {"x": x + 1, "y": y},
            {"x": x + 1, "y": y + 1},
        ]
        for n in coords:
            try:
                neighbours.append(self.tiles[n["x"]][n["y"]])
            except KeyError:
                pass
        return neighbours

    def clear_surrounding_tiles(self, tile_id):
        queue = deque([tile_id])

        while len(queue) is not 0:
            key = queue.popleft()
            parts = key.split("_")
            x = int(parts[0])
            y = int(parts[1])

            for tile in self.get_neighbours(x, y):
                self.clear_tile(tile, queue)

    def clear_tile(self, tile, queue):
        if tile["state"] is not STATE_DEFAULT:
            return
        if tile["mines"] == 0:
            tile["button"].config(image=self.assets["clicked"])
            queue.append(tile["id"])
        else:
            tile["button"].config(image=self.assets["numbers"][tile["mines"]-1])

        tile["state"] = STATE_CLICKED
        self.clicked_count += 1

    def game_over(self, won):
        for x in range(SIZE_X):
            for y in range(SIZE_Y):
                if self.tiles[x][y]["is_mine"] is False and self.tiles[x][y]["state"] is STATE_FLAGGED:
                    self.tiles[x][y]["button"].config(image=self.assets["wrong"])
                if self.tiles[x][y]["is_mine"] is True and self.tiles[x][y]["state"] is not STATE_FLAGGED:
                    self.tiles[x][y]["button"].config(image=self.assets["mine"])

        self.tk.update()

        msg = "YOU WIN! PLAY AGAIN?" if won else "YOU LOSE! PLAY AGAIN?"
        res = messagebox.askyesno("GAME OVER", msg)
        if res:
            self.restart()
        else:
            self.tk.quit()


def main():
    # INIT TKB
    window = master
    # SET TITLE
    window.title("Minesweeper")
    # CREATE GAME
    Minesweeper(window)
    # RUN EVENT LOOP
    window.mainloop()


if __name__ == "__main__":
    main()

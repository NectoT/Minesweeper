import random
import http.server
import json


class Player:
    def __init__(self):
        pass


class Minesweeper:
    def __init__(self):
        self.field_size = 400  # in most code the size is actually hardcoded, this variable is useless atm
        self.field_width = int(self.field_size**0.5)
        self.field = [-1 for i in range(self.field_size)]
        self.mines_indices = random.sample(range(self.field_size), 90)

        self.first_tile = True

        self.closed_tiles = self.field_size

    def get_field_info(self):
        return self.field

    def check_win(self):
        if self.closed_tiles == len(self.mines_indices):
            return True
        return False

    def open_tile(self, tile_index):
        if not 0 <= tile_index < self.field_size:
            return False

        if tile_index in self.mines_indices or self.field[tile_index] != -1:
            if not self.first_tile:
                return False
            #print("First mine replaced")
            self.mines_indices.remove(tile_index)
            new_mine_index = random.randint(0, 399)
            while new_mine_index in self.mines_indices:
                new_mine_index = random.randint(0, 399)
            self.mines_indices.append(new_mine_index)
        self.first_tile = False


        nearby_mines = 0
        neighbors_distance = []
        # listen I don't know how to properly work with border cases so it's a bunch of nested ifs
        if tile_index % 20 != 0 and tile_index % 20 != 19 and 20 <= tile_index < 380:
            neighbors_distance = [-1, 1, 19, 20, 21, -19, -20, -21]  # good ending
        else:
            if tile_index < 20:
                if tile_index == 0:
                    neighbors_distance = [1, 20, 21]
                elif tile_index == 19:
                    neighbors_distance = [-1, 19, 20]
                else:
                    neighbors_distance = [-1, 1, 19, 20, 21]
            elif tile_index >= 380:
                if tile_index % 20 == 0:
                    neighbors_distance = [1, -20, -19]
                elif tile_index % 20 == 19:
                    neighbors_distance = [-1, -21, -20]
                else:
                    neighbors_distance = [-1, 1, -19, -20, -21]
            elif tile_index % 20 == 0:
                neighbors_distance = [1, 20, 21, -20, -19]
            else:  # tile_index % 20 == 19
                neighbors_distance = [-1, 19, 20, -21, -20]

        for distance in neighbors_distance:
            if (tile_index + distance) in self.mines_indices:
                nearby_mines += 1

        self.field[tile_index] = nearby_mines

        if nearby_mines == 0:
            for distance in neighbors_distance:
                self.open_tile(tile_index + distance)

        self.closed_tiles -= 1

        return True


class MinesweeperRequestHandler(http.server.BaseHTTPRequestHandler):
    active_minesweeper: Minesweeper = None

    def __init__(self, request, client_address, server):
        self.get_urls = {
            "/": self.index,
            "/script.js": self.script,
            "/style.css": self.style,
            "/get-field": self.get_field
        }
        self.post_urls = {
            "/open-tile": self.open_tile,
            "/reset": self.reset
        }
        super().__init__(request, client_address, server)

    def do_POST(self):
        body = self.rfile.read(int(self.headers["content-length"]))
        if self.path not in self.post_urls:
            self.send_error(400)
            return
        # for now assume that every post body is json
        if (len(body) > 0):
            kwargs: dict = json.loads(body)
        else:
            kwargs = {}
        self.post_urls[self.path](*kwargs.values())

    def open_tile(self, *args):
        if MinesweeperRequestHandler.active_minesweeper is None:
            self.send_error(500)
            return

        if len(args) != 1 or type(args[0]) != int or not (0 <= args[0] < 400):
            self.send_error(400, "Wrong number sent")
            return

        result = {'successful': MinesweeperRequestHandler.active_minesweeper.open_tile(args[0])}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode("UTF-8"))

    def reset(self, *args):
        MinesweeperRequestHandler.active_minesweeper = Minesweeper()
        print("Game restarted")
        self.send_response(301)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        if self.path not in self.get_urls:
            self.send_error(404)
            return
        self.get_urls[self.path]()

    def index(self):
        html_file = open("index.html")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html_file.read().encode("UTF-8"))

    def script(self):
        script_file = open("script.js")
        self.send_response(200)
        self.send_header("Content-Type", "application/javascript")
        self.end_headers()
        self.wfile.write(script_file.read().encode("UTF-8"))

    def style(self):
        style_file = open("style.css")
        self.send_response(200)
        self.send_header("Content-Type", "text/css")
        self.end_headers()
        self.wfile.write(style_file.read().encode("UTF-8"))

    def get_field(self):
        if MinesweeperRequestHandler.active_minesweeper is None:
            self.send_error(500)
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {"field": MinesweeperRequestHandler.active_minesweeper.get_field_info()}
        self.wfile.write(json.dumps(response).encode("UTF-8"))


def run_server():
    MinesweeperRequestHandler.active_minesweeper = Minesweeper()

    # running a server for visualizing the game
    server = http.server.ThreadingHTTPServer(('', 8000), MinesweeperRequestHandler)
    print("Server started")
    server.serve_forever()


def train_player():
    pass
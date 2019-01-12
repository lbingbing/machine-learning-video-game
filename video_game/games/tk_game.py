import tkinter as tk
import tkinter.ttk
import queue
import threading

from video_game.players.player import is_human
from video_game.players.player import is_monitor
from video_game.games.utils import save_transcript

class BaseApp:

    def __init__(self, player_type, is_save_transcript):
        self.is_save_transcript = is_save_transcript

        self.set_intervals()

        self.game_num = 0
        self.init_state()
        self.init_player(player_type)
        self.is_human_player = is_human(self.player)
        self.is_monitor_mode = is_monitor(self.player)
        self.create_gui()
        self.bind_events()
        self.is_polling_update = False
        self.init_async_worker()
        self.reset()
        if self.is_monitor_mode:
            self.start()

    def set_intervals(self):
        pass

    def init_async_worker(self):
        self.request_queue = queue.Queue()
        self.response_queue = queue.Queue()

        self.worker_thread = threading.Thread(target = self.async_get_action)

        self.is_polling_async_response = False
        self.is_async_request_sent = False
        self.get_async_action_id = None

    def async_get_action(self):
        while True:
            item = self.request_queue.get()
            if item == None:
                break
            func, arg = item
            action = func(arg)
            self.response_queue.put(action)

    def init_state(self):
        pass

    def init_player(self, player_type):
        self.player = self.create_player(self.state, player_type)

    def get_unit_size(self):
        pass

    def create_gui(self):
        self.root = tk.Tk()

        self.root.resizable(width=False, height=False)
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.frame = tk.ttk.Frame(self.root, borderwidth=1, relief=tk.GROOVE, padding=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.grid(row=0, column=0, padx=3, pady=3, sticky=tk.N+tk.S+tk.W+tk.E)

        canvas_height = (self.state.height + 2) * self.get_unit_size()
        canvas_width = (self.state.width + 2) * self.get_unit_size()
        self.canvas = tk.Canvas(self.frame, width = canvas_width, height = canvas_height)
        self.canvas.grid(row=0, column=0, sticky=tk.N+tk.S+tk.W+tk.E)
        for i in range(1, self.state.height+1):
            x0 = self.get_unit_size()
            x1 = self.state.width * self.get_unit_size()
            y = i * self.get_unit_size()
            self.canvas.create_line(x0, y, x1, y)
        for j in range(1, self.state.width+1):
            x = j * self.get_unit_size()
            y0 = self.get_unit_size()
            y1 = self.state.height * self.get_unit_size()
            self.canvas.create_line(x, y0, x, y1)
        self.canvas_unit_objs = [[None for j in range(self.state.width)] for i in range(self.state.height)]
        for i in range(self.state.height):
            for j in range(self.state.width):
                coords = ((j + 1) * self.get_unit_size(), (i + 1) * self.get_unit_size(), (j + 2) * self.get_unit_size(), (i + 2) * self.get_unit_size())
                self.canvas_unit_objs[i][j] = self.canvas.create_rectangle(*coords, tags = 'unit')

    def bind_events(self):
        if not self.is_monitor_mode:
            self.root.bind('<Return>', lambda e: (self.reset(), self.start()))
        if self.is_human_player:
            self.bind_human_player_events()

    def bind_human_player_events(self):
        pass

    def reset(self):
        if self.is_polling_update:
            self.root.after_cancel(self.update_id)
            self.is_polling_update = False
        self.cancel_async_request()
        self.state.reset()
        self.actions = []
        self.draw()

    def cancel_async_request(self):
        if self.is_polling_async_response:
            self.root.after_cancel(self.get_async_action_id)
            self.is_polling_async_response = False
        if self.is_async_request_sent:
            self.response_queue.get()
            self.is_async_request_sent = False

    def start(self):
        if self.is_human_player:
            self.schedule_update()
        else:
            self.computer_step()

    def computer_step(self):
        self.send_async_request()
        self.poll_async_response()

    def send_async_request(self):
        self.request_queue.put((self.player.get_action, self.state))
        self.is_async_request_sent = True

    def poll_async_response(self):
        self.is_polling_async_response = False
        try:
            item = self.response_queue.get(block = False)
            if self.is_monitor_mode:
                action, next_state = item
                self.state = next_state
            else:
                action = item
                self.state.do_action(action)
            self.is_async_request_sent = False
            self.actions.append(action)
            self.schedule_update()
        except queue.Empty:
            self.get_async_action_id = self.root.after(self.async_response_poll_interval_in_millisecond, self.poll_async_response)
            self.is_polling_async_response = True

    def schedule_update(self):
        self.update_id = self.root.after(self.update_interval_in_millisecond, self.update)
        self.is_polling_update = True

    def update(self):
        self.is_polling_update = False
        if not self.is_monitor_mode:
            self.state.update()
        self.draw()
        if self.state.is_end():
            self.game_num += 1
            print('{0} game over! score: {1} age: {2}'.format(self.game_num, self.state.get_score(), self.state.get_age()))
            if self.is_save_transcript:
                save_transcript(self.get_transcript_save_path(), self.actions)
            if self.is_monitor_mode:
                self.reset()
                self.start()
        else:
            if self.is_human_player:
                self.schedule_update()
            else:
                self.computer_step()

    def draw(self):
        pass

    def get_transcript_save_path(self):
        pass

    def mainloop(self):
        self.worker_thread.start()
        self.root.mainloop()
        self.request_queue.put(None)
        self.worker_thread.join()


import tkinter as tk
import tkinter.ttk as ttk
from tkinter.scrolledtext import ScrolledText
from UnoServer import UnoServer
from ChatServer import ChatServer
from PingServer import PingServer
import threading

RECV_BUFFER = 1024


class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.uno_server = UnoServer()
        self.chat_server = ChatServer()
        self.ping_server = PingServer()

        self.wm_title("PyUno Server")
        # Main frame and config
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionary of frames in the app.
        self.frames = {}

        # Loop through the frame tuple (windows) and add it to the frames dictionary
        frame = ServerWindow(parent=container, controller=self)
        self.frames[ServerWindow] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        # Showing the connection window first.
        self.show_frame(ServerWindow)

        # Showing the connection window first.
        self.show_frame(ServerWindow)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class ServerWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # Controller references the main app. Used to access its instance variables.
        self.controller = controller
        self.parent = parent

        # Controls relevant to the server window.
        port_label = ttk.Label(self, text="Port Number: ")
        self.port_entry = ttk.Entry(self)
        chatport_label = ttk.Label(self, text="Chat Port Number: ")
        self.chatport_entry = ttk.Entry(self)
        pingport_label = ttk.Label(self, text="Ping Port Number: ")
        self.pingport_entry = ttk.Entry(self)
        playerno_label = ttk.Label(self, text="Number of players: ")
        self.playerno_entry = ttk.Entry(self)
        # Adding relevant controls to grid.
        port_label.grid(row=0, sticky="e")
        self.port_entry.grid(row=0, column=1)
        self.chatport_entry.grid(row=1, column=1)
        self.pingport_entry.grid(row=2, column=1)
        chatport_label.grid(row=1, sticky="e")
        pingport_label.grid(row=2, sticky="e")
        playerno_label.grid(row=3, sticky="e")
        self.playerno_entry.grid(row=3, column=1)
        start_button = ttk.Button(self, text="Start server", command=self.start)
        start_button.grid(row=4, column=1)

        self.insert_defaults()

    # Start accepting players into the game
    def start(self):
        uno_server = self.controller.uno_server
        chat_server = self.controller.chat_server
        ping_server = self.controller.ping_server
        server_port = int(self.port_entry.get())

        uno_server.create_socket(server_port)
        ping_server.create_socket(int(self.pingport_entry.get()))
        chat_server.create_socket(int(self.chatport_entry.get()))

        chat_thread = threading.Thread(
            target=chat_server.accept_chats,
            args=(int(self.playerno_entry.get()), uno_server.players),
        )
        chat_thread.start()

        uno_server.accept_players(int(self.playerno_entry.get()))

        print(self.controller.uno_server.players)

        frame = PingWindow(parent=self.parent, controller=self.controller)
        self.controller.frames[PingWindow] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.controller.show_frame(PingWindow)

    # Insert defaults to entry controls for quick testing.
    def insert_defaults(self):
        self.port_entry.insert("end", 8000)
        self.playerno_entry.insert("end", 1)
        self.chatport_entry.insert("end", 4000)
        self.pingport_entry.insert("end", 5000)


class PingWindow(tk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        uno_server = self.controller.uno_server
        self.ping_server = self.controller.ping_server

        self.grid_rowconfigure(1)
        self.grid_columnconfigure(1, weight=1)

        label = ttk.Label(self, text="Pings from players")
        self.chat_area = ScrolledText(self, height=10)
        label.grid(row=0, column=1)
        self.chat_area.grid(row=1, column=1)

        uno_server.start_gamethread()
        ping_thread = threading.Thread(target=self.ping_thread)
        ping_thread.start()

    def ping_thread(self):
        while True:
            message = self.ping_server.accept_pings()
            self.chat_area.insert("end", message)


server_app = MainApp()
server_app.mainloop()

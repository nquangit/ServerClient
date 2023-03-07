import tkinter as tk
from tkinter import ttk
from .Server_Method import *

FONT = ("Tahoma", 12)
SMALL_FONT = ("Tahoma", 10)


class client_interraction(Client):
    _STOP_UPDATE_RESPONSE = threading.Event()
    _system_command_window_open = False

    def __init__(self, master, client) -> None:
        self.__master = master
        self.__client = client

    def systemCommandWindow(self):
        if self._system_command_window_open:
            return
        self._system_command_window_open = True
        self.__system_command_window = tk.Toplevel(self.__master)
        self.__system_command_window.title(
            f"System Command | {self.__client._INFO[0]}")
        self.__system_command_window.geometry("500x550")
        self.__system_command_window.resizable(True, False)
        self.__system_command_window.option_add("*Font", FONT)

        frame = tk.Frame(self.__system_command_window,
                         borderwidth=2, relief=tk.RIDGE, padx=7, pady=7)
        self.__output = tk.Text(frame)
        self.__output.pack(fill=tk.BOTH, expand=True)
        command_frame = tk.Frame(frame)
        self.__command = tk.Entry(command_frame)
        self.__command.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.__command.bind(
            "<Return>", lambda e: self.systemCommandWindow_send_command())
        send = tk.Button(command_frame, text="Send",
                         command=self.systemCommandWindow_send_command)
        send.pack(side=tk.RIGHT)
        command_frame.pack(fill=tk.X, expand=True)
        frame.pack(fill=tk.BOTH, expand=True)

        # Reload the history
        self.systemCommandWindow_reload_history()

        self.__system_command_window.protocol(
            "WM_DELETE_WINDOW", self.systemCommandWindow_onclosing)
        self.__system_command_window.mainloop()

    def systemCommandWindow_reload_history(self):
        history = self.__client.get_command_response()
        # Add the history to the output
        for command in history:
            for key, value in command.items():
                self.__output.insert(tk.END, f"\n{key}:\n{value}")

    def systemCommandWindow_onclosing(self):
        self._STOP_UPDATE_RESPONSE.set()
        self.__system_command_window.destroy()

    def systemCommandWindow_send_command(self):
        command = self.__command.get()
        self.__command.delete(0, tk.END)
        if not command or len(command) == 0:
            return
        self.__output.insert(
            tk.END, f"Executing command: {command}")
        self.__client.send_message("command", command)
        # Create a new thread to check the command response
        self._STOP_UPDATE_RESPONSE.clear()
        self._UPDATE_RESPONSE_THREAD = threading.Thread(
            target=self.update_command_response, daemon=True)
        self._UPDATE_RESPONSE_THREAD.start()

    def update_command_response(self):
        while not self._STOP_UPDATE_RESPONSE.is_set():
            if self.__client.responsed():
                self.__client.reset_responsed()
                res = self.__client.get_command_response()[-1]
                for key, value in res.items():
                    self.__output.insert(tk.END, f"\n{value}")


class Application(Server_Method):
    APP_NAME = "Server"
    APP_SIZE = "950x700"
    FONT = ("Tahoma", 12)
    SMALL_FONT = ("Tahoma", 10)
    _STOP_UPDATE_RESPONSE = threading.Event()

    def __init__(self):
        self.__main = tk.Tk()
        self.__main.title(self.APP_NAME)
        self.__main.geometry(self.APP_SIZE)
        self.__main.resizable(False, False)
        self.__main.option_add("*Font", self.FONT)
        self.add_tab()
        # self.add_menu()
        self.__main.protocol("WM_DELETE_WINDOW", self.on_closing)
        # show image windows

    def on_closing(self):
        self._STOP.set()
        self.stop()
        self.__main.destroy()

    def add_tab(self):
        self.Tabs = ttk.Notebook(self.__main)

        self.waiting_client_tab = ttk.Frame(self.Tabs)
        self.Tabs.add(self.waiting_client_tab, text='Waiting Client')
        self.add_wating_client_tab()

        self.vocabulary_tab = ttk.Frame(self.Tabs)
        self.Tabs.add(self.vocabulary_tab, text='Clients')
        self.add_vocabulary_tab()

        self.notify_tab = ttk.Frame(self.Tabs)
        self.Tabs.add(self.notify_tab, text='Notify')
        self.add_notify_tab()

        self.about_tab = ttk.Frame(self.Tabs)
        self.Tabs.add(self.about_tab, text='About')

        self.Tabs.pack(expand=True, fill="both")

        toolbar = tk.Frame(self.__main, padx=5, pady=5)

        self.total_label = ttk.Label(
            toolbar, text=f"Server listen on {self._HOST}:{self._PORT}")
        self.total_label.pack(side=tk.LEFT)
        self.show_image_button = ttk.Button(toolbar, text="Show Image")
        self.show_image_button['state'] = 'disabled'
        self.show_image_button.pack(side=tk.RIGHT)

        toolbar.pack(side=tk.BOTTOM, anchor=tk.W, fill=tk.X)

    def add_notify_tab(self):
        container = self.notify_tab
        notify_frame = tk.LabelFrame(
            container, text="Notification", borderwidth=2, relief=tk.RIDGE, padx=7, pady=7, font=self.SMALL_FONT)
        scrollbar_y = ttk.Scrollbar(notify_frame)
        scrollbar_x = ttk.Scrollbar(notify_frame, orient=tk.HORIZONTAL)
        self.list_notify_var = tk.Variable(value=list([]))
        self.list_notify = tk.Listbox(
            notify_frame, yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set, listvariable=self.list_notify_var)
        self.list_notify.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        notify_frame.pack(fill=tk.BOTH, expand=True)

    def add_wating_client_tab(self):
        container = self.waiting_client_tab

        wordlist = tk.LabelFrame(
            container, text="Waiting Clients", borderwidth=2, relief=tk.RIDGE, padx=7, pady=7, font=self.SMALL_FONT)
        scrollbar_y = ttk.Scrollbar(wordlist)
        scrollbar_x = ttk.Scrollbar(wordlist, orient=tk.HORIZONTAL)
        self.list_waiting_client_var = tk.Variable(value=list([]))
        self.list_waiting_client = tk.Listbox(
            wordlist, yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set, listvariable=self.list_waiting_client_var)

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.list_waiting_client.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.config(command=self.list_waiting_client.yview)
        scrollbar_x.config(command=self.list_waiting_client.xview)
        wordlist.pack(side=tk.LEFT, anchor=tk.NW, fill=tk.BOTH, expand=True)

        # Right click context menu
        self.waiting_client_context_menu = tk.Menu(
            self.list_waiting_client, tearoff=0)
        self.waiting_client_context_menu.add_command(
            label="Disconnect", command=self.waiting_client_context_menu_delete_command)
        self.list_waiting_client.bind(
            "<Button-3>", self.waiting_client_context_menu_popup)

    def waiting_client_context_menu_popup(self, event):
        selection = self.list_waiting_client.curselection()
        if selection:
            self.waiting_client_context_menu.post(event.x_root, event.y_root)

    def waiting_client_context_menu_delete_command(self):
        selection = self.list_waiting_client.curselection()
        if selection:
            index = selection[0]
            self._WATING_CLIENT[index].disconnect()

        self.waiting_client_context_menu.unpost()

    def add_vocabulary_tab(self):
        container = self.vocabulary_tab

        # Search box
        search = tk.LabelFrame(container, text="Tool", borderwidth=2,
                               relief=tk.RIDGE, padx=7, pady=7, font=self.SMALL_FONT)
        search_text = tk.StringVar()
        search_entry = ttk.Label(search, text="Something")

        wordlist = tk.LabelFrame(
            container, text="Clients", borderwidth=2, relief=tk.RIDGE, padx=7, pady=7, font=self.SMALL_FONT)
        scrollbar_y = ttk.Scrollbar(wordlist)
        scrollbar_x = ttk.Scrollbar(wordlist, orient=tk.HORIZONTAL)
        self.list_data = tk.Variable(value=list(self._CLIENT))
        self.mylist = tk.Listbox(
            wordlist, yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set, listvariable=self.list_data)
        search_entry.focus()
        search_entry.pack(fill=tk.X)
        search.pack(side=tk.TOP, fill=tk.X)

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.mylist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.config(command=self.mylist.yview)
        scrollbar_x.config(command=self.mylist.xview)
        wordlist.pack(side=tk.LEFT, anchor=tk.NW, fill=tk.BOTH, expand=True)

        # Right click context menu
        self.client_context_menu = tk.Menu(
            self.mylist, tearoff=0)
        self.client_context_menu.add_command(
            label="System command", command=self.client_context_menu_system_cmd_command)
        self.mylist.bind("<Button-3>", self.client_context_menu_popup)

    def client_context_menu_popup(self, event):
        selection = self.mylist.curselection()
        if selection:
            self.client_context_menu.post(event.x_root, event.y_root)

    def client_context_menu_system_cmd_command(self):
        selection = self.mylist.curselection()
        self.client_context_menu.unpost()
        if selection:
            index = selection[0]
            self._CLIENT[index].get_client_interaction().systemCommandWindow()

    def update_waiting_client_list(self):
        CLIENT_backup = []
        while not self._STOP.is_set():
            if CLIENT_backup != self._WATING_CLIENT:
                self.list_waiting_client.delete(0, tk.END)
                for client in self._WATING_CLIENT:
                    print(client.get_connection().getpeername())
                    self.list_waiting_client.insert(
                        tk.END, client.get_connection().getpeername())
                CLIENT_backup = self._WATING_CLIENT.copy()

    def update_client_list(self):
        CLIENT_backup = []
        while not self._STOP.is_set():
            if CLIENT_backup != self._CLIENT:
                self.mylist.delete(0, tk.END)
                self.list_client.delete(0, tk.END)
                for client in self._CLIENT:
                    print(client.get_info())
                    client_interact = client_interraction(self.__main, client)
                    client.set_client_interaction(client_interact)
                    self.mylist.insert(tk.END, client.get_info()[0])
                    self.list_client.insert(tk.END, client.get_info()[0])
                CLIENT_backup = self._CLIENT.copy()

    def update_notification(self):
        while not self._STOP.is_set():
            if len(self._NOTIFY) > 0:
                print(self._NOTIFY)
                for notify in self._NOTIFY:
                    self.list_notify.insert(tk.END, notify)
                self._NOTIFY.clear()

    def run(self):
        self.update_client_list_thread = threading.Thread(
            target=self.update_client_list, daemon=True)
        self.update_client_list_thread.start()

        self.update_waiting_client_list_thread = threading.Thread(
            target=self.update_waiting_client_list, daemon=True)
        self.update_waiting_client_list_thread.start()

        self.update_notification_thread = threading.Thread(
            target=self.update_notification, daemon=True)
        self.update_notification_thread.start()

        self.__main.mainloop()

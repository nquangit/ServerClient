import tkinter as tk


class App:
    def __init__(self, master):
        self.master = master
        self.create_widgets()

    def create_widgets(self):
        # Create a Listbox widget
        self.listbox = tk.Listbox(self.master)
        self.listbox.pack()

        # Add items to the Listbox widget
        for i in range(10):
            self.listbox.insert(tk.END, f"Item {i+1}")

        # Create a context menu for the Listbox widget
        self.menu = tk.Menu(self.master, tearoff=0)
        self.menu.add_command(label="Delete", command=self.delete_item)

        # Bind the right-click event to the Listbox widget
        self.listbox.bind("<Button-3>", self.show_menu)

    def show_menu(self, event):
        # Show the context menu at the current mouse position
        selection = self.listbox.curselection()
        if selection:
            self.menu.post(event.x_root, event.y_root)

        self.menu.unpost()

    def delete_item(self):
        # Get the selected item and delete it from the Listbox widget
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            self.listbox.delete(index)


root = tk.Tk()
app = App(root)
root.mainloop()

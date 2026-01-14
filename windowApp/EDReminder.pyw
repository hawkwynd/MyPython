import tkinter as tk
import sqlite3
from tkinter import messagebox

class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ED:Reminders")
        
        dark_color = "#404041"
        # root.configure(bg=dark_color)
        
        # custom font and size 
        custom_font = ("Tahoma", -12)
        label_font  = ("Tahoma", -14, "bold")

        # Create a database or connect to an existing one
        self.conn = sqlite3.connect("EDreminders.db")
        self.cursor = self.conn.cursor()

        # Create a table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY, system TEXT, reminder TEXT)''')
        self.conn.commit()

        # Create GUI elements system label and input form
        self.reminder_label = tk.Label(root, text="System", font=label_font)
        self.reminder_label.pack(side=tk.TOP, anchor="w", padx=10, pady=1)
        
        # system input
        self.reminder_entry = tk.Entry(root,font=custom_font, width=40)
        self.reminder_entry.pack(side=tk.TOP, anchor="w", padx=10, pady=2)

        # reminder label
        self.textReminder = tk.Label(root, text="Reminder", font=label_font)     
        self.textReminder.pack(side=tk.TOP, anchor="w", padx=10, pady=1)
        
        # reminder text input field
        self.textReminder_entry = tk.Entry(root, font=custom_font, width=40)
        self.textReminder_entry.pack(pady=10, padx=10,side=tk.TOP, anchor="w")

        # Add reminder button
        self.add_button = tk.Button(root, text="Add To list", command=self.add_reminder)
        self.add_button.pack()

        # saved reminders label
        self.listBox_label = tk.Label(root, font=label_font, text="Saved Reminders")
        self.listBox_label.pack(pady=10)

        # listbox
        self.reminder_listbox = tk.Listbox(root, font=custom_font, borderwidth=0, highlightthickness=0,  width=50)
        # self.reminder_listbox.place(relwidth=0.8)
        self.reminder_listbox.pack( fill="x", padx=10, pady=10, ipady=12)

        # delete button
        self.delete_button = tk.Button(root, text="Delete selected", command=self.delete_reminder)
        # self.delete_button.place(relx=0.1, rely=0.1)
        # self.delete_button.pack(pady=(120, 10))
        self.delete_button.pack(pady=(10, 20))
        
        # load reminders
        self.load_reminders()

    def add_reminder(self):
        system = self.reminder_entry.get()
        reminderText = self.textReminder_entry.get()

        if system and reminderText:
            self.cursor.execute("INSERT INTO reminders (system, reminder) VALUES (?,?)", (system,reminderText))
            self.conn.commit()
            self.load_reminders()
            self.reminder_entry.delete(0, tk.END)
            self.textReminder_entry.delete(0, tk.END)

        elif not system and not reminderText:
            messagebox.showwarning("Warning", "Please input a system and a reminder.")
        elif not system:
            messagebox.showwarning("Warning", "Please input a system.")
        elif not reminderText:
            messagebox.showwarning("Warning", "Please input a reminder.")


    def load_reminders(self):
        self.reminder_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT * FROM reminders")
        reminders = self.cursor.fetchall()
        # dynamic resize listbox for content
        
        self.reminder_listbox.configure(height=len(reminders)+10)

        # list system: reminder
        for row in reminders:
            self.reminder_listbox.configure(height=len(reminders))
            self.reminder_listbox.insert(tk.END, row[1] + ": " + row[2])

    def delete_reminder(self):
        selected_reminder = self.reminder_listbox.get(tk.ACTIVE)
        selected_system = selected_reminder.split(":")

        if selected_reminder:
            self.cursor.execute("DELETE FROM reminders WHERE system=?", (selected_system[0],))
            self.conn.commit()
            self.load_reminders()
        else:
            messagebox.showwarning("Warning", "Please select a system to delete.")

    def __del__(self):
        self.conn.close()


def open_help_modal():
        # 1. Create the Toplevel (popup) window
        help_window = tk.Toplevel(root)
        help_window.title("Help & Complaints Dept.")
        help_window.geometry("300x400")
        help_window.configure(bg="#000000") # Matching dark theme

        # 2. Make it a 'Modal'
        help_window.transient(root)    # Ties this window to the main 'root'
        help_window.grab_set()         # Prevents interaction with main window until closed

        # 3. Add Content
        tk.Label(
            help_window, 
            text="Help", 
            font=("Tahoma", -16, "bold"),
            bg="#000000", 
            fg="#FFFFFF"

        ).pack(pady=10)

        help_text = "1. Enter your data.\n2. Click Submit to save.\n3. View history in the list.\n4. Click an item to select it.\n5. Click Delete button to remove.\n"

        tk.Label(
            help_window, 
            text=help_text, 
            justify="left",
            bg="#000000", 
            fg="#ffffff",
            font=("Tahoma", -16)
        ).pack(padx=20, pady=10)


        tk.Label(
            help_window,
            text = "by CMDR Scott Fleming\n\nAn unofficial, undocumented, unsanctioned,\nunsupported application which is beta version\nand most likely will remain that way.",
            justify="left",
            bg="#000000", 
            fg="#ffffff",
            font=("Tahoma", -12)
        ).pack(padx=20, pady=10)

        # 4. Close Button
        tk.Button(
            help_window, 
            text="Close Help", 
            command=help_window.destroy,
            bg="#000000",
            fg="#e6640d"
        ).pack(pady=10)



if __name__ == "__main__":
    root = tk.Tk()
    root.title("ED Reminder")
    root.geometry("400x600")

    # Header area for the help link
    header = tk.Frame(root, bg="#000000")
    header.pack(fill="x", padx=10, pady=5)

    # Clickable Help Label
    help_link = tk.Label(
        header, 
        text="Help", 
        fg="#3498db", 
        cursor="hand2", 
        font=("Tahoma", -14 ),
        bg="#000000"
    )
    help_link.pack(side="right",padx=0)
    help_link.bind("<Button-1>", lambda e: open_help_modal())



    app = DatabaseApp(root)
    root.mainloop()

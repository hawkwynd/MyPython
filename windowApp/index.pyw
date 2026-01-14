
import tkinter as tk

def create_application_window():
    # Create the main window object
    root = tk.Tk()

    # Set properties of the window
    root.title("Elite Dangerous Reminder") # Set window title
    root.geometry("400x300")           # Set initial window dimensions (width x height)
    root.resizable(True, True)         # Allow window to be resized (width, height)

    # Add widgets (e.g., a label and a button)
    label = tk.Label(root, text="Hello, this is a standard application window!")
    label.pack(pady=20) # Add some padding

    def on_button_click():
        label.config(text="Button clicked!")

    button = tk.Button(root, text="Click Me", command=on_button_click)
    button.pack(pady=10)

    # Start the main event loop
    # This keeps the window open and responsive to user interactions
    root.mainloop()

if __name__ == "__main__":
    create_application_window()

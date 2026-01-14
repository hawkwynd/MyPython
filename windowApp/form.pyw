import tkinter as tk
from tkinter import messagebox

def handle_submit():
    user_name = name_entry.get()
    user_email = email_entry.get()
    
    if user_name and user_email:
        # Update the display label with the new data
        display_text = f"Last Submitted:\nName: {user_name}\nEmail: {user_email}"
        result_label.config(text=display_text, fg="green")
        
        # Clear inputs for the next entry
        name_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Please fill out all fields.")

root = tk.Tk()
root.title("Data Entry Form")
root.geometry("350x400")

# --- Form Section ---
tk.Label(root, text="Name:").pack(pady=(10, 0))
name_entry = tk.Entry(root)
name_entry.pack(pady=5)

tk.Label(root, text="Email:").pack(pady=(10, 0))
email_entry = tk.Entry(root)
email_entry.pack(pady=5)

submit_btn = tk.Button(root, text="Submit Data", command=handle_submit)
submit_btn.pack(pady=20)

# --- Display Section ---
# A separator for visual clarity
tk.Frame(root, height=2, bd=1, relief="sunken").pack(fill="x", padx=10, pady=10)

tk.Label(root, text="Submitted Information:", font=("Arial", 10, "bold")).pack()
result_label = tk.Label(root, text="No data submitted yet", justify="left", pady=10)
result_label.pack()

root.mainloop()

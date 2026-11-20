import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "PARKING.db"

# -----------------------
# Database Initialization
# -----------------------
def initialize_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parking_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slot_number INTEGER UNIQUE NOT NULL,
            is_available INTEGER NOT NULL DEFAULT 1,
            allowed_type TEXT NOT NULL,
            level INTEGER NOT NULL,
            zone TEXT NOT NULL,
            is_covered INTEGER NOT NULL DEFAULT 1,
            has_charger INTEGER NOT NULL DEFAULT 0,
            is_reserved INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM parking_slots")
    if cursor.fetchone()[0] == 0:
        for i in range(101, 131):
            cursor.execute("""
                INSERT INTO parking_slots (slot_number, allowed_type, level, zone, is_covered, has_charger, is_reserved)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (i, 'Compact' if i % 4 == 0 else 'SUV' if i % 3 == 0 else 'EV',
                 (i - 100) // 5 + 1, chr(65 + ((i - 101) % 5)), i % 2, i % 3 == 0, i % 7 == 0))
        conn.commit()
    conn.close()

# -----------------------
# Database Operations
# -----------------------
def get_all_slots():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM parking_slots ORDER BY slot_number")
    data = cursor.fetchall()
    conn.close()
    return data

def book_slot(slot_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE parking_slots SET is_available = 0 WHERE id = ? AND is_available = 1", (slot_id,))
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated > 0

def reset_slots():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE parking_slots SET is_available = 1")
    conn.commit()
    conn.close()

# -----------------------
# GUI Class
# -----------------------
class SmartParkingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Parking Management System")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f5f5f5")

        title = tk.Label(root, text="Smart Parking Dashboard", font=("Helvetica", 24, "bold"), bg="#f5f5f5")
        title.pack(pady=20)

        filter_frame = tk.Frame(root, bg="#f5f5f5")
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Filter by Type:", bg="#f5f5f5").grid(row=0, column=0, padx=5)
        self.filter_type = ttk.Combobox(filter_frame, values=["All", "Compact", "SUV", "EV"])
        self.filter_type.set("All")
        self.filter_type.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Level:", bg="#f5f5f5").grid(row=0, column=2, padx=5)
        self.filter_level = ttk.Combobox(filter_frame, values=["All"] + [str(i) for i in range(1, 8)])
        self.filter_level.set("All")
        self.filter_level.grid(row=0, column=3, padx=5)

        tk.Button(filter_frame, text="Apply Filter", command=self.display_slots, bg="#03a9f4", fg="white", width=15).grid(row=0, column=4, padx=5)

        button_frame = tk.Frame(root, bg="#f5f5f5")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Refresh", command=self.display_slots, bg="#4caf50", fg="white",
                  font=("Helvetica", 12), width=15).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Reset All", command=self.reset_all, bg="#f44336", fg="white",
                  font=("Helvetica", 12), width=15).grid(row=0, column=1, padx=10)

        self.canvas = tk.Canvas(root, bg="#f5f5f5")
        self.scroll_y = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.frame = tk.Frame(self.canvas, bg="#f5f5f5")

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.canvas.pack(fill="both", expand=True, side="left")
        self.scroll_y.pack(fill="y", side="right")

        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.display_slots()

    def display_slots(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        slots = get_all_slots()

        type_filter = self.filter_type.get()
        level_filter = self.filter_level.get()

        filtered_slots = []
        for s in slots:
            if type_filter != "All" and s[3] != type_filter:
                continue
            if level_filter != "All" and str(s[4]) != level_filter:
                continue
            filtered_slots.append(s)

        for i, slot in enumerate(filtered_slots):
            sid, snum, avail, ctype, level, zone, covered, charger, reserved = slot
            color = "#8bc34a" if avail else "#e91e63"
            text = f"Slot {snum}\n{ctype} | Level {level} | Zone {zone}\n"
            if reserved:
                text += "Reserved\n"
            if charger:
                text += "EV Charger\n"
            if not covered:
                text += "Open-Air"
            else:
                text += "Covered"

            btn = tk.Button(self.frame, text=text, bg=color, fg="white", font=("Arial", 10, "bold"),
                            width=20, height=6,
                            command=lambda s=sid, a=avail: self.book(s, a))
            btn.grid(row=i // 4, column=i % 4, padx=10, pady=10)

    def book(self, slot_id, is_available):
        if not is_available:
            messagebox.showwarning("Already Booked", "This slot is already occupied.")
        elif book_slot(slot_id):
            messagebox.showinfo("Booked", "You have successfully booked the slot.")
        else:
            messagebox.showerror("Failed", "Unable to book the slot.")
        self.display_slots()

    def reset_all(self):
        if messagebox.askyesno("Confirm Reset", "Reset all parking slots to available?"):
            reset_slots()
            self.display_slots()

# -----------------------
# Run App
# -----------------------
if __name__ == "__main__":
    initialize_db()
    root = tk.Tk()
    app = SmartParkingApp(root)
    root.mainloop()

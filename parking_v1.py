import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_NAME = "PARKING.db"

# --------------------------
# DATABASE ACCESS FUNCTIONS
# --------------------------
def get_all_slots():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, slot_number, is_available, allowed_type, level, zone, 
               is_covered, has_charger, is_reserved 
        FROM parking_slots
        ORDER BY slot_number
    """)
    slots = cursor.fetchall()
    conn.close()
    return slots

def book_slot(slot_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE parking_slots SET is_available = 0 
        WHERE id = ? AND is_available = 1
    """, (slot_id,))
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated > 0

def reset_all_slots():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE parking_slots SET is_available = 1")
    conn.commit()
    conn.close()

# --------------------------
# GUI APP CLASS
# --------------------------
class ParkingApp:
    def __init__(self, root):  # ✅ FIXED __init__ (double underscores)
        self.root = root
        self.root.title("Smart Parking System")

        tk.Label(root, text="Smart Parking System with Car Type & Level", font=("Arial", 16)).pack(pady=10)

        self.slots_frame = tk.Frame(root)
        self.slots_frame.pack()

        tk.Button(root, text="Reset All Slots", command=self.reset_slots, bg="orange").pack(pady=5)
        tk.Button(root, text="Refresh", command=self.refresh_slots).pack(pady=5)

        self.refresh_slots()

    def refresh_slots(self):
        for widget in self.slots_frame.winfo_children():
            widget.destroy()

        slots = get_all_slots()

        for idx, (slot_id, number, avail, car_type, level, zone, covered, charger, reserved) in enumerate(slots):
            status = "Available" if avail else "Occupied"
            color = "green" if avail else "red"
            text = f"Slot {number}\n{status}\nType: {car_type}\nLevel: {level}\nZone: {zone}"

            btn = tk.Button(
                self.slots_frame,
                text=text,
                bg=color,
                fg="white",
                width=20,
                height=5,
                command=lambda s_id=slot_id, available=avail: self.book(s_id, available)
            )
            btn.grid(row=idx // 3, column=idx % 3, padx=8, pady=8)

    def book(self, slot_id, is_available):
        if not is_available:
            messagebox.showwarning("Unavailable", "This slot is already occupied.")
            return

        if book_slot(slot_id):
            messagebox.showinfo("Booked", "Slot booked successfully.")
        else:
            messagebox.showerror("Error", "Booking failed.")
        self.refresh_slots()

    def reset_slots(self):
        if messagebox.askyesno("Reset", "Reset all slots to available?"):
            reset_all_slots()
            self.refresh_slots()

# --------------------------
# MAIN PROGRAM
# --------------------------
if __name__ == "__main__":  # ✅ FIXED __name__ (double underscores)
    root = tk.Tk()
    app = ParkingApp(root)
    root.mainloop()

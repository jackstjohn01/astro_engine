import tkinter as tk
from tkinter import filedialog, messagebox

class SpacecraftEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Spacecraft Editor")

        # Field order in CSV:      x, y, vx, vy, m, r, name, color
        # Display order in GUI:    name, x, y, vx, vy, m, r, color
        self.csv_field_order = ["x", "y", "vx", "vy", "m", "r", "name", "color"]
        self.display_order = ["name", "x", "y", "vx", "vy", "m", "r", "color"]
        self.burn_labels = ["+t", "Δv_x", "Δv_y"]

        self.property_entries = {}
        self.burn_entries = []

        self.file_path = None
        self.init_gui()

    def init_gui(self):
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(fill="both", expand=True)

        # Top buttons
        top_btns = tk.Frame(self.main_frame)
        tk.Button(top_btns, text="Open CSV", command=self.load_csv).pack(side="left", padx=5)
        tk.Button(top_btns, text="Save CSV", command=self.save_csv).pack(side="left", padx=5)
        tk.Button(top_btns, text="Add Burn Command", command=self.add_burn_row).pack(side="left", padx=5)
        top_btns.pack(pady=5)

        # Property section
        self.property_frame = tk.LabelFrame(self.main_frame, text="Spacecraft Properties")
        self.property_frame.pack(fill="x", pady=10)

        # Burn command section
        self.burn_frame = tk.LabelFrame(self.main_frame, text="Burn Commands")
        self.burn_frame.pack(fill="both", expand=True)
        self.burn_table_frame = tk.Frame(self.burn_frame)
        self.burn_table_frame.pack(fill="both", expand=True)

    def clear_entries(self):
        for widget in self.property_frame.winfo_children():
            widget.destroy()
        for widget in self.burn_table_frame.winfo_children():
            widget.destroy()
        self.property_entries.clear()
        self.burn_entries.clear()

    def load_csv(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not self.file_path:
            return

        with open(self.file_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            messagebox.showerror("Error", "CSV is empty or invalid.")
            return

        self.clear_entries()

        # Line 1 = properties
        raw_values = lines[0].split(',')
        properties = dict(zip(self.csv_field_order, raw_values))

        for i, field in enumerate(self.display_order):
            tk.Label(self.property_frame, text=field).grid(row=0, column=i, sticky="w", padx=4)
            entry = tk.Entry(self.property_frame, width=10)
            val = properties.get(field, "")
            if field == "name" and val.startswith('"') and val.endswith('"'):
                val = val[1:-1]  # Strip surrounding quotes
            entry.insert(0, val)
            entry.grid(row=1, column=i, padx=4, pady=2)
            self.property_entries[field] = entry

        # Burn commands
        self.add_burn_header()
        for burn in lines[1:]:
            self.add_burn_row(burn.split(','))

    def save_csv(self):
        if not self.file_path:
            self.file_path = filedialog.asksaveasfilename(defaultextension=".csv")

        if not self.file_path:
            return

        # Get values in CSV field order
        prop_values = []
        for field in self.csv_field_order:
            val = self.property_entries[field].get()
            if field == "name":
                val = f'"{val}"'  # Ensure quotes around name
            prop_values.append(val)
        prop_line = ','.join(prop_values)

        # Get burn rows
        burn_lines = []
        for row in self.burn_entries:
            line = ','.join(e.get() for e in row["entries"])
            burn_lines.append(line)

        with open(self.file_path, "w") as f:
            f.write(prop_line + "\n")
            for line in burn_lines:
                f.write(line + "\n")

        messagebox.showinfo("Saved", "Spacecraft file saved successfully.")

    def add_burn_header(self):
        headers = ["Order"] + self.burn_labels + ["Delete"]
        for col, text in enumerate(headers):
            tk.Label(self.burn_table_frame, text=text, font=("Arial", 10, "bold")).grid(row=0, column=col, padx=5, pady=2)

    def add_burn_row(self, values=None):
        row_index = len(self.burn_entries) + 1  # +1 because row 0 is header
        row_data = {"entries": [], "row_index": row_index}

        # Order number
        order_label = tk.Label(self.burn_table_frame, text=f"{row_index}")
        order_label.grid(row=row_index, column=0, padx=5)
        row_data["label"] = order_label

        # Burn entries
        for i in range(3):
            entry = tk.Entry(self.burn_table_frame, width=10)
            if values and i < len(values):
                entry.insert(0, values[i])
            entry.grid(row=row_index, column=i + 1, padx=5, pady=2)
            row_data["entries"].append(entry)

        # Delete button
        del_btn = tk.Button(self.burn_table_frame, text="Delete", command=lambda: self.delete_burn_row(row_data))
        del_btn.grid(row=row_index, column=4, padx=5)
        row_data["delete_btn"] = del_btn

        self.burn_entries.append(row_data)

    def delete_burn_row(self, row_data):
        # Remove widgets
        row_data["label"].destroy()
        for e in row_data["entries"]:
            e.destroy()
        row_data["delete_btn"].destroy()

        # Remove from list
        self.burn_entries.remove(row_data)

        # Re-render remaining entries (renumbering)
        self.redraw_burn_rows()

    def redraw_burn_rows(self):
        for i, row_data in enumerate(self.burn_entries, start=1):
            row_data["label"].config(text=str(i))
            row_data["label"].grid(row=i, column=0)
            for j, e in enumerate(row_data["entries"]):
                e.grid(row=i, column=j+1)
            row_data["delete_btn"].grid(row=i, column=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = SpacecraftEditor(root)
    root.mainloop()

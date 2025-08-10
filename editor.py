import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import numpy as np
from config import g0  # Make sure you have g0 defined in your config.py (9.80665 m/s²)


class SpacecraftEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Spacecraft CSV Editor")

        self.file_path = None
        self.entries = {}        # To store property entries by name
        self.burn_entries = []   # To store burn command row widgets

        self.build_ui()

    def build_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Buttons to open/save CSV
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(0, 10))
        open_btn = tk.Button(btn_frame, text="Open CSV", command=self.open_csv)
        open_btn.pack(side="left", padx=(0, 10))
        save_btn = tk.Button(btn_frame, text="Save CSV", command=self.save_csv)
        save_btn.pack(side="left")

        # === Spacecraft Properties Frame ===
        prop_frame = tk.LabelFrame(main_frame, text="Spacecraft Properties", padx=10, pady=10)
        prop_frame.pack(fill="x")

        # Subframes for groups
        identity_frame = tk.LabelFrame(prop_frame, text="Identity", padx=5, pady=5)
        identity_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        posvel_frame = tk.LabelFrame(prop_frame, text="Position & Velocity", padx=5, pady=5)
        posvel_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        mass_frame = tk.LabelFrame(prop_frame, text="Mass & Radius", padx=5, pady=5)
        mass_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        rocket_frame = tk.LabelFrame(prop_frame, text="Rocket Properties", padx=5, pady=5)
        rocket_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Make columns expand evenly
        prop_frame.columnconfigure(0, weight=1)
        prop_frame.columnconfigure(1, weight=1)

        # Add properties (name shown first but stored with quotes)
        self.add_property(identity_frame, "name", callback=self.update_dv, width=20)
        self.add_property(identity_frame, "color", width=15)

        self.add_property(posvel_frame, "x", width=12)
        self.add_property(posvel_frame, "y", width=12)
        self.add_property(posvel_frame, "vx", width=12)
        self.add_property(posvel_frame, "vy", width=12)

        self.add_property(mass_frame, "m", width=12, label="Dry Mass (kg)")
        self.add_property(mass_frame, "m_p", width=12, label="Propellant Mass (kg)")
        self.add_property(mass_frame, "r", width=12, label="Radius (m)")

        self.add_property(rocket_frame, "Isp", width=12, label="Isp (s)")
        self.add_property(rocket_frame, "thrust", width=12, label="Thrust (N)")

        # === Burn Commands Frame ===
        burns_frame = tk.LabelFrame(main_frame, text="Burn Commands", padx=10, pady=10)
        burns_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Burn table frame (for header + rows)
        self.burn_table = tk.Frame(burns_frame)
        self.burn_table.pack(fill="both", expand=True)

        # Header row
        headers_frame = tk.Frame(self.burn_table)
        headers_frame.grid(row=0, column=0, sticky="w", pady=(0, 6))
        tk.Label(headers_frame, text="Order", width=6, anchor="w").grid(row=0, column=0, padx=2)
        tk.Label(headers_frame, text="+t (s)", width=12, anchor="w").grid(row=0, column=1, padx=2)
        tk.Label(headers_frame, text="Δv_x (m/s)", width=12, anchor="w").grid(row=0, column=2, padx=2)
        tk.Label(headers_frame, text="Δv_y (m/s)", width=12, anchor="w").grid(row=0, column=3, padx=2)
        tk.Label(headers_frame, text="Action", width=10, anchor="w").grid(row=0, column=4, padx=2)

        # Add Burn button
        add_burn_btn = tk.Button(burns_frame, text="Add Burn Command", command=self.add_burn_row)
        add_burn_btn.pack(pady=6)

        # === Delta-v budget display ===
        self.dv_label = tk.Label(main_frame, text="Delta-v budget: N/A", font=("Arial", 12, "bold"), fg="blue")
        self.dv_label.pack(pady=(10,0))

    def add_property(self, parent, name, label=None, width=10, callback=None):
        """Create a label and entry in the parent frame, store entry widget keyed by name."""
        lbl_text = label if label else name.capitalize()
        frame = tk.Frame(parent)
        frame.pack(fill="x", pady=2)

        lbl = tk.Label(frame, text=lbl_text, width=15, anchor="w")
        lbl.pack(side="left")

        var = tk.StringVar()
        ent = tk.Entry(frame, textvariable=var, width=width)
        ent.pack(side="left", fill="x", expand=True)

        # Save entry widget by property name
        self.entries[name] = ent

        # Bind callback if provided
        if callback:
            var.trace_add("write", lambda *args: callback())

    def add_burn_row(self, values=None):
        """Add a new burn command row, optionally filling with 'values'."""
        row_index = len(self.burn_entries) + 1

        row_frame = tk.Frame(self.burn_table)
        row_frame.grid(row=row_index, column=0, sticky="w", pady=1)

        # Order label
        lbl = tk.Label(row_frame, text=str(row_index), width=6, anchor="w")
        lbl.grid(row=0, column=0, padx=2)

        # Entries for +t, Δv_x, Δv_y
        entries = []
        for col in range(1, 4):
            e = tk.Entry(row_frame, width=12)
            e.grid(row=0, column=col, padx=2)
            if values and col-1 < len(values):
                e.insert(0, values[col-1])
            entries.append(e)

        # Delete button
        del_btn = tk.Button(row_frame, text="Delete", command=lambda rf=row_frame: self.delete_burn_row(rf))
        del_btn.grid(row=0, column=4, padx=6)

        self.burn_entries.append({"frame": row_frame, "entries": entries, "label": lbl, "delete_btn": del_btn})
        self.renumber_burns()

    def delete_burn_row(self, frame):
        """Delete a burn command row and update numbering."""
        for i, burn in enumerate(self.burn_entries):
            if burn["frame"] == frame:
                burn["frame"].destroy()
                self.burn_entries.pop(i)
                break
        self.renumber_burns()

    def renumber_burns(self):
        """Update the order numbers of the burn commands after add/delete."""
        for i, burn in enumerate(self.burn_entries, start=1):
            burn["label"].config(text=str(i))
            # Also re-grid the rows to keep order consistent
            burn["frame"].grid_configure(row=i)

    def open_csv(self):
        """Open a spacecraft CSV file and populate UI fields."""
        path = filedialog.askopenfilename(
            title="Open Spacecraft CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                # Read spacecraft properties line
                props_line = next(reader)
                if len(props_line) != 11:
                    messagebox.showerror("Error", "Spacecraft properties line does not have 11 fields.")
                    return

                # Map CSV order to UI entries order
                # CSV order: name, color, x, y, vx, vy, m, m_p, r, Isp, thrust
                name, color, x, y, vx, vy, m, m_p, r, Isp, thrust = props_line

                # Populate entries, strip quotes from name for UI display
                self.entries["name"].delete(0, "end")
                self.entries["name"].insert(0, name.strip('"'))

                self.entries["color"].delete(0, "end")
                self.entries["color"].insert(0, color)

                self.entries["x"].delete(0, "end")
                self.entries["x"].insert(0, x)

                self.entries["y"].delete(0, "end")
                self.entries["y"].insert(0, y)

                self.entries["vx"].delete(0, "end")
                self.entries["vx"].insert(0, vx)

                self.entries["vy"].delete(0, "end")
                self.entries["vy"].insert(0, vy)

                self.entries["m"].delete(0, "end")
                self.entries["m"].insert(0, m)

                self.entries["m_p"].delete(0, "end")
                self.entries["m_p"].insert(0, m_p)

                self.entries["r"].delete(0, "end")
                self.entries["r"].insert(0, r)

                self.entries["Isp"].delete(0, "end")
                self.entries["Isp"].insert(0, Isp)

                self.entries["thrust"].delete(0, "end")
                self.entries["thrust"].insert(0, thrust)

                # Clear any existing burn commands UI rows
                for burn in self.burn_entries:
                    burn["frame"].destroy()
                self.burn_entries.clear()

                # Load burn commands (rest of CSV)
                for burn_line in reader:
                    # Skip empty or invalid lines
                    if not burn_line or len(burn_line) < 3:
                        continue
                    self.add_burn_row(burn_line[:3])

                self.file_path = path
                self.update_dv()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def save_csv(self):
        """Save current UI data to CSV file."""
        if not self.file_path:
            # Prompt for save location if no file loaded
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Spacecraft CSV"
            )
            if not path:
                return
            self.file_path = path

        try:
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Write spacecraft properties in CSV order:
                # name (with quotes), color, x, y, vx, vy, m, m_p, r, Isp, thrust
                name_val = f'"{self.entries["name"].get().strip()}"'  # add quotes for CSV
                row = [
                    name_val,
                    self.entries["color"].get().strip(),
                    self.entries["x"].get().strip(),
                    self.entries["y"].get().strip(),
                    self.entries["vx"].get().strip(),
                    self.entries["vy"].get().strip(),
                    self.entries["m"].get().strip(),
                    self.entries["m_p"].get().strip(),
                    self.entries["r"].get().strip(),
                    self.entries["Isp"].get().strip(),
                    self.entries["thrust"].get().strip()
                ]
                writer.writerow(row)

                # Write burn commands
                for burn in self.burn_entries:
                    vals = [e.get().strip() for e in burn["entries"]]
                    writer.writerow(vals)

                messagebox.showinfo("Saved", f"File saved to {self.file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def update_dv(self, *args):
        """Calculate and update delta-v budget label live."""
        try:
            m = float(self.entries["m"].get())
            m_p = float(self.entries["m_p"].get())
            Isp = float(self.entries["Isp"].get())

            if m <= 0 or (m + m_p) <= 0:
                raise ValueError("Mass values must be positive")

            dv_budget = Isp * g0 * np.log((m + m_p) / m)
            self.dv_label.config(text=f"Delta-v budget: {dv_budget:.2f} m/s")
        except Exception:
            self.dv_label.config(text="Delta-v budget: Invalid input")


if __name__ == "__main__":
    root = tk.Tk()
    app = SpacecraftEditor(root)
    root.mainloop()

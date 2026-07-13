import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class TelemetrySet:
    """Represents the data model for a single telemetry reading."""
    def __init__(self, set_id, temp, soc, idc, iac_list, status="Pending"):
        self.set_id = set_id
        self.temp = temp
        self.soc = soc
        self.idc = idc
        self.iac_list = iac_list
        self.status = status


class TelemetryTablePanel(ttk.LabelFrame):
    """Encapsulates the Left (70%) area handling the Treeview tabular layout."""
    def __init__(self, parent, status_callback, **kwargs):
        super().__init__(parent, text="Added Sets Table", padding=10, **kwargs)
        
        self.telemetry_sets = {} # Dict using item iids as keys for faster O(1) tracking
        self.update_status = status_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Define Columns for the Treeview
        # 'c0' tracks the visible sequential Set ID index column, others hold parameters
        self.columns = ("id", "temp", "soc", "idc", "iac_list", "set_status")
        
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings", selectmode="browse")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Setup Column Header Labels
        self.tree.heading("id", text="Set ID")
        self.tree.heading("temp", text="Target Temp (°C)")
        self.tree.heading("soc", text="Target SoC (%)")
        self.tree.heading("idc", text="Target IDC (A)")
        self.tree.heading("iac_list", text="Target IAC List")
        self.tree.heading("set_status", text="Status")
        
        # Configure column widths and center alignment
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("temp", width=110, anchor="center")
        self.tree.column("soc", width=110, anchor="center")
        self.tree.column("idc", width=110, anchor="center")
        self.tree.column("iac_list", width=130, anchor="center")
        self.tree.column("set_status", width=90, anchor="center")
        
        # Dynamic Scrollbar binding
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def add_set(self, data_set_instance):
        """Inserts a new row into the table grid."""
        # Insert elements directly mapped to our tuple configurations
        item_iid = self.tree.insert("", tk.END, values=(
            f"Set {data_set_instance.set_id}",
            f"{data_set_instance.temp} °C",
            f"{data_set_instance.soc} %",
            f"{data_set_instance.idc} A",
            data_set_instance.iac_list,
            data_set_instance.status
        ))
        # Keep data structure map synced with row reference ID
        self.telemetry_sets[item_iid] = data_set_instance
        self.update_status(f"Added Profile Set {data_set_instance.set_id}")

    def get_selected_set(self):
        """Helper to get data profile object of the highlighted row."""
        selected_item = self.tree.selection()
        if not selected_item:
            return None, None
        iid = selected_item[0]
        return iid, self.telemetry_sets[iid]

    def delete_selected(self):
        """Deletes highlighted row item."""
        iid, selected_set = self.get_selected_set()
        if not selected_set:
            messagebox.showwarning("Selection Error", "Please select a profile row from the table first.")
            return
            
        removed_id = selected_set.set_id
        self.tree.delete(iid)
        del self.telemetry_sets[iid]
        self.update_status(f"Deleted Profile Set {removed_id}")

    def move_selected_up(self):
        """Shifts selected row index visually up by one grid index step."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a row to move.")
            return
        
        iid = selected[0]
        idx = self.tree.index(iid)
        if idx == 0:
            return # Top of boundary limit reached
            
        # Move row element position inside Treeview
        self.tree.move(iid, self.tree.parent(iid), idx - 1)
        self.update_status(f"Moved Set {self.telemetry_sets[iid].set_id} Up")

    def move_selected_down(self):
        """Shifts selected row index visually down by one grid index step."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a row to move.")
            return
            
        iid = selected[0]
        idx = self.tree.index(iid)
        # Check layout size boundaries
        if idx == len(self.tree.get_children()) - 1:
            return 
            
        self.tree.move(iid, self.tree.parent(iid), idx + 1)
        self.update_status(f"Moved Set {self.telemetry_sets[iid].set_id} Down")


class NewSetDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Create New Telemetry Set")
        self.geometry("340x430")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        self.result = None
        
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="Target Temp (C) ").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_temp = ttk.Entry(main_frame, width=15)
        self.entry_temp.grid(row=0, column=1, sticky="ew", pady=5)
        
        ttk.Label(main_frame, text="Target SoC (%) ").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_soc = ttk.Entry(main_frame, width=15)
        self.entry_soc.grid(row=1, column=1, sticky="ew", pady=5)
        
        ttk.Label(main_frame, text="Target IDC (mA) ").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_idc = ttk.Entry(main_frame, width=15)
        self.entry_idc.grid(row=2, column=1, sticky="ew", pady=5)
        
        ttk.Label(main_frame, text="Target IAC List ").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_iac = ttk.Entry(main_frame, width=15)
        self.entry_iac.grid(row=3, column=1, sticky="ew", pady=5)

        ttk.Label(main_frame, text="Duration (ms) ").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_iac = ttk.Entry(main_frame, width=15)
        self.entry_iac.grid(row=4, column=1, sticky="ew", pady=5)

        ttk.Label(main_frame, text="Sampling Start (ms) ").grid(row=5, column=0, sticky="w", pady=5)
        self.entry_iac = ttk.Entry(main_frame, width=15)
        self.entry_iac.grid(row=5, column=1, sticky="ew", pady=5)

        ttk.Label(main_frame, text="Sample Points").grid(row=6, column=0, sticky="w", pady=5)
        self.entry_iac = ttk.Entry(main_frame, width=15)
        self.entry_iac.grid(row=6, column=1, sticky="ew", pady=5)

        ttk.Label(main_frame, text="Sampling Freq (Hz) ").grid(row=7, column=0, sticky="w", pady=5)
        self.entry_iac = ttk.Entry(main_frame, width=15)
        self.entry_iac.grid(row=7, column=1, sticky="ew", pady=5)

        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=8, column=0, columnspan=2, pady=(20, 0), sticky="ew")
        ttk.Label(info_frame, text="Οι AC συνιστώσες να έχουν τη μορφή \n(f1,I1),(f2,I2),...").grid()
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=(20, 0), sticky="ew")
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ttk.Button(btn_frame, text="Submit", command=self.on_submit).grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        self.bind("<Return>", lambda event: self.on_submit())
        self.wait_window(self)

    def on_submit(self):
        try:
            temp_val = float(self.entry_temp.get())
            soc_val = float(self.entry_soc.get())
            idc_val = float(self.entry_idc.get())
            iac_val = self.entry_iac.get()
            
            self.result = {
                "temp": temp_val,
                "soc": soc_val,
                "idc": idc_val,
                "iac_list": iac_val
            }
            self.destroy()
        except ValueError:
            messagebox.showerror("Input Error", "Please check your entries. Numeric values are expected.")


class BatteryDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Battery Table Dashboard Workspace")
        self.geometry("1050x620") # Expanded base size slightly to display table columns clean
        self.minimum_size = (850, 520)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=7, minsize=550)
        self.grid_columnconfigure(1, weight=3, minsize=250)
        
        self.set_counter = 1
        
        self.style = ttk.Style()
        self.style.configure("Abort.TButton", foreground="red")
        
        self.create_menu_bar()
        
        # Instantiate the new Left Table view instead of old Listbox format
        self.left_panel = TelemetryTablePanel(self, status_callback=self.set_status)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.create_right_area()
        self.create_status_bar()
        self.set_status("System Workspace Ready")
        
        # Load sample profile templates to showcase column population automatically
        self.load_default_profiles()

    def create_menu_bar(self):
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Set Wizard", command=self.handle_new_set)
        file_menu.add_separator()
        file_menu.add_command(label="Exit Application", command=self.quit)
        
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About Dashboard", command=lambda: messagebox.showinfo("About", "Structured Telemetry Workspace"))
        
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu_bar)

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self, textvariable=self.status_var, anchor="w", padx=10, pady=4, bd=1, relief=tk.SUNKEN, background="#F0F0F0")
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

    def set_status(self, text_message):
        self.status_var.set(f" Status: {text_message}")

    def create_right_area(self):
        right_frame = ttk.Frame(self, padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # --- TELEMETRY DISPLAYS GROUP ---
        display_group = ttk.LabelFrame(right_frame, text="Live Telemetry", padding=10)
        display_group.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        display_group.grid_columnconfigure(1, weight=1)
        
        self.telemetry_vars = {
            "Temp 1": tk.StringVar(value="-- °C"),
            "Temp 2": tk.StringVar(value="-- °C"),
            "Temp 3": tk.StringVar(value="-- °C"),
            "SoC": tk.StringVar(value="-- %"),
            "Voltage": tk.StringVar(value="-- V"),
            "Current": tk.StringVar(value="-- A")
        }
        
        for i, (label_text, var) in enumerate(self.telemetry_vars.items()):
            ttk.Label(display_group, text=f"{label_text}:", font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", pady=4, padx=5)
            ttk.Label(display_group, textvariable=var, font=("Arial", 10), background="#EAEAEA", width=12, anchor="center").grid(row=i, column=1, sticky="ew", pady=4, padx=5)

        # --- BUTTONS GROUP ---
        btn_group = ttk.LabelFrame(right_frame, text="Actions", padding=10)
        btn_group.grid(row=1, column=0, sticky="ew")
        btn_group.grid_columnconfigure(0, weight=1)
        btn_group.grid_columnconfigure(1, weight=1)
        
        ttk.Button(btn_group, text="New Set", command=self.handle_new_set).grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Button(btn_group, text="Delete Set", command=self.left_panel.delete_selected).grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Button(btn_group, text="Sync", command=self.handle_test).grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Button(btn_group, text="Move Up", command=self.left_panel.move_selected_up).grid(row=3, column=0, sticky="ew", pady=5, padx=(0, 2))
        ttk.Button(btn_group, text="Move Down", command=self.left_panel.move_selected_down).grid(row=3, column=1, sticky="ew", pady=5, padx=(2, 0))
        
        ttk.Button(btn_group, text="RUN", command=self.handle_run).grid(row=4, column=0, sticky="ew", pady=5, padx=(0, 2))
        ttk.Button(btn_group, text="ABORT", command=self.handle_abort, style="Abort.TButton").grid(row=4, column=1, sticky="ew", pady=5, padx=(2, 0))
        
        ttk.Button(btn_group, text="Quit", command=self.quit).grid(row=5, column=0, columnspan=2, sticky="ew", pady=(15, 5))

    def load_default_profiles(self):
        """Loads default rows onto dashboard instantiation."""
        self.left_panel.add_set(TelemetrySet(self.set_counter, 25.0, 80.0, 1.5, "0.5, 1.0, 1.2", "Pending"))
        self.set_counter += 1
        self.left_panel.add_set(TelemetrySet(self.set_counter, 40.0, 45.0, -2.0, "0.0, 0.5", "Complete"))
        self.set_counter += 1

    def handle_new_set(self):
        self.set_status("Awaiting profile configurations...")
        dialog = NewSetDialog(self)
        if dialog.result:
            new_set_obj = TelemetrySet(
                set_id=self.set_counter,
                temp=dialog.result["temp"],
                soc=dialog.result["soc"],
                idc=dialog.result["idc"],
                iac_list=dialog.result["iac_list"],
                status="Pending"
            )
            self.set_counter += 1
            self.left_panel.add_set(new_set_obj)
        else:
            self.set_status("Configuration creation canceled.")

    def handle_test(self):
        self.set_status("Firing live evaluation framework verification tests...")
        self.telemetry_vars["Temp 1"].set("24.5 °C")
        self.telemetry_vars["Temp 2"].set("25.1 °C")
        self.telemetry_vars["Temp 3"].set("24.8 °C")
        self.telemetry_vars["SoC"].set("87.3 %")
        self.telemetry_vars["Voltage"].set("3.82 V")
        self.telemetry_vars["Current"].set("1.45 A")

    def handle_run(self):
        iid, selected_set = self.left_panel.get_selected_set()
        if not selected_set:
            self.set_status("Execution halted: No source profile index highlighted.")
            messagebox.showwarning("Execution Error", "Please select a target data profile set from the table first.")
            return

        # Dynamically modify the internal object values and update the row layout view
        selected_set.status = "Running"
        self.left_panel.tree.set(iid, "set_status", "Running")
        
        self.set_status(f"Executing profile metrics sequence from Row Set {selected_set.set_id}...")
        messagebox.showinfo("Execution", f"Running Profile Set {selected_set.set_id} parameters...")

    def handle_abort(self):
        # Update any currently running set status indicator labels to aborted
        iid, selected_set = self.left_panel.get_selected_set()
        if selected_set and selected_set.status == "Running":
            selected_set.status = "Aborted"
            self.left_panel.tree.set(iid, "set_status", "Aborted")
            
        self.set_status("CRITICAL STATUS SIGNAL: OPERATION SEQUENCE ABORTED.")
        messagebox.showwarning("System Alert", "Emergency Abort Triggered! All sequences halted.")


if __name__ == "__main__":
    app = BatteryDashboard()
    app.mainloop()

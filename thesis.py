import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog  # Added for file open/save dialogs
import json
import re


class Set:
    def __init__(self, set_id, temp, soc, mode, sampling_freq, sample_points, sample_time, params, commands, status="Pending"):
        self.set_id = set_id
        self.temp = temp
        self.soc = soc
        self.status = status
        self.mode = mode
        self.sampling_freq = sampling_freq
        self.sample_points = sample_points
        self.sample_time = sample_time
        self.params = params
        self.commands=commands

    def to_dict(self):
        return {
            "set_id": self.set_id,
            "temp": self.temp,
            "soc": self.soc,
            "status": self.status,
            "mode": self.mode,
            "sampling_freq": self.sampling_freq,
            "sample_points": self.sample_points,
            "sample_time": self.sample_time,
            "params": self.params,
            "commands": self.commands
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            set_id=data["set_id"],
            temp=data["temp"],
            soc=data["soc"],
            mode=data["mode"],
            sampling_freq=data["sampling_freq"],
            sample_points=data["sample_points"],
            sample_time=data["sample_time"],
            params=data["params"],
            commands=data["commands"],
            status=data.get("status", "Pending")
        )


class Panel(ttk.LabelFrame):
    def __init__(self, parent, status_callback, **kwargs):
        super().__init__(parent, text="Added Sets Table", padding=10, **kwargs)
        
        self.sets = {} # Dict using item iids as keys for faster O(1) tracking
        self.update_status = status_callback
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Define Columns for the Treeview
        self.columns = ("id", "temp", "soc", "mode", "set_status")
        
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings", selectmode="browse")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Setup Column Header Labels
        self.tree.heading("id", text="Set ID")
        self.tree.heading("temp", text="Target Temp (°C)")
        self.tree.heading("soc", text="Target SoC (%)")
        self.tree.heading("mode", text="Mode")
        self.tree.heading("set_status", text="Status")
        
        # Configure column widths and center alignment
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("temp", width=110, anchor="center")
        self.tree.column("soc", width=110, anchor="center")
        self.tree.column("mode", width=130, anchor="center")
        self.tree.column("set_status", width=90, anchor="center")
        
        # Dynamic Scrollbar binding
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def add_set(self, data_set_instance):
        # Insert elements directly mapped to our tuple configurations
        item_iid = self.tree.insert("", tk.END, values=(
            f"{data_set_instance.set_id}",
            f"{data_set_instance.temp} °C",
            f"{data_set_instance.soc} %",
            data_set_instance.mode,
            data_set_instance.status
        ))
        # Keep data structure map synced with row reference ID
        self.sets[item_iid] = data_set_instance
        self.update_status(f"Added Profile Set {data_set_instance.set_id}")

    def clear_all(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.sets.clear()

    def get_ordered_sets(self):
        return [self.sets[iid] for iid in self.tree.get_children()]

    def get_selected_set(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return None, None
        iid = selected_item[0]
        return iid, self.sets[iid]

    def delete_selected(self):
        iid, selected_set = self.get_selected_set()
        if not selected_set:
            messagebox.showwarning("Selection Error", "Please select a profile row from the table first.")
            return
            
        removed_id = selected_set.set_id
        self.tree.delete(iid)
        del self.sets[iid]
        self.update_status(f"Deleted Profile Set {removed_id}")

    def move_selected_up(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a row to move.")
            return
        
        iid = selected[0]
        idx = self.tree.index(iid)
        if idx == 0:
            return 
            
        # Move row element position inside Treeview
        self.tree.move(iid, self.tree.parent(iid), idx - 1)
        self.update_status(f"Moved Set {self.sets[iid].set_id} Up")

    def move_selected_down(self):
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
        self.update_status(f"Moved Set {self.sets[iid].set_id} Down")


class NewSetDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Create New Experiment Set")
        self.geometry("360x520") 
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        self.result = None
        
        base_frame = ttk.Frame(self, padding=15)
        base_frame.pack(fill=tk.BOTH, expand=True)
        

        global_frame = ttk.Frame(base_frame)
        global_frame.pack(fill=tk.X, pady=(0, 15))
        global_frame.columnconfigure(1, weight=1)
        
        ttk.Label(global_frame, text="Target Temp (C) ").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_temp = ttk.Entry(global_frame, width=15)
        self.entry_temp.grid(row=0, column=1, sticky="ew", pady=5)
        
        ttk.Label(global_frame, text="Target SoC (%) ").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_soc = ttk.Entry(global_frame, width=15)
        self.entry_soc.grid(row=1, column=1, sticky="ew", pady=5)
        
        ttk.Label(global_frame, text="Sampling Start (ms) ").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_start = ttk.Entry(global_frame, width=15)
        self.entry_start.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(global_frame, text="Sample Points").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_points = ttk.Entry(global_frame, width=15)
        self.entry_points.grid(row=3, column=1, sticky="ew", pady=5)

        ttk.Label(global_frame, text="Sampling Freq (Hz) ").grid(row=4, column=0, sticky="w", pady=5)
        self.entry_freq = ttk.Entry(global_frame, width=15)
        self.entry_freq.grid(row=4, column=1, sticky="ew", pady=5)
        
        ttk.Separator(base_frame, orient="horizontal").pack(fill=tk.X, pady=(0, 10))


        self.notebook = ttk.Notebook(base_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.tab1 = ttk.Frame(self.notebook, padding=10)
        self.tab2 = ttk.Frame(self.notebook, padding=10)
        self.tab3 = ttk.Frame(self.notebook, padding=10)
        
        self.notebook.add(self.tab1, text="EIS")
        self.notebook.add(self.tab2, text="VRP")
        self.notebook.add(self.tab3, text="CCCV")

        self.tab1.columnconfigure(1, weight=1)
        
        ttk.Label(self.tab1, text="Target IDC (mA) ").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_idc = ttk.Entry(self.tab1, width=15)
        self.entry_idc.grid(row=0, column=1, sticky="ew", pady=5)
        
        ttk.Label(self.tab1, text="Target IAC List ").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_iac = ttk.Entry(self.tab1, width=15)
        self.entry_iac.grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(self.tab1, text="Duration (ms) ").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_duration = ttk.Entry(self.tab1, width=15)
        self.entry_duration.grid(row=2, column=1, sticky="ew", pady=5)

        info_frame = ttk.Frame(self.tab1)
        info_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        ttk.Label(info_frame, text="Οι AC συνιστώσες να έχουν τη μορφή \n(f1,p1,I1),(f2,p2,I2),...").grid()
        
        self.tab2.columnconfigure(1, weight=1)
        
        ttk.Label(self.tab2, text="Excitation I (mA) ").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_excitation_i = ttk.Entry(self.tab2, width=15)
        self.entry_excitation_i.grid(row=0, column=1, sticky="ew", pady=5)
        
        ttk.Label(self.tab2, text="Excitation Time (s) ").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_excitation_time = ttk.Entry(self.tab2, width=15)
        self.entry_excitation_time.grid(row=1, column=1, sticky="ew", pady=5)
        
        ttk.Label(self.tab2, text="Relaxation Time (s) ").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_relaxation_time = ttk.Entry(self.tab2, width=15)
        self.entry_relaxation_time.grid(row=2, column=1, sticky="ew", pady=5)

        self.tab3.columnconfigure(1, weight=1)

        ttk.Label(self.tab3, text="CC stage I (mA) ").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_charge_i = ttk.Entry(self.tab3, width=15)
        self.entry_charge_i.grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(self.tab3, text="CC stage V limit (mV) ").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_charge_v_lim = ttk.Entry(self.tab3, width=15)
        self.entry_charge_v_lim.grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(self.tab3, text="CV stage V (mV) ").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_charge_v = ttk.Entry(self.tab3, width=15)
        self.entry_charge_v.grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Label(self.tab3, text="CV stage time (s) ").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_charge_v_time = ttk.Entry(self.tab3, width=15)
        self.entry_charge_v_time.grid(row=3, column=1, sticky="ew", pady=5)

        btn_frame = ttk.Frame(base_frame)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        
        ttk.Button(btn_frame, text="Άκυρο", command=self.destroy).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ttk.Button(btn_frame, text="OK", command=self.on_submit).grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        self.bind("<Return>", lambda event: self.on_submit())
        self.wait_window(self)

    def on_submit(self):
        temp = self.entry_temp.get()
        soc = self.entry_soc.get()
        start = self.entry_start.get()
        points = self.entry_points.get()
        freq = self.entry_freq.get()
        idc = self.entry_idc.get()
        iac = self.entry_iac.get()
        duration = self.entry_duration.get()
        excitation_i = self.entry_excitation_i.get()
        excitation_time = self.entry_excitation_time.get()
        relaxation_time = self.entry_relaxation_time.get()
        charge_i = self.entry_charge_i.get()
        charge_v_lim = self.entry_charge_v_lim.get()
        charge_v = self.entry_charge_v.get()
        charge_v_time = self.entry_charge_v_time.get()
        
        try:
            base_params = {
                "temp": int(temp),
                "soc": int(soc),
                "start": int(start),
                "points": int(points),
                "freq": int(freq)
            }

            if idc != "" and iac != "":
                try:
                    cleaned = iac.strip().strip("()")
                    blocks = cleaned.split("),(")
                    result = []
                    for block in blocks:
                        if not block.strip():
                            continue
                        # Split individual digits by comma and cast to integers
                        item_tuple = tuple(int(x.strip()) for x in block.split(","))
                        result.append(item_tuple)
                except:
                    messagebox.showwarning("Error", "Please check your IAC values.")

                base_params.update({
                    "mode": "EIS",
                    "params": {
                        "idc": int(idc), 
                        "iac": result, 
                        "duration": int(duration)
                    },
                    "commands": ["SET_SOC "+soc, "SET_TEMP "+temp, "SSTART "+start, "SPOINTS "+points, "SFREQ "+freq
                    ]
                })


            elif excitation_i != "" and excitation_time != "" and relaxation_time != "":
                base_params.update({
                    "mode": "VRP",
                    "params": {"excitation_i": int(excitation_i), "excitation_time": int(excitation_time), "relaxation_time": int(relaxation_time)},
                    "commands": ["SET_SOC "+soc, "SET_TEMP "+temp, "SSTART "+start, "SPOINTS "+points, "SFREQ "+freq
                    ]
                })
            else:
                base_params.update({
                    "mode": "CHARGE",
                    "params": {"charge_i": int(charge_i), "charge_v_lim": int(charge_v_lim), "charge_v": int(charge_v), "charge_v_time": int(charge_v_time)},
                    "commands": ["SET_SOC "+soc, "SET_TEMP "+temp, "SSTART "+start, "SPOINTS "+points, "SFREQ "+freq
                    ]
                })
            
            self.result = base_params
            self.destroy()

        except ValueError:
            messagebox.showwarning("Error", "Please check your values.")


class BatteryDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Battery Dashboard")
        self.geometry("1050x620")
        self.minimum_size = (850, 520)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=7, minsize=550)
        self.grid_columnconfigure(1, weight=3, minsize=250)
        
        self.set_counter = 1
        
        self.style = ttk.Style()
        self.style.configure("Abort.TButton", foreground="red")
        
        # --- MENU BAR CONFIGURATIONS ---
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Set Wizard", command=self.handle_new_set)
        file_menu.add_command(label="Import...", command=self.handle_import_sets)
        file_menu.add_command(label="Export...", command=self.handle_export_sets)
        file_menu.add_separator()
        file_menu.add_command(label="Exit Application", command=self.quit)
        
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About Dashboard", command=lambda: messagebox.showinfo("About", "Structured Telemetry Workspace"))
        
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu_bar)
        
        self.experiment_sets = Panel(self, status_callback=self.set_status)
        self.experiment_sets.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        right_frame = ttk.Frame(self, padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # --- TELEMETRY DISPLAYS GROUP ---
        display_group = ttk.LabelFrame(right_frame, text="Live Telemetry", padding=10)
        display_group.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        display_group.grid_columnconfigure(1, weight=1)
        
        self.status_variables = {
            "Battery": tk.StringVar(value="-- °C"),
            "Peltier": tk.StringVar(value="-- °C"),
            "Heatsink": tk.StringVar(value="-- °C"),
            "SoC": tk.StringVar(value="-- %"),
            "Voltage": tk.StringVar(value="-- V"),
            "Current": tk.StringVar(value="-- A")
        }
        
        for i, (label_text, var) in enumerate(self.status_variables.items()):
            ttk.Label(display_group, text=f"{label_text}:", font=("Arial", 10, "bold")).grid(row=i, column=0, sticky="w", pady=4, padx=5)
            ttk.Label(display_group, textvariable=var, font=("Arial", 10), background="#EAEAEA", width=12, anchor="center").grid(row=i, column=1, sticky="ew", pady=4, padx=5)

        # --- BUTTONS GROUP ---
        btn_group = ttk.LabelFrame(right_frame, text="Actions", padding=10)
        btn_group.grid(row=1, column=0, sticky="ew")
        btn_group.grid_columnconfigure(0, weight=1)
        btn_group.grid_columnconfigure(1, weight=1)
        
        ttk.Button(btn_group, text="New Set", command=self.handle_new_set).grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Button(btn_group, text="Delete Set", command=self.experiment_sets.delete_selected).grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Button(btn_group, text="Sync", command=self.handle_sync).grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Button(btn_group, text="Move Up", command=self.experiment_sets.move_selected_up).grid(row=3, column=0, sticky="ew", pady=5, padx=(0, 2))
        ttk.Button(btn_group, text="Move Down", command=self.experiment_sets.move_selected_down).grid(row=3, column=1, sticky="ew", pady=5, padx=(2, 0))
        
        ttk.Button(btn_group, text="RUN", command=self.handle_run).grid(row=4, column=0, sticky="ew", pady=5, padx=(0, 2))
        ttk.Button(btn_group, text="ABORT", command=self.handle_abort, style="Abort.TButton").grid(row=4, column=1, sticky="ew", pady=5, padx=(2, 0))
        
        # Re-inserted original position for CSV downloads
        ttk.Button(btn_group, text="Download CSV...", command=self.download_measurements).grid(row=5, column=0, columnspan=2, sticky="ew", pady=(15, 5))
        
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self, textvariable=self.status_var, anchor="w", padx=10, pady=4, bd=1, relief=tk.SUNKEN, background="#F0F0F0")
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.set_status("System Workspace Ready")

    def set_status(self, text_message):
        self.status_var.set(f"{text_message}")

    def handle_new_set(self):
        self.set_status("Awaiting profile configurations...")
        dialog = NewSetDialog(self)
        if dialog.result:
            new_set_obj = Set(
                set_id=self.set_counter,
                temp=dialog.result["temp"],
                soc=dialog.result["soc"],
                status="Pending",
                mode=dialog.result["mode"],
                sampling_freq=dialog.result["freq"],
                sample_points=dialog.result["points"],
                sample_time=dialog.result["start"],
                params=dialog.result["params"],
                commands=dialog.result["commands"]
            )
            self.set_counter += 1
            self.experiment_sets.add_set(new_set_obj)
        else:
            self.set_status("Configuration creation canceled.")

    def handle_export_sets(self):
        ordered_sets = self.experiment_sets.get_ordered_sets()
        if not ordered_sets:
            messagebox.showwarning("Export Warning", "The workspace profile table is empty. Nothing to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Export Profile Set Sequences"
        )
        if not file_path:
            return

        try:
            serializable_list = [s.to_dict() for s in ordered_sets]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_list, f, indent=4)
            self.set_status(f"Successfully exported {len(serializable_list)} experiment sets.")
            messagebox.showinfo("Export Successful", f"Saved configuration profiles to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to save profiles to text file:\n{str(e)}")

    def handle_import_sets(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Import Profile Set Sequences"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)

            if not isinstance(raw_data, list):
                raise ValueError("Invalid file structure layout format framework parsed framework settings.")

            choice = messagebox.askyesnocancel(
                "Import Option", 
                "Would you like to clear the current workspace table layout before loading the configurations?\n\n"
                "[Yes] = Clear Table and Load\n[No] = Append to Existing Table\n[Cancel] = Abort Action"
            )
            
            if choice is None:
                return
            elif choice is True:
                self.experiment_sets.clear_all()
                self.set_counter = 1

            imported_count = 0
            for item in raw_data:
                loaded_set = Set.from_dict(item)
                
                if choice is False or loaded_set.set_id < self.set_counter:
                    loaded_set.set_id = self.set_counter
                
                if loaded_set.set_id >= self.set_counter:
                    self.set_counter = loaded_set.set_id + 1

                self.experiment_sets.add_set(loaded_set)
                imported_count += 1

            self.set_status(f"Successfully loaded {imported_count} configuration profiles.")
        except Exception as e:
            messagebox.showerror("Import Error", f"Could not parse setup configuration data indices elements:\n{str(e)}")

    def handle_sync(self):
        print({iid: s.to_dict() for iid, s in self.experiment_sets.sets.items()})

    def handle_run(self):
        self.set_status("Sending Run Command and Set List to Microcontroller...")

    def handle_abort(self):
        self.set_status("Sending Halt Command to Microcontroller...")

    def download_measurements(self):
        self.set_status("Downloading...")


if __name__ == "__main__":
    app = BatteryDashboard()
    app.mainloop()
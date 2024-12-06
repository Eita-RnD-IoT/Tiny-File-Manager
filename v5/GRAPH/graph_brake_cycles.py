import json
import pandas as pd
import plotly.express as px
import os
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont

# Load directory configuration
DIRECTORY_JSON = "JSON/dir.json"
if not os.path.exists(DIRECTORY_JSON):
    print("Error: 'dir.json' does not exist.")
    exit(1)

with open(DIRECTORY_JSON, "r") as file:
    dir_data = json.load(file)
    ROOT = dir_data["root"]
    MEASUREMENT_DATA_ANALYSIS = dir_data["measurement"][2]["measurement_data_analysis"]
    GRAPH_JOBSITE = dir_data["graph"][2]["graph_jobsite"]

jobsite_filtering_dir = os.path.join(ROOT, GRAPH_JOBSITE, 'jobsite.json')
if not os.path.exists(jobsite_filtering_dir):
    print("Error: 'jobsite.json' file not found.")
    exit(1)

with open(jobsite_filtering_dir, "r") as file:
    jobsite_data = json.load(file)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Tkinter App
class LiftSelectorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lift Selection")
        self.geometry("600x400")
        self.minsize(500, 400)

        # Configure grid layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Font settings for a consistent and readable UI
        self.font = tkFont.Font(family="Helvetica", size=12)

        # Frame to add margin from parent window
        self.main_frame = tk.Frame(self, padx=20, pady=20)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # State Selection
        self.state_label = tk.Label(self.main_frame, text="Select State:", font=self.font)
        self.state_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.state_var = tk.StringVar()
        self.state_dropdown = ttk.Combobox(
            self.main_frame, textvariable=self.state_var, values=list(jobsite_data.keys()), state="readonly", font=self.font
        )
        self.state_dropdown.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.state_dropdown.bind("<<ComboboxSelected>>", self.on_state_select)

        # Jobsite Selection
        self.jobsite_label = tk.Label(self.main_frame, text="Select Jobsite:", font=self.font)
        self.jobsite_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.jobsite_var = tk.StringVar()
        self.jobsite_dropdown = ttk.Combobox(self.main_frame, textvariable=self.jobsite_var, state="readonly", font=self.font)
        self.jobsite_dropdown.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        self.jobsite_dropdown.bind("<<ComboboxSelected>>", self.on_jobsite_select)

        # Lift Selection
        self.lift_label = tk.Label(self.main_frame, text="Select Lift:", font=self.font)
        self.lift_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.lift_var = tk.StringVar()
        self.lift_dropdown = ttk.Combobox(self.main_frame, textvariable=self.lift_var, state="readonly", font=self.font)
        self.lift_dropdown.grid(row=5, column=0, sticky="ew", padx=10, pady=5)

        # Buttons
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.grid(row=6, column=0, sticky="ew", padx=10, pady=10)
        self.button_frame.grid_columnconfigure(0, weight=1)

        self.submit_button = tk.Button(self.button_frame, text="Submit", command=self.generate_graph, font=self.font)
        self.submit_button.pack(side=tk.LEFT, padx=10)

        self.exit_button = tk.Button(self.button_frame, text="Exit", command=self.exit_app, font=self.font)
        self.exit_button.pack(side=tk.RIGHT, padx=10)

        # Selected Data
        self.selected_state = None
        self.selected_jobsite = None
        self.selected_lift = None

    def on_state_select(self, event):
        """Update jobsite dropdown based on selected state and clear lower selections."""
        self.selected_state = self.state_var.get()
        jobsites = [jobsite["Jobsite"] for jobsite in jobsite_data[self.selected_state]]

        # Update jobsite dropdown
        self.jobsite_var.set("")  # Clear the current jobsite selection
        self.jobsite_dropdown.config(values=jobsites)

        # Clear lift dropdown
        self.lift_var.set("")  # Clear the current lift selection
        self.lift_dropdown.config(values=[])
        self.selected_jobsite = None
        self.selected_lift = None

    def on_jobsite_select(self, event):
        """Update lift dropdown based on selected jobsite and clear lower selections."""
        self.selected_jobsite = self.jobsite_var.get()
        lifts = []
        for jobsite in jobsite_data[self.selected_state]:
            if jobsite["Jobsite"] == self.selected_jobsite:
                lifts = [list(lift.values())[0] for lift in jobsite["Lift PMA"]]
                break

        # Update lift dropdown
        self.lift_var.set("")  # Clear the current lift selection
        self.lift_dropdown.config(values=lifts)
        self.selected_lift = None
    

    def generate_graph(self):
        """Generate the graph based on the selected lift and updated parameters."""
        self.selected_lift = self.lift_var.get()
        if not self.selected_state or not self.selected_jobsite or not self.selected_lift:
            messagebox.showerror("Error", "Please make all selections.")
            return

        # Load floor count data
        json_file = os.path.join(ROOT, MEASUREMENT_DATA_ANALYSIS, 'BRAKE OPENING AND CLOSING COUNT', f'BOCC-{self.selected_lift}.json')
        if not os.path.exists(json_file):
            messagebox.showerror("Error", f"File not found: {json_file}")
            return

        with open(json_file, "r") as file:
            data = json.load(file)

        # Extract all files data
        files_data = data.get("files", {})
        if not files_data:
            messagebox.showerror("Error", f"No data found in {json_file}.")
            return

        rows = []
        for file_name, params in files_data.items():
            date_range = file_name.split("-FROM_")[1].replace(".csv", "").split("_TO_")
            start_date, end_date = date_range

            rows.append({
                "Start Time": pd.to_datetime(start_date, format="%Y-%m-%d%H%M%S").strftime('%Y-%m-%d'),
                "_mb1s_0": params["_mb1s"]["0"],
                "_mb1s_1": params["_mb1s"]["1"],
                "_mb2s_0": params["_mb2s"]["0"],
                "_mb2s_1": params["_mb2s"]["1"],
                "cycles": params["cycles"],
            })

        # Create DataFrame
        df = pd.DataFrame(rows)

        # Plot graph using Plotly
        fig = px.bar(
            df,
            x="Start Time",
            y=["_mb1s_0", "_mb1s_1", "_mb2s_0", "_mb2s_1"],
            title=f"Lift Data for {self.selected_lift}",
            labels={"value": "Counts", "Start Time": "Date"},
        )
        
        # Add cycles as a line on a secondary y-axis
        fig.add_scatter(
            x=df["Start Time"],
            y=df["cycles"],
            mode="lines+markers",
            name="Cycles",
            yaxis="y2",
            line=dict(color="red"),
        )

        # Update layout for dual axes
        fig.update_layout(
            yaxis=dict(title="Counts"),
            yaxis2=dict(title="Cycles", overlaying="y", side="right"),
            barmode="group",
            hovermode="x unified",
        )

        fig.show()

        

    def exit_app(self):
        """Exit the application."""
        clear_screen()
        self.destroy()


if __name__ == "__main__":
    app = LiftSelectorApp()
    app.mainloop()

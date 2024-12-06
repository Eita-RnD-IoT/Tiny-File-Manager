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
        """Generate the graph based on the selected lift."""
        self.selected_lift = self.lift_var.get()
        if not self.selected_state or not self.selected_jobsite or not self.selected_lift:
            messagebox.showerror("Error", "Please make all selections.")
            return

        # Path to the file
        json_file = os.path.join(ROOT, MEASUREMENT_DATA_ANALYSIS, 'MODE FLOOR COUNT', f'MFC-{self.selected_lift}.json.json')
        if not os.path.exists(json_file):
            messagebox.showerror("Error", f"File not found: {json_file}")
            return

        with open(json_file, "r") as file:
            data = json.load(file)

        # Extract file modes and cycles data
        files_data = data.get("file_modes", {})
        if not files_data:
            messagebox.showerror("Error", f"No data found in {json_file}.")
            return

        # Prepare a list to collect cycles data and corresponding dates
        rows = []
        for file_name, cycles in files_data.items():
            date_range = file_name.split("-FROM_")[1].split(".csv")[0]  # Extract date from file name
            start_date, end_date = date_range.split("_TO_")

            # Add the cycles and date information
            rows.append({
                "Start Date": start_date,
                "End Date": end_date,
                "Cycles": cycles
            })

        # Create DataFrame from the rows
        df = pd.DataFrame(rows)

        # Calculate the mode (most frequent) value of 'Cycles' column
        mode_value = df['Cycles'].mode()[0]  # This will give the most frequent cycle count
        mode_count = df[df['Cycles'] == mode_value].shape[0]  # Count how many times this mode appears

        # Create a new DataFrame for plotting the mode across the dates
        mode_df = pd.DataFrame({
            "Date": df["Start Date"],
            "Mode (Most Frequent Cycle)": [mode_value] * len(df),
            "Frequency": [mode_count] * len(df)
        })

        # Plot the mode (most frequent cycles) over time
        fig = px.line(
            mode_df,
            x="Date",
            y="Mode (Most Frequent Cycle)",
            title=f"({self.selected_lift}) Most Frequent Lift Mode Over Time",
            labels={"Mode (Most Frequent Cycle)": "Most Frequent Mode (Cycles)", "Date": "Date"},
            markers=True,
        )
        fig.update_layout(
            xaxis=dict(title="Date", tickangle=45),
            yaxis=dict(title="Most Frequent Mode (Cycle Count)"),
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

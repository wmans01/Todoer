import tkinter as tk
from todoist_api_python.api import TodoistAPI
from datetime import date, timedelta

api = TodoistAPI("API_KEY_HERE")

bg_color = "#1E1E1E"
text_color = "#FFFFFF"
secondary_bg = "#2D2D2D"
scrollbar_bg = "#3D3D3D"
scrollbar_active = "#4D4D4D"
priority_colors = {
    1: "#B0C4DE",
    2: "#98FB98",
    3: "#FFA07A",
    4: "#FF6B6B"
}

class TaskItem(tk.Frame):
    def __init__(self, master, task, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.task = task
        self.completed = False
        
        # Configure the frame
        self.configure(bg=bg_color)
        
        # Create a sub-frame for the task content with slightly lighter background
        self.content_frame = tk.Frame(self, bg=secondary_bg, padx=10, pady=5)
        self.content_frame.pack(fill="x", expand=True)

        self.canvas = tk.Canvas(self.content_frame, width=20, height=20, 
                              highlightthickness=0, bg=secondary_bg)
        self.circle = self.canvas.create_oval(2, 2, 18, 18, outline=text_color, width=2)
        self.canvas.bind("<Button-1>", self.toggle_complete)
        self.canvas.pack(side="left", padx=(5, 15))

        # Create a frame for the text content
        text_frame = tk.Frame(self.content_frame, bg=secondary_bg)
        text_frame.pack(side="left", fill="x", expand=True)

        priority = getattr(task, 'priority', 4)
        task_color = priority_colors.get(priority, priority_colors[4])

        self.title_label = tk.Label(text_frame, 
                                  text=task.content,
                                  anchor="w", 
                                  wraplength=360, 
                                  justify="left", 
                                  font=("Helvetica", 12, "bold"),
                                  bg=secondary_bg,
                                  fg=task_color)
        self.title_label.pack(fill="x")

        if task.due:
            self.date_label = tk.Label(text_frame,
                                     text=f"Due: {task.due.date.strftime('%a %b %d')}",
                                     anchor="w",
                                     font=("Helvetica", 10),
                                     bg=secondary_bg,
                                     fg="#808080")
            self.date_label.pack(fill="x")

    def toggle_complete(self, event):
        if not self.completed:
            self.completed = True
            
            def complete_task():
                try:
                    api.complete_task(self.task.id)
                    # print(f"Task '{self.task.content}' marked complete.")
                    # Remove the task after successful completion
                    self.pack_forget()
                except Exception as e:
                    print(f"Error completing task: {e}")

            # Run the completion in a separate thread to avoid freezing UI
            import threading
            threading.Thread(target=complete_task).start()

# --- Filter function ---
def get_todays_tasks():
    try:
        today = date.today()
        today_tasks = []

        paginator = api.get_tasks(limit=100)
        count = 0

        for page in paginator:
            for task in page:  # page is a list of Task objects
                count += 1
                due_date = task.due.date if task.due else "No due date"
                # print(f"Task: {task.content} — Due: {due_date}")
                if task.due and task.due.date == today:
                    today_tasks.append(task)

        # Sort tasks by priority (high to low)
        today_tasks.sort(key=lambda x: getattr(x, 'priority', 4), reverse=True)
        return today_tasks

    except Exception as e:
        print(f"Error: {e}")
        return []

def get_upcoming_tasks():
    try:
        today = date.today()
        upcoming = []

        paginator = api.get_tasks(limit=100)
        for page in paginator:
            for task in page:
                if task.due:
                    due = task.due.date
                    if today < due <= today + timedelta(days=7):
                        upcoming.append(task)
        
        # Sort tasks by priority (high to low)
        upcoming.sort(key=lambda x: getattr(x, 'priority', 4), reverse=True)
        return upcoming
    except Exception as e:
        print(f"Error: {e}")
        return []

def refresh_tasks():
    # Store current scroll position
    current_scroll = canvas.yview()
    
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    # --- Today Section ---
    tk.Label(scrollable_frame, text="Today", font=("Helvetica", 16, "bold"), 
             bg=bg_color, fg=text_color).pack(pady=(0, 10))

    today_tasks = get_todays_tasks()
    if isinstance(today_tasks, str):
        tk.Label(scrollable_frame, text=today_tasks, fg="#FF6B6B", bg=bg_color).pack()
    elif not today_tasks:
        tk.Label(scrollable_frame, text="No tasks for today! 🎉", fg="#98FB98", bg=bg_color).pack()
    else:
        for task in today_tasks:
            task_item = TaskItem(scrollable_frame, task)
            task_item.pack(fill="x", pady=5)

    # --- Upcoming Section ---
    tk.Label(scrollable_frame, text="Upcoming", font=("Helvetica", 16, "bold"), 
             bg=bg_color, fg=text_color).pack(pady=(20, 10))

    upcoming_tasks = get_upcoming_tasks()
    if isinstance(upcoming_tasks, str):
        tk.Label(scrollable_frame, text=upcoming_tasks, fg="#FF6B6B", bg=bg_color).pack()
    elif not upcoming_tasks:
        tk.Label(scrollable_frame, text="No upcoming tasks.", fg="#B0C4DE", bg=bg_color).pack()
    else:
        for task in upcoming_tasks:
            task_item = TaskItem(scrollable_frame, task)
            task_item.pack(fill="x", pady=5)

    # Update canvas scroll region
    canvas.configure(scrollregion=canvas.bbox("all"))
    
    # Restore scroll position
    canvas.yview_moveto(current_scroll[0])

def periodic_refresh():
    refresh_tasks()
    # Schedule next refresh
    root.after(60 * 1000, periodic_refresh)  # every 2 minutes

# --- GUI Setup ---
root = tk.Tk()
root.title("Today's Tasks")
root.geometry("400x600")
root.attributes('-fullscreen', True)

# Configure dark theme colors
bg_color = "#1E1E1E"  # Dark background
text_color = "#FFFFFF"  # White text
secondary_bg = "#2D2D2D"  # Slightly lighter background for frames
priority_colors = {
    1: "#B0C4DE",  # High priority - Red
    2: "#98FB98",  # Medium priority - Light Salmon
    3: "#FFA07A",  # Low priority - Pale Green
    4: "#FF6B6B"   # No priority - Light Steel Blue
}

root.configure(bg=bg_color)

# Create main container with padding
main_container = tk.Frame(root, bg=bg_color, padx=20, pady=20)
main_container.pack(fill="both", expand=True)

# Create canvas
canvas = tk.Canvas(main_container, bg=bg_color, highlightthickness=0)
scrollable_frame = tk.Frame(canvas, bg=bg_color)

# Store the initial window width
initial_width = root.winfo_width() - 40  # Account for padding

# Configure canvas
def configure_scroll_region(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

scrollable_frame.bind("<Configure>", configure_scroll_region)

# Create window in canvas with fixed width
canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=initial_width)

# Pack canvas
canvas.pack(side="left", fill="both", expand=True)

# Smooth scrolling with animation
def smooth_scroll(event):
    # Get the current scroll position
    current_pos = canvas.yview()
    
    # Calculate the new position with a smaller step
    if event.delta > 0:
        # Scrolling up
        new_pos = max(0, current_pos[0] - 0.01)  # Even smaller step for smoother scrolling
    else:
        # Scrolling down
        new_pos = min(1, current_pos[0] + 0.01)  # Even smaller step for smoother scrolling
    
    # Apply the new position
    canvas.yview_moveto(new_pos)

# Bind mousewheel to smooth scroll
canvas.bind_all("<MouseWheel>", smooth_scroll)

# Bind window resize
def on_window_resize(event):
    if event.widget == root:  # Only handle root window resize
        canvas_width = event.width - 40  # Account for padding
        canvas.itemconfig(canvas_window, width=canvas_width)

root.bind("<Configure>", on_window_resize)

refresh_tasks()
periodic_refresh()
root.mainloop()
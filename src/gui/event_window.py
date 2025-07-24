"""Floating window for displaying event data.

This module provides a floating window to display event data during test execution.
It includes an EventWindow class that updates the displayed event information and handles window dragging.

The window displays real-time information about events being recorded or executed,
including event counter, position, type, action, and timing information.
"""

import tkinter as tk
from tkinter import ttk
from src.utils.config import Config
from src.utils.process_utils import terminate_running_instance, close_existing_mouse_threads


class EventWindow(tk.Tk):
    """A floating window to display event data during test execution.
    
    This class creates a draggable, always-on-top window that displays real-time
    information about events being recorded or executed. It includes transparency
    settings and proper cleanup on window closing.
    
    Attributes:
        frame: The main frame of the window
        event_label: The label that displays the event data
        x: The initial x-coordinate for window dragging
        y: The initial y-coordinate for window dragging
    """

    def __init__(self, test_name=None, run_number=1, run_total=1):
        """Initialize the EventWindow with the given test name.
        
        Args:
            test_name: The name of the test being executed (default: None)
            run_number: Current run number (default: 1)
            run_total: Total number of runs (default: 1)
        """
        super().__init__()
        
        # Get configuration
        config = Config()
        
        # Configure window
        base_title = config.get_Event_Monitor_window_title()
        self.title(f"{base_title} - {test_name} - Run #{run_number} / {run_total}" if test_name else base_title)
        self.attributes('-alpha', config.get_Event_Monitor_window_opacity())  # Set transparency
        self.attributes('-topmost', True)  # Always on top
        
        # Set window size and position
        width, height = config.get_Event_Monitor_window_size()
        x, y = config.get_Event_Monitor_window_position()
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create frame
        self.frame = ttk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create label for event data
        self.event_label = ttk.Label(
            self.frame,
            text="Waiting for events...",
            font=('Arial', 10)
        )
        self.event_label.pack(fill=tk.BOTH, expand=True)
        
        # Make window draggable
        self.bind('<Button-1>', self.start_move)
        self.bind('<B1-Motion>', self.on_move)
        
        # Store initial position for dragging
        self.x = 0
        self.y = 0
        
        # Set up window close handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def start_move(self, event):
        """Start window dragging.
        
        Args:
            event: The event that triggered the start of dragging
        """
        self.x = event.x
        self.y = event.y
        
    def on_move(self, event):
        """Handle window dragging.
        
        Args:
            event: The event that triggered the dragging
        """
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
        
    def update_event(self, event, state="recording"):
        """Update the displayed event data.
        
        Args:
            event: The event data to display
            state: Current state ("recording" or "running") (default: "recording")
        """
        text = f"{state} |  Event #{event.counter} | Position: {event.position} | Type: {event.event_type} | Action: {event.action} | Time: {event.time}ms"
        self.event_label.config(text=text)
        
    def on_closing(self):
        """Handle window closing.
        
        This method performs cleanup operations including closing mouse listener
        threads, terminating the running instance, and destroying the window.
        
        Raises:
            Exception: For errors during cleanup (handled internally)
        """
        try:
            # Close any existing mouse listener threads
            close_existing_mouse_threads()
            
            # Terminate running instance using process_utils
            terminate_running_instance("cursor_listener.lock")
            
            # Destroy the window
            self.quit()  # Stop the mainloop
            self.destroy()  # Destroy the window
            
        except Exception as e:
            print(f"Error during window closing: {e}")
            self.quit()
            self.destroy() 
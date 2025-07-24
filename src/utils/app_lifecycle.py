"""Application lifecycle management functions.

This module provides functions for managing the application lifecycle, including
restarting and bringing the control panel to the foreground.
"""

import tkinter as tk

def restart_control_panel():
    """Restart or bring to front the control panel application.
    
    This function attempts to bring an existing control panel to the foreground.
    If no instance exists or if bringing to front fails, it creates a new instance.
    Includes comprehensive error handling for window management operations.
    
    Returns:
        None
        
    Raises:
        Exception: If there are critical errors in creating the control panel.
        This is caught and logged internally.
        
    Note:
        Uses a singleton pattern to ensure only one control panel instance exists.
        Imports ControlPanel locally to avoid circular dependencies.
    """
    from src.gui.control_panel import ControlPanel  # Import here to avoid circular dependency
    
    try:
        if ControlPanel._instance is not None:
            try:
                # Try to bring to front, if it returns False, create a new instance
                if not ControlPanel.bring_to_front_and_refresh():
                    root = tk.Tk()
                    app = ControlPanel(root)
                    root.mainloop()
            except Exception as e:
                print(f"Error bringing control panel to front: {e}")
                # If bringing to front fails, create a new instance
                root = tk.Tk()
                app = ControlPanel(root)
                root.mainloop()
        else:
            root = tk.Tk()
            app = ControlPanel(root)
            root.mainloop()
    except Exception as e:
        print(f"Error restarting control panel: {e}")
        # Last resort: try to create a new instance
        try:
            root = tk.Tk()
            app = ControlPanel(root)
            root.mainloop()
        except Exception as e:
            print(f"Fatal error creating control panel: {e}") 
"""
Dialog for configuring screenshot event data.

This module provides a dialog for configuring screenshot event data, including priority, image name,
Print Screen window configuration, step description, and step acceptance criteria.

Classes
-------
ScreenshotDialog
    A class that creates a dialog for configuring screenshot event data.
"""

import tkinter as tk
from tkinter import ttk, StringVar, Text, messagebox
import time
import os
from src.utils.config import Config
from PIL import ImageGrab, Image, ImageTk
from pynput import mouse
from src.utils.picture_handle import find_image, save_screenshot, capture_screen

class ScreenshotDialog:
    """
    A class that creates a dialog for configuring screenshot event data.

    This class initializes a Tkinter dialog that allows users to configure various aspects of a screenshot event,
    including priority, image name, Print Screen window configuration, step description, and step acceptance criteria.

    Attributes
    ----------
    result : dict or None
        The result dictionary containing the dialog data if the user pressed OK, or None if cancelled.
    config : Config
        The configuration object used to retrieve dialog and Print Screen window options.
    screenshot_counter : int
        The counter for the number of screenshots taken.
    selection_state : str
        The current state of the area selection process.
    start_x : int or None
        The x-coordinate of the first click during area selection.
    start_y : int or None
        The y-coordinate of the first click during area selection.
    current_rect : tuple or None
        The current rectangle coordinates during area selection.
    selection_canvas : tk.Canvas or None
        The canvas used for area selection.
    mouse_listener : mouse.Listener or None
        The mouse listener for area selection.
    overlay_window : tk.Toplevel or None
        The overlay window showing the selected area.

    Methods
    -------
    _create_overlay_window(x, y, width, height)
        Create a transparent overlay window showing the selected area.
    _remove_overlay_window()
        Remove the overlay window if it exists.
    _start_area_selection()
        Start the area selection process.
    _on_click(x, y, button, pressed)
        Handle mouse click event.
    _reset_ps_values()
        Reset Print Screen window values to defaults.
    _on_ok()
        Handle OK button click.
    _on_cancel()
        Handle Cancel button click.
    _handle_area_selection()
        Handle the area selection process.
    capture_screen_region(picture_name="test_image", window_type="ps")
        Capture a region of the screen by drag and drop.
    """

    def __init__(self, screenshot_counter):
        """
        Initialize the ScreenshotDialog with the given screenshot counter.

        Parameters
        ----------
        screenshot_counter : int
            The counter for the number of screenshots taken.
        """
        self.result = None
        self.config = Config()
        self.screenshot_counter = screenshot_counter
        self.selection_state = "waiting_first_click"
        self.start_x = None
        self.start_y = None
        self.current_rect = None
        self.selection_canvas = None
        self.mouse_listener = None
        self.overlay_window = None
        self.ps_original_geometry = None
        self.tsw_original_geometry = None
        
        # Get dialog configuration
        dialog_config = self.config.get('Screenshot_Dialog', {})
        # Get time sleep before minimize the window
        self.time_sleep = self.config.get_time_sleep()
        # Get Print Screen window configuration
        ps_config = self.config.get('Print_Screen_window', {})
        self.default_ps_width = ps_config.get('PSW_width', 1000)
        self.default_ps_height = ps_config.get('PSW_height', 800)
        self.default_ps_x = ps_config.get('PSW_position', {}).get('PSW_x', 10)
        self.default_ps_y = ps_config.get('PSW_position', {}).get('PSW_y', 10)
        self.default_tsw_width = ps_config.get('TSW_width', 900)
        self.default_tsw_height = ps_config.get('TSW_height', 700)
        self.default_tsw_x = ps_config.get('TSW_position', {}).get('TSW_x', 50)
        self.default_tsw_y = ps_config.get('TSW_position', {}).get('TSW_y', 50)
        self.default_rotation_start = ps_config.get('rotation_start', 0)
        self.default_rotation_end = ps_config.get('rotation_end', 0)
        self.default_rotation_state = ps_config.get('rotation_state', False)
        self.ps_original_geometry = self.default_ps_width, self.default_ps_height, self.default_ps_x, self.default_ps_y
        self.tsw_original_geometry = self.default_tsw_width, self.default_tsw_height, self.default_tsw_x, self.default_tsw_y
        
        # Create the dialog window
        self.dialog = tk.Toplevel()
        self.dialog.title(dialog_config.get("title", "Screenshot Configuration"))
        self.dialog.transient()
        self.dialog.grab_set()  # Make the dialog modal
        
        # Set window size and position from config
        width = dialog_config.get('width', 500)
        height = dialog_config.get('height', 750)  # Increased height for new section
        x = dialog_config.get('position', {}).get('x', 200)
        y = dialog_config.get('position', {}).get('y', 200)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

        # Store original window state for restore functionality
        self.is_minimized = False

                # --- SCROLLABLE AREA SETUP ---
        container = ttk.Frame(self.dialog)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
                )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        
        # Make dialog modal and always on top
        self.dialog.attributes('-topmost', True)
        self.dialog.focus_force()
        self.dialog.grab_set()
       
        # Priority Section
        low = "low - " + str(self.config.get("minmumMatchPresent_low", 30)) + "%"
        medium = "medium - " + str(self.config.get("minmumMatchPresent_medium", 50)) + "%"
        high = "high - " + str(self.config.get("minmumMatchPresent_high", 70)) + "%"
        priorities = [low, medium, high]
        ttk.Label(scrollable_frame, text="Test cut at:").pack(anchor="w", pady=(0, 5), padx=5)
        self.priority_var = StringVar(value=medium)
        priority_frame = ttk.Frame(scrollable_frame)
        priority_frame.pack(fill="x", pady=(0, 10), padx=5)
        


        for priority in priorities:
            ttk.Radiobutton(
                priority_frame,
                text=priority.capitalize(),
                variable=self.priority_var,
                value=priority
            ).pack(side="left", padx=5)
        
        # Image Name Section
        ttk.Label(scrollable_frame, text="Image name (for the image file name):").pack(anchor="w", pady=(0, 5), padx=5)
        self.imagName_text = Text(scrollable_frame, height=1, width=40)
        self.imagName_text.insert("1.0", f"Pic_{self.screenshot_counter:03d}")
        self.imagName_text.pack(fill="x", pady=(0, 10), padx=5)
        
        # Print Screen Window Section
        ttk.Label(scrollable_frame, text="area to earch the template in :").pack(anchor="w", pady=(0, 5), padx=5)
        ps_frame = ttk.Frame(scrollable_frame)
        ps_frame.pack(fill="x", pady=(0, 10), padx=5)

                # Preview Frame
        self.preview_frame = ttk.LabelFrame(scrollable_frame, text="Preview Image", padding="5")
        self.preview_frame.pack(fill="x", pady=(0, 10))

        # Preview Labels
        self.image_preview = ttk.Label(self.preview_frame, text="Image Preview")
        self.image_preview.pack(side="left", padx=5)
        
        # Width
        ttk.Label(ps_frame, text="Width:").grid(row=0, column=0, padx=5, pady=2)
        self.ps_width_var = StringVar(value=str(self.default_ps_width))
        ttk.Entry(ps_frame, textvariable=self.ps_width_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        # Height
        ttk.Label(ps_frame, text="Height:").grid(row=0, column=2, padx=5, pady=2)
        self.ps_height_var = StringVar(value=str(self.default_ps_height))
        ttk.Entry(ps_frame, textvariable=self.ps_height_var, width=10).grid(row=0, column=3, padx=5, pady=2)
        
        # X Position
        ttk.Label(ps_frame, text="X Position:").grid(row=1, column=0, padx=5, pady=2)
        self.ps_x_var = StringVar(value=str(self.default_ps_x))
        ttk.Entry(ps_frame, textvariable=self.ps_x_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        # Y Position
        ttk.Label(ps_frame, text="Y Position:").grid(row=1, column=2, padx=5, pady=2)
        self.ps_y_var = StringVar(value=str(self.default_ps_y))
        ttk.Entry(ps_frame, textvariable=self.ps_y_var, width=10).grid(row=1, column=3, padx=5, pady=2)
        
        # Buttons frame
        button_frame = ttk.Frame(ps_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=5)
        
        # Reset button
        ttk.Button(button_frame, text="Reset to Default", command=lambda: self._reset_values("ps")).pack(side="left", padx=5)
        
        # Select Area button
        #self.select_area_button = ttk.Button(button_frame, text="Select Area", command=self._start_area_selection)
        self.select_area_button = ttk.Button(button_frame, text="Select Area", command=lambda: self._handle_area_selection("ps"))
        self.select_area_button.pack(side="left", padx=5, pady=5)
        

        # template Screen Window Section
        ttk.Label(scrollable_frame, text="template Screen Window Configuration:").pack(anchor="w", pady=(0, 5), padx=5)
        ps_frame = ttk.Frame(scrollable_frame)
        ps_frame.pack(fill="x", pady=(0, 10), padx=5)

                # Preview  template Frame
        self.preview_template_frame = ttk.LabelFrame(scrollable_frame, text="Preview Template", padding="5")
        self.preview_template_frame.pack(fill="x", pady=(0, 10))

        # Preview Labels template
        self.template_preview = ttk.Label(self.preview_template_frame, text="Template Preview")
        self.template_preview.pack(side="left", padx=5)

        
        # Width
        ttk.Label(ps_frame, text="template Width:").grid(row=0, column=0, padx=5, pady=2)
        self.tsw_width_var = StringVar(value=str(self.default_tsw_width))
        ttk.Entry(ps_frame, textvariable=self.tsw_width_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        # Height
        ttk.Label(ps_frame, text="template Height:").grid(row=0, column=2, padx=5, pady=2)
        self.tsw_height_var = StringVar(value=str(self.default_tsw_height))
        ttk.Entry(ps_frame, textvariable=self.tsw_height_var, width=10).grid(row=0, column=3, padx=5, pady=2)
        
        # X Position
        ttk.Label(ps_frame, text="template X Position:").grid(row=1, column=0, padx=5, pady=2)
        self.tsw_x_var = StringVar(value=str(self.default_tsw_x))
        ttk.Entry(ps_frame, textvariable=self.tsw_x_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        # Y Position
        ttk.Label(ps_frame, text="template Y Position:").grid(row=1, column=2, padx=5, pady=2)
        self.tsw_y_var = StringVar(value=str(self.default_tsw_y))
        ttk.Entry(ps_frame, textvariable=self.tsw_y_var, width=10).grid(row=1, column=3, padx=5, pady=2)
        


        # Buttons frame
        button_frame = ttk.Frame(ps_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=5, padx=5)
        
        # Reset button
        ttk.Button(button_frame, text="Reset to Default template", command=lambda: self._reset_values("tsw")).pack(side="left", padx=5)
        
        # Select Area button
        #self.select_area_button = ttk.Button(button_frame, text="Select Area", command=self._start_area_selection)
        self.select_area_button = ttk.Button(button_frame, text="Select Area template", command=lambda: self._handle_area_selection("tsw"))
        self.select_area_button.pack(side="left", padx=5)


        # Rotation Testing Options
        rotation_frame = ttk.LabelFrame(scrollable_frame, text="template rotation", padding="5")
        rotation_frame.pack(fill="x", pady=10, padx=5)

        # Enable rotation testing
        self.enable_rotation = tk.BooleanVar(value=False)
        ttk.Checkbutton(rotation_frame, text="Enable Rotation Testing", 
                       variable=self.enable_rotation).pack(anchor="w", padx=5, pady=2)
        
        # Rotation range
        range_row = ttk.Frame(rotation_frame)
        range_row.pack(fill="x", pady=2)
        ttk.Label(range_row, text="Rotation Range:").pack(side="left", padx=2)
        self.rotation_start = tk.DoubleVar(value=-0)
        self.rotation_end = tk.DoubleVar(value=0)
        ttk.Entry(range_row, textvariable=self.rotation_start, width=8).pack(side="left", padx=2)
        ttk.Label(range_row, text="to").pack(side="left", padx=2)
        ttk.Entry(range_row, textvariable=self.rotation_end, width=8).pack(side="left", padx=2)
        ttk.Label(range_row, text="degrees").pack(side="left", padx=2)
        
        
        # Process Buttons
        check_farme = ttk.Frame(scrollable_frame)
        check_farme.pack(pady=20, fill="x")
        
        # ttk.Button(check_farme, text="check template  Image",  command=lambda: find_image().grid(row=0, column=0, padx=5)
        
        # Step Description Section
        ttk.Label(scrollable_frame, text="Step Description - Enter what this step does...:").pack(anchor="w", pady=(0, 5), padx=5)
        # Create a frame to hold the text widget and scrollbar
        desc_frame = ttk.Frame(scrollable_frame)
        desc_frame.pack(fill="x", pady=(0, 10), padx=5)
        
        # Create scrollbar for description
        desc_scrollbar = ttk.Scrollbar(desc_frame)
        desc_scrollbar.pack(side="right", fill="y")
        
        # Create text widget with scrollbar
        self.desc_text = Text(desc_frame, height=4, width=40, yscrollcommand=desc_scrollbar.set)
        self.desc_text.insert("1.0", f"Step {self.screenshot_counter:03d} - do something")
        self.desc_text.pack(side="left", fill="x", expand=True)
        
        # Configure scrollbar to work with text widget
        desc_scrollbar.config(command=self.desc_text.yview)
        
        # Step Acceptance Section
        ttk.Label(scrollable_frame, text="Step Acceptance - Enter expected outcome...:").pack(anchor="w", pady=(0, 5), padx=5)
        # Create a frame to hold the text widget and scrollbar
        accep_frame = ttk.Frame(scrollable_frame)
        accep_frame.pack(fill="x", pady=(0, 10), padx=5)
        
        # Create scrollbar for acceptance
        accep_scrollbar = ttk.Scrollbar(accep_frame)
        accep_scrollbar.pack(side="right", fill="y")
        
        # Create text widget with scrollbar
        self.accep_text = Text(accep_frame, height=4, width=40, yscrollcommand=accep_scrollbar.set)
        self.accep_text.insert("1.0", f"Step {self.screenshot_counter:03d} - result is good")
        self.accep_text.pack(side="left", fill="x", expand=True)
        
        # Configure scrollbar to work with text widget
        accep_scrollbar.config(command=self.accep_text.yview)
        
        # Button Frame
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill="x", pady=(10, 0), padx=5)
        
        ttk.Button(button_frame, text="OK", command=self._on_ok).pack(side="right", padx=5 )
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side="right", padx=5)
        
        self._minimize_window()
        # wait for the window to be created
        time.sleep( self.time_sleep)
        # Convert (width, height, x, y) to (x1, y1, x2, y2) format
        ps_width, ps_height, ps_x, ps_y = self.ps_original_geometry
        ps_coords = (ps_x, ps_y, ps_x + ps_width, ps_y + ps_height)
        self._present_image_preview(ps_coords, "ps")
        
        tsw_width, tsw_height, tsw_x, tsw_y = self.tsw_original_geometry
        tsw_coords = (tsw_x, tsw_y, tsw_x + tsw_width, tsw_y + tsw_height)
        self._present_image_preview(tsw_coords, "tsw")
        self._restore_window()

        # Set focus to the dialog window itself instead of any entry
        self.dialog.focus_set()
        
        # Prevent closing the window with the X button
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        
        # Store original window state for restore functionality


    def _handle_area_selection(self, window_type):
        """
        Handle the area selection process.

        This function handles the area selection process and returns the selected area coordinates.
        """
        # Get image name from the form
        image_name = self.imagName_text.get("1.0", "end-1c")
        if not image_name:
            image_name = f"Pic_{self.screenshot_counter:03d}"
        
        self._minimize_window()
        # wait for the window to be created
        time.sleep( self.time_sleep)
        # Call the screen capture function
        result = self.capture_screen_region(image_name, window_type)
        self._restore_window()
        if result:
            x, y, width, height = result
            if window_type == "ps":
            # Update the form fields with the selected coordinates
                self.ps_x_var.set(str(x))
                self.ps_y_var.set(str(y))
                self.ps_width_var.set(str(width))
                self.ps_height_var.set(str(height))
                screenshot = capture_screen(x, y, width, height) 
                save_screenshot(screenshot, "ps.jpg")
            elif window_type == "tsw":
                self.tsw_x_var.set(str(x))
                self.tsw_y_var.set(str(y))
                self.tsw_width_var.set(str(width))
                self.tsw_height_var.set(str(height))
                screenshot = capture_screen(x, y, width, height) 
                save_screenshot(screenshot, "tsw.jpg")
            

            # # Update instruction label
            # self.instruction_label.config(text=f"Selected area: {width}x{height} at ({x},{y})")
        # else:
            # # Selection was cancelled
            # self.instruction_label.config(text="Area selection cancelled")

    def capture_screen_region(self, picture_name="test_image", window_type="ps") -> tuple:
        """
        Capture a region of the screen by drag and drop.
        
        Args:
            picture_name (str): Name for the saved image file
            window_type (str): Type of window ("ps" for print screen, "tsw" for template screen)
            
        Returns:
            tuple: (x, y, width, height) coordinates of selected area
        """
        class ScreenCapture:
            def __init__(self, picture_name, window_type, dialog_ref):
                self.picture_name = picture_name
                self.window_type = window_type
                self.dialog_ref = dialog_ref
                self.root = tk.Tk()
                self.root.attributes('-fullscreen', True)
                self.root.attributes('-alpha', 0.3)  # Semi-transparent overlay
                self.root.configure(bg='black')
                self.root.attributes('-topmost', True)
                
                # Create canvas for drawing selection rectangle
                self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
                self.canvas.pack(fill='both', expand=True)
                
                # Variables for drag and drop
                self.start_x = None
                self.start_y = None
                self.rect = None
                self.selection_made = False
                
                # Bind events
                self.canvas.bind('<Button-1>', self.on_mouse_down)
                self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
                self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
                self.canvas.bind('<Escape>', self.cancel_capture)
                
                # Instructions
                self.canvas.create_text(
                    self.root.winfo_screenwidth() // 2, 
                    50, 
                    text="Drag to select a region. Press ESC to cancel.", 
                    fill='white', 
                    font=('Arial', 16, 'bold')
                )
                
            def on_mouse_down(self, event):
                self.start_x = event.x
                self.start_y = event.y
                if self.rect:
                    self.canvas.delete(self.rect)
                self.rect = self.canvas.create_rectangle(
                    self.start_x, self.start_y, self.start_x, self.start_y,
                    outline='red', width=2
                )
                
            def on_mouse_drag(self, event):
                if self.rect:
                    self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
                    
            def on_mouse_up(self, event):
                if self.start_x is not None and self.start_y is not None:
                    x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
                    x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
                    
                    # Ensure minimum size
                    if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
                        self.selection_coords = (x1, y1, x2, y2)
                        self.selection_made = True
                        self.root.quit()
                    else:
                        # Selection too small, clear it
                        if self.rect:
                            self.canvas.delete(self.rect)
                            self.rect = None
                            
            def cancel_capture(self, event=None):
                self.selection_made = False
                self.root.quit()
                
            def capture(self):
                self.root.mainloop()
                self.root.destroy()
                
                if not self.selection_made:
                    return None
                    
                # Wait a moment for the window to close
                time.sleep(0.1)
                x1, y1, x2, y2 = self.selection_coords
                self.dialog_ref._present_image_preview(self.selection_coords, self.window_type)

                # # Capture the screen
                # screenshot = ImageGrab.grab()
                
                # # Crop to selected region
                # x1, y1, x2, y2 = self.selection_coords
                # cropped = screenshot.crop((x1, y1, x2, y2))
                
                # # Resize for preview (max 200x200 pixels)
                # preview_size = (200, 200)
                # cropped.thumbnail(preview_size, Image.Resampling.LANCZOS)
                
                # # Convert to PhotoImage for tkinter
                # photo = ImageTk.PhotoImage(cropped)
                
                # # Update the appropriate preview label
                # if self.window_type == "tsw":
                #     self.dialog_ref.template_preview.config(image=photo, text="")
                #     self.dialog_ref.template_preview.image = photo  # Keep a reference
                # else:  # ps
                #     self.dialog_ref.image_preview.config(image=photo, text="")
                #     self.dialog_ref.image_preview.image = photo  # Keep a reference
                
                # Return coordinates (x, y, width, height)
                return (x1, y1, x2 - x1, y2 - y1)
        
        # Create and run the screen capture
        capture_tool = ScreenCapture(picture_name, window_type, self)
        return capture_tool.capture()

    def _present_image_preview(self, selection_coords, window_type):
        """
        Present the image preview.
        """
        # Capture the screen
        screenshot = ImageGrab.grab()


        # Crop to selected region
        x1, y1, x2, y2 = selection_coords
        cropped = screenshot.crop((x1, y1, x2, y2))
                
        # Resize for preview (max 200x200 pixels)
        preview_size = (200, 200)
        cropped.thumbnail(preview_size, Image.Resampling.LANCZOS)
                
        # Convert to PhotoImage for tkinter
        photo = ImageTk.PhotoImage(cropped)
                
        # Update the appropriate preview label
        if window_type == "tsw":
            self.template_preview.config(image=photo, text="")
            self.template_preview.image = photo  # Keep a reference
        else:  # ps
            self.image_preview.config(image=photo, text="")
            self.image_preview.image = photo  # Keep a reference

    def _reset_values(self, window_type):
        """
        Reset Print Screen (_ps_) or Template Screen (_tsw_) window values to defaults.

        This function resets the Print Screen or Template Screen window values to their default values.
        """
        self._minimize_window()
        # wait for the window to be created
        time.sleep( self.time_sleep)
        if window_type == "ps":
            self.ps_width_var.set(str(self.default_ps_width))
            self.ps_height_var.set(str(self.default_ps_height))
            self.ps_x_var.set(str(self.default_ps_x))
            self.ps_y_var.set(str(self.default_ps_y))

            # Convert (width, height, x, y) to (x1, y1, x2, y2) format
            ps_width, ps_height, ps_x, ps_y= self.ps_original_geometry
            ps_coords = (ps_x, ps_y, ps_x + ps_width, ps_y + ps_height)
            self._present_image_preview(ps_coords, "ps")
            # self.image_preview.config(image=None, text="")
            # if hasattr(self.image_preview, 'image'):
            #     self.image_preview.image = None  # Remove reference to the image
        elif window_type == "tsw":
            self.tsw_width_var.set(str(self.default_tsw_width))
            self.tsw_height_var.set(str(self.default_tsw_height))
            self.tsw_x_var.set(str(self.default_tsw_x))
            self.tsw_y_var.set(str(self.default_tsw_y))

            # Convert (width, height, x, y) to (x1, y1, x2, y2) format
            tsw_width, tsw_height,tsw_x, tsw_y = self.tsw_original_geometry
            tsw_coords = (tsw_x, tsw_y, tsw_x + tsw_width, tsw_y + tsw_height)
            self._present_image_preview(tsw_coords, "tsw")
            # self.template_preview.config(image=None, text="")
            # if hasattr(self.template_preview, 'image'):
            #     self.template_preview.image = None  # Remove reference to the template image
        self._restore_window()
            
    def _minimize_window(self):
        """
        Minimize the dialog window.
        This function minimizes the dialog window to the taskbar.
        """
        
        self.dialog.iconify()
        self.is_minimized = True

    def _restore_window(self):
        """
        Restore the dialog window to its original size and position.
        This function restores the dialog window from minimized state to its original geometry.
        """
        if self.is_minimized:
            self.dialog.deiconify()
            self.dialog.geometry()
            self.is_minimized = False
            self.dialog.focus_force()  # Bring window to front and give it focus

    def _on_ok(self):
        """
        Handle OK button click.

        This function collects the dialog data, validates the Print Screen window values,
        and stores the result in the result dictionary.
        """
        # Get text content
        image_name = self.imagName_text.get("1.0", "end-1c")
        step_desc = self.desc_text.get("1.0", "end-1c")
        step_accep = self.accep_text.get("1.0", "end-1c")


        # check the bouderies coodinate of the template image to make sure oits not out of the search area
        tsw_x = int(self.tsw_x_var.get())
        tsw_y = int(self.tsw_y_var.get())
        tsw_width = int(self.tsw_width_var.get())
        tsw_height = int(self.tsw_height_var.get())
        ps_x = int(self.ps_x_var.get())
        ps_y = int(self.ps_y_var.get())
        ps_width = int(self.ps_width_var.get())
        ps_height = int(self.ps_height_var.get())

        if tsw_x < ps_x or tsw_x + tsw_width > ps_x + ps_width or tsw_y < ps_y or tsw_y + tsw_height > ps_y + ps_height:
            messagebox.showwarning(
                "boundary error",
                "make sure the template image is in the search area - boundary error",
                parent=self.dialog
            )
            return
        # check the start angle is not greater than the end angle
        if self.rotation_start.get() > self.rotation_end.get():
            messagebox.showwarning(
                "Invalid Rotation",
                "make sure the start angle is not greater than the end angle",
                parent=self.dialog
            )   
            return

        # check their is  a mtch between the template and the search area if not return
        succsess, result_image, all_high_res_results, best_high_res_confidence, best_high_res_location= find_image("tsw.jpg","ps.jpg", 0.8, 0, self.rotation_start.get(), self.rotation_end.get())
        if best_high_res_confidence[0] < 0.8:
            messagebox.showwarning(
                "Invalid match ",
                "make sure the template image is in the search area - no match: {best_high_res_confidence[0]}",
                parent=self.dialog
            )
            return

        
        # check the image name is not empty
        if not image_name:
            messagebox.showwarning(
                "Invalid Name",
                "Please enter a image name.",
                parent=self.dialog
            )
            return
        
        # Check for invalid characters
        invalid_chars = '<>:"/\\|?*'
        if any(char in image_name for char in invalid_chars):
            messagebox.showwarning(
                "Invalid Name",
                f"Image name cannot contain any of these characters: {invalid_chars}",
                parent=self.dialog
            )
            return
        
        # Get Print Screen window values
        try:
            ps_width = int(self.ps_width_var.get())
            ps_height = int(self.ps_height_var.get())
            ps_x = int(self.ps_x_var.get())
            ps_y = int(self.ps_y_var.get())
            tsw_width = int(self.tsw_width_var.get())
            tsw_height = int(self.tsw_height_var.get())
            tsw_x = int(self.tsw_x_var.get())
            tsw_y = int(self.tsw_y_var.get())
            rotation_start = int(self.rotation_start.get())
            rotation_end = int(self.rotation_end.get())
            rotation_state = self.enable_rotation.get()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for Print Screen window dimensions and position.")
            return
        
        self.result = {
            'image_name': image_name,
            'step_desc': step_desc,
            'step_accep': step_accep,
            'priority': self.priority_var.get(),
            'ps_width': ps_width,
            'ps_height': ps_height,
            'ps_x': ps_x,
            'ps_y': ps_y,
            'tsw_width': tsw_width,
            'tsw_height': tsw_height,
            'tsw_x': tsw_x,
            'tsw_y': tsw_y,
            'rotation_start': rotation_start,
            'rotation_end': rotation_end,
            'rotation_state': rotation_state
        }
        print("\nDialog data being saved:")
        print(f"Priority: {self.result['priority']}")
        print(f"Description: {self.result['step_desc']}")
        print(f"Acceptance: {self.result['step_accep']}")
        print(f"Print Screen Window: {ps_width}x{ps_height} at ({ps_x},{ps_y})")
        
        # Release grab and destroy window
        self.dialog.grab_release()
        self.dialog.destroy()
        
    def _on_cancel(self):
        """
        Handle Cancel button click.

        This function sets the result to None, removes the overlay window, and destroys the dialog.
        """
        print("\nDialog cancelled")
        self.result = None
        # Release grab and destroy window
        self.dialog.grab_release()
        self.dialog.destroy() 
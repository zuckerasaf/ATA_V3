"""Configuration utility for managing application settings.

This module provides a singleton Config class that manages application configuration
from a JSON file. It supports both development and PyInstaller bundled environments,
with comprehensive error handling and default values for all settings.

The configuration includes settings for:
- Keyboard and mouse behavior
- Window properties and positioning
- Image comparison parameters
- File paths and logging
- Event tracking preferences
"""

import json
import os
from typing import Dict, Any
import sys

class Config:
    """Singleton configuration manager for the ATA_V3 application.
    
    This class implements a singleton pattern to ensure only one configuration
    instance exists throughout the application. It loads configuration from a JSON
    file and provides type-safe access to various application settings.
    
    Attributes:
        _instance: The singleton instance of the Config class
        _config: Dictionary containing the loaded configuration data
    """
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        """Create or return the singleton instance.
        
        Returns:
            Config: The singleton instance of the Config class
        """
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the configuration by loading from file if not already loaded."""
        if not self._config:
            self._load_config()
    
    def _load_config(self):
        """Load the configuration from config.json file.
        
        This method reads the configuration file that contains application settings.
        It handles both development and PyInstaller bundled environments by detecting
        the execution context and locating the appropriate config file.
        
        The configuration includes:
            - keyboard: Keyboard settings and special keys
            - mouse: Mouse tracking and behavior settings
            - event: Event priority and step configuration
            - paths: File path configurations
            - Image_compare: Image comparison algorithm settings
            - Control_Panel: Main GUI window settings
            - startingPoint: Test starting point configuration
            - Test_Name_Dialog: Test creation dialog settings
            - track_mouse_scroll: Mouse scroll tracking preferences
            
        Raises:
            FileNotFoundError: If config file is not found (handled internally)
            json.JSONDecodeError: If config file contains invalid JSON (handled internally)
        """
        if getattr(sys, 'frozen', False):
            # Running as a PyInstaller bundle
            base_path = os.path.dirname(sys.executable)
            #base_path = sys._MEIPASS
            config_path = os.path.join(base_path, 'config.json')
        else:
            base_path = os.path.dirname(__file__)
            config_path = os.path.join(base_path, 'config.json')
        try:
            with open(config_path, 'r') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file not found at {config_path}")
            self._config = {}
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in config file at {config_path}")
            self._config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'keyboard.quit_key')
            default: Default value to return if key is not found
            
        Returns:
            Any: The configuration value or default if not found
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
                
        return value
    
    def get_keyboard_quit_key(self) -> str:
        """Get the configured quit key.
        
        Returns:
            str: The quit key (default: 'q')
        """
        return self.get('keyboard.quit_key', 'q')
    
    def get_special_keys(self) -> list:
        """Get the list of special keys to track.
        
        Returns:
            list: List of special key names to track during recording
        """
        return self.get('keyboard.special_keys', [])
    
    def get_print_screen_key(self) -> str:
        """Get the configured print screen key.
        
        Returns:
            str: The print screen key (default: 'print_screen')
        """
        return self.get('keyboard.print_screen_key', 'print_screen')
    
    def get_Event_Monitor_window_title(self) -> str:
        """Get the Event Monitor window title.
        
        Returns:
            str: The window title (default: 'Event Monitor')
        """
        return self.get('Event_Monitor_window.title', 'Event Monitor')
    
    def get_Event_Monitor_window_size(self) -> tuple:
        """Get the Event Monitor window size.
        
        Returns:
            tuple: Window size as (width, height) (default: (800, 50))
        """
        width = self.get('Event_Monitor_window.width', 800)
        height = self.get('Event_Monitor_window.height', 50)
        return (width, height)
    
    def get_Event_Monitor_window_opacity(self) -> float:
        """Get the Event Monitor window opacity.
        
        Returns:
            float: Window opacity value (default: 0.8)
        """
        return self.get('Event_Monitor_window.opacity', 0.8)
    
    def get_Event_Monitor_window_position(self) -> tuple:
        """Get the Event Monitor window position.
        
        Returns:
            tuple: Window position as (x, y) (default: (10, 10))
        """
        pos = self.get('Event_Monitor_window.position', {'x': 10, 'y': 10})
        return (pos.get('x', 10), pos.get('y', 10))
    
    def get_event_priority(self) -> str:
        """Get the event priority level.
        
        Returns:
            str: Event priority level (default: 'medium')
        """
        return self.get('event.priority', 'medium')
    
    def get_step_prefix(self) -> str:
        """Get the step prefix for event steps.
        
        Returns:
            str: Step prefix string (default: 'Step')
        """
        return self.get('event.step_prefix', 'Step')
    
    def should_track_mouse_press(self) -> bool:
        """Check if mouse press events should be tracked.
        
        Returns:
            bool: True if mouse press events should be tracked (default: True)
        """
        return self.get('mouse.track_press', True)
    
    def should_track_mouse_release(self) -> bool:
        """Check if mouse release events should be tracked.
        
        Returns:
            bool: True if mouse release events should be tracked (default: True)
        """
        return self.get('mouse.track_release', True)
        
    def get_Print_Screen_window_size(self) -> tuple:
        """Get the Print Screen window size.
        
        Returns:
            tuple: Window size as (width, height) (default: (600, 600))
        """
        width = self.get('Print_Screen_window.PSW_width', 600)
        height = self.get('Print_Screen_window.PSW_height', 600)
        return (width, height)
    
    def get_Print_Screen_window_position(self) -> tuple:
        """Get the Print Screen window position.
        
        Returns:
            tuple: Window position as (x, y) (default: (10, 10))
        """
        pos = self.get('Print_Screen_window.PSW_position', {'PSW_x': 10, 'PSW_y': 10})
        return (pos.get('PSW_x', 10), pos.get('PSW_y', 10))
        
    def get_Control_Panel_config(self) -> dict:
        """Get the Control Panel configuration.
        
        Returns:
            dict: Control Panel configuration with title, size, and position
                (default: title='Test Control Panel', width=1000, height=600, position=(100, 100))
        """
        return self.get('Control_Panel', {
            'title': 'Test Control Panel',
            'width': 1000,
            'height': 600,
            'position': {
                'x': 100,
                'y': 100
            }
        })
        
    def get_starting_point(self) -> str:
        """Get the configured starting point for tests.
        
        Returns:
            str: Starting point identifier (default: 'none')
        """
        return self.get('startingPoint', 'none')
        
    def get_Test_Name_Dialog_config(self) -> dict:
        """Get the Test Name Dialog configuration.
        
        Returns:
            dict: Test Name Dialog configuration with title, size, and position
                (default: title='New Test Configuration', width=400, height=500, position=(200, 200))
        """
        return self.get('Test_Name_Dialog', {
            'title': 'New Test Configuration',
            'width': 400,
            'height': 500,
            'position': {
                'x': 200,
                'y': 200
            }
        }) 
    
    def get_track_drag_threshold(self) -> int:
        """Get the track drag threshold.
        
        Returns:
            int: Drag threshold in pixels (default: 5)
        """
        return self.get('mouse.track_drag_threshold', 5)
    
    def should_track_mouse_scroll(self) -> bool:
        """Check if mouse scroll events should be tracked.
        
        Returns:
            bool: True if mouse scroll events should be tracked (default: True)
        """
        return self.get('track_mouse_scroll', True)  # Default to True if not specified
    
    def get_scroll_sensitivity(self) -> float:
        """Get the mouse scroll sensitivity factor.
        
        Returns:
            float: Scroll sensitivity factor (default: 0.1)
        """
        return self.get('mouse.scroll_sensitivity', 0.1)  # Default to 0.1 if not specified
    
    def get_run_log_path(self) -> str:
        """Get the run log file path.
        
        Returns:
            str: Path to the run log file (default: 'run_log.txt')
        """
        return self.get('paths.run_log_path', 'run_log.txt')
    
    def get_Image_compare_config(self) -> dict:
        """Get the Image comparison configuration.
        
        Returns:
            dict: Image comparison settings including tolerance, threshold, and algorithms
                (default: comprehensive image comparison settings)
        """
        return self.get('Image_compare', {
            'position_tolerance': 0,
            'tolerance': 0,
            'debug': True,
            'threshold': 0.8,
            'frame_threshold': 20,
            'rotation_start': -30,
            'rotation_end': 30,
            'rotation_step': 1,
            'match_algorithm': ["TM_CCOEFF_NORMED", "TM_CCORR_NORMED", "TM_SQDIFF_NORMED"],
            'distance_error': 0.1
        })
    
    def get_invalid_chars(self) -> str:
        """Get the invalid characters for file names.
        
        Returns:
            str: String of invalid characters (default: '<>:"/\\|?*')
        """
        return self.get('keyboard.invalid_chars', '<>:\"/\\|?*')
    
    def get_comment_screen_key(self) -> str:
        """Get the comment screen key.
        
        Returns:
            str: The comment screen key (default: 'f3')
        """
        return self.get('keyboard.comment_screen_key', 'f3')
    
    def get_Comment_Panel_config(self) -> tuple:
        """Get the Comment Panel configuration.
        
        Returns:
            tuple: Comment Panel configuration as (width, height, position)
                (default: (600, 200, {'x': 20, 'y': 20}))
        """
        width = self.get('Comment_Panel.CSW_width', 600)
        height = self.get('Comment_Panel.CSW_height', 200)
        position = self.get('Comment_Panel.CSW_position', {'x': 20, 'y': 20})
        return (width, height, position)

    def get_time_sleep(self) -> float:
        """Get the time sleep duration.
        
        Returns:
            float: Sleep duration in seconds (default: 0.2)
        """
        return self.get('time_sleep', 0.2)

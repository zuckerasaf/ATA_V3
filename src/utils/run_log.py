"""RunLog utility for collecting and managing log messages during test or recording runs.

This module provides a singleton RunLog class that collects log messages during test execution
and provides methods to retrieve summaries and save logs to a file. It ensures only one log
instance exists throughout the application.
"""

from datetime import datetime
from src.utils.config import Config

config = Config()
filepath = config.get_run_log_path()

class RunLog:
    """General-purpose log container for test/recording runs.
    
    This class implements a singleton pattern to ensure only one log instance exists
    throughout the application. It provides methods to add messages, retrieve summaries,
    and save logs to a file.
    
    Attributes:
        _instance: The singleton instance of the RunLog class
        entries: List of log entries with timestamps and levels
    """
    _instance = None  # Class variable for singleton pattern
    
    def __new__(cls):
        """Create or return the singleton instance.
        
        Returns:
            RunLog: The singleton instance of the RunLog class
        """
        if cls._instance is None:
            cls._instance = super(RunLog, cls).__new__(cls)
            cls._instance.entries = []
        return cls._instance
    
    def __init__(self):
        """Initialize the RunLog instance.
        
        Note:
            No initialization needed here since it's handled in __new__
        """
        # No need to initialize entries here since it's done in __new__
        pass

    def add(self, message, level="INFO"):
        """Add a message to the log.
        
        Args:
            message: The message to add to the log
            level: The log level (e.g., 'INFO', 'WARNING', 'ERROR') (default: "INFO")
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.entries.append(f"[{level}] {timestamp}: {message}")

    def get_summary(self):
        """Get the full log as a single string.
        
        Returns:
            str: The concatenated log entries, separated by newlines
        """
        return "\n".join(self.entries)

    def clear(self):
        """Clear all log entries.
        
        This method removes all entries from the log, effectively resetting it.
        """
        self.entries.clear()

    def save_to_file(self):
        """Save the log to a text file.
        
        This method appends the current log entries to the log file and then clears
        the entries to prevent duplication on subsequent saves.
        
        Note:
            If no entries exist, the method returns without saving anything.
        """
        if not self.entries:  # Don't save if no entries
            return
            
        with open(filepath, "a", encoding="utf-8") as f:
            f.write("\n")  # Add an empty line before the new log entry
            f.write(self.get_summary())
        
        # Clear entries after saving to prevent duplication
        self.entries.clear()

    def erase(self):
        """Erase the log file.
        
        This method clears the entire log file by writing an empty string to it.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("") 
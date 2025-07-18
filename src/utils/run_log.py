"""
RunLog utility for collecting and managing log messages during test or recording runs.

This class provides a simple interface to accumulate messages, retrieve summaries, and save logs to a file.
"""

from datetime import datetime
from src.utils.config import Config

config = Config()
filepath = config.get_run_log_path()

class RunLog:
    """
    General-purpose log container for test/recording runs.

    Methods
    -------
    add(message, level="INFO")
        Add a message to the log with an optional level.
    get_summary()
        Get the full log as a single string.
    clear()
        Clear all log entries.
    save_to_file(filepath)
        Save the log to a text file.
    """
    _instance = None  # Class variable for singleton pattern
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RunLog, cls).__new__(cls)
            cls._instance.entries = []
        return cls._instance
    
    def __init__(self):
        # No need to initialize entries here since it's done in __new__
        pass

    def add(self, message, level="INFO"):
        """
        Add a message to the log.

        Parameters
        ----------
        message : str
            The message to add.
        level : str, optional
            The log level (e.g., 'INFO', 'WARNING', 'ERROR'). Default is 'INFO'.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.entries.append(f"[{level}] {timestamp}: {message}")

    def get_summary(self):
        """
        Get the full log as a single string.

        Returns
        -------
        str
            The concatenated log entries, separated by newlines.
        """
        return "\n".join(self.entries)

    def clear(self):
        """
        Clear all log entries.
        """
        self.entries.clear()

    def save_to_file(self):
        """
        Save the log to a text file.

        Parameters
        ----------
        filepath : str
            The path to the file where the log should be saved.
        """
        if not self.entries:  # Don't save if no entries
            return
            
        with open(filepath, "a", encoding="utf-8") as f:
            f.write("\n")  # Add an empty line before the new log entry
            f.write(self.get_summary())
        
        # Clear entries after saving to prevent duplication
        self.entries.clear()

    def erase(self):
        """
        Erase the log file.

        Parameters
        ----------
        filepath : str
            The path to the file where the log should be saved.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("") 
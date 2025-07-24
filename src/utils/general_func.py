"""General utility functions for test automation.

This module provides helper functions for test data management, file operations,
string manipulation, and image handling for test automation workflows.

The module includes functions for:
- Random word generation for test names
- Test data loading and display from JSON files
- Image file management and copying
- String manipulation utilities
- Test object creation and serialization
"""

import json
import os
import sys
import random
import string
import numpy as np
import wave
import tempfile
import shutil


# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from src.utils.test import Test
from src.utils.event_mouse_keyboard import Event
from src.utils.config import Config
from src.utils.run_log import RunLog

run_log = RunLog()


def generate_random_word():
    """Generate a random 5-letter word.
    
    Returns:
        str: A random 5-letter lowercase word
        
    Example:
        >>> generate_random_word()
        'abcde'
    """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(5))

def display_test_data(file_path):
    """Display a summary of test data from a JSON file.
    
    Loads a test from JSON and extracts step names and results for display
    in the GUI. Handles cases where the file is missing or invalid.
    
    Args:
        file_path: Path to the test JSON file
        
    Returns:
        list: A list of [step name, result] pairs summarizing the test steps.
            Returns [["Name1", ""]] if no data is available.
            
    Raises:
        FileNotFoundError: If the test file doesn't exist (handled internally)
        json.JSONDecodeError: If the JSON file is invalid (handled internally)
    """
    test_summary = []
    test = create_test_from_json(file_path)
    
    if test is None:
        return [["Name1", ""]]
        
    try:
        num_of_events = len(test.stepResult)
        if num_of_events == 0:
            test_summary.append(["Name1", ""])
        else:
            for i in range(num_of_events):
                test_summary.append([test.stepResult[i][0], test.stepResult[i][1]])
    except:
        test_summary.append(["Name1", ""])
    return test_summary


def create_test_from_json(filepath):
    """Create a Test instance from a JSON file.
    
    Loads test configuration, events, and results from a JSON file and
    creates a Test object with all the data. Handles various error conditions
    gracefully and logs errors to the run log.
    
    Args:
        filepath: Path to the test JSON file
        
    Returns:
        Test or None: The Test object if loaded successfully, otherwise None
        
    Raises:
        FileNotFoundError: If the test file doesn't exist (handled internally)
        json.JSONDecodeError: If the JSON file is invalid (handled internally)
        Exception: For other errors during loading (handled internally)
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        # Create Test instance with data from JSON
        test = Test(
            config=data.get('config', ''),
            comment1=data.get('comment1', ''),
            comment2=data.get('comment2', ''),
            accuracy_level=data.get('accuracy_level', '5'),
            starting_point=data.get('starting_point', ''),
            numOfSteps=data.get('numOfSteps', 0),
            stepResult=data.get('stepResult', [])   
        )
        
        # Add events from JSON
        for event_data in data.get('events', []):
            # Convert dictionary to Event object using from_dict
            event = Event.from_dict(event_data)
            test.add_event(event)
            
        return test
        
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        run_log.add(f"Error: File not found at {filepath}", level="ERROR")
        run_log.save_to_file()
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {filepath}")  
        run_log.add(f"Error: Invalid JSON format in {filepath}", level="ERROR") 
        run_log.save_to_file()
        return None
    except Exception as e:
        print(f"Error loading test data: {e}")
        run_log.add(f"Error loading test data: {e}", level="ERROR")
        run_log.save_to_file()
        return None
    
def update_images_to_test(result_folder_path):
    """Copy all _Result.jpg images from a result folder to the corresponding test folder.
    
    This function copies screenshot images from test results back to the test folder
    for future reference. It renames the files by removing the "_Result" suffix.
    
    Args:
        result_folder_path: Path to the result folder (e.g., 'DB/Result/20250517_224058_paint')
        
    Returns:
        bool: True if images were copied successfully, False otherwise
        
    Raises:
        Exception: For file system errors (handled internally)
        
    Note:
        The function expects result folder names in the format:
        YYYYMMDD_HHMMSS_testname
    """
    try:
        # Get the result folder name
        result_folder_name = os.path.basename(result_folder_path)
        
        # Extract test name by removing timestamp (format: YYYYMMDD_HHMMSS_testname)
        parts = result_folder_name.split('_')
        if len(parts) >= 3:
            test_name = '_'.join(parts[2:])  # Join remaining parts in case test name contains underscores
        else:
            print(f"Invalid result folder name format: {result_folder_name}")
            return False
            
        # Get paths from config
        config = Config()
        paths_config = config.get('paths', {})
        db_path = paths_config.get('db_path', os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "DB"))
        test_path = paths_config.get('test_path', "Test")
        
        # Construct test folder path
        test_folder_path = os.path.join(db_path, test_path, test_name)
        
        # # Create test folder if it doesn't exist
        # os.makedirs(test_folder_path, exist_ok=True)
        
        # Find all _Result.jpg files
        result_files = [f for f in os.listdir(result_folder_path) if f.endswith('_Result.jpg')]
        
        if not result_files:
            print(f"No _Result.jpg files found in {result_folder_path}")
            return False
            
        # Copy and rename files
        copied_files = []
        for file in result_files:
            # Create new filename by removing _Result
            new_filename = file.replace('_Result.jpg', '.jpg')
            src_file = os.path.join(result_folder_path, file)
            dst_file = os.path.join(test_folder_path, new_filename)
            shutil.copy2(src_file, dst_file)
            copied_files.append(new_filename)
                
        if copied_files:
            print(f"Successfully copied {len(copied_files)} images to {test_folder_path}")
            print("Copied files:", copied_files)
            return True
        else:
            print(f"No _Result.jpg files found in {result_folder_path}")
            return False
            
    except Exception as e:
        print(f"Error copying images: {e}")
        return False
    
def replace_last_part_of_string(original_string, old_suffix, new_suffix):
    """Replace the last occurrence of a suffix in a string with a new suffix.
    
    This function finds the last occurrence of old_suffix in the string and
    inserts new_suffix before it. If the string doesn't end with old_suffix,
    the original string is returned unchanged.
    
    Args:
        original_string: The original string to modify
        old_suffix: The suffix to find and replace
        new_suffix: The new suffix to insert before the old suffix
    
    Returns:
        str: The modified string with the new suffix inserted before the old suffix
        
    Example:
        >>> replace_last_part_of_string(
        ...     'C:\\path\\file_Result.jpg', 
        ...     '_Result.jpg', 
        ...     '_Match'
        ... )
        'C:\\path\\file_Match_Result.jpg'
    """
    if original_string.endswith(old_suffix):
        # Remove the old suffix and add the new suffix + old suffix
        base = original_string[:-len(old_suffix)]
        return base + new_suffix + old_suffix
    else:
        # If the string doesn't end with the expected suffix, return original
        return original_string

def insert_match_before_result(file_path):
    """Insert "_Match" before "_Result" in a file path.
    
    This is a convenience function specifically for the common case of
    inserting "_Match" before "_Result.jpg" in image file paths. It's used
    for creating template image paths from result image paths.
    
    Args:
        file_path: The file path to modify
        
    Returns:
        str: The modified file path with "_Match" inserted before "_Result"
        
    Example:
        >>> insert_match_before_result(
        ...     'C:\\path\\image_Result.jpg'
        ... )
        'C:\\path\\image_Match_Result.jpg'
    """
    return replace_last_part_of_string(file_path, '_Result.jpg', '_Match')
    
    

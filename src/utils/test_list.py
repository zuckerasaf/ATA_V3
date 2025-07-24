"""Test list management utilities.

This module provides the TeslList class for managing collections of tests.
It supports adding tests, serialization to/from dictionaries, and metadata
tracking for test suites.
"""

from typing import List
from datetime import datetime
from src.utils.test import Test

class TeslList:
    """Container for managing a collection of tests.
    
    This class represents a test suite or batch of tests that can be executed
    together. It tracks metadata about the test collection including timing,
    comments, and execution delays.
    
    Attributes:
        tests: List of Test objects in the collection
        timestamp: When the test list was created
        comment: Optional comment describing the test collection
        numOfTest: Number of tests in the collection
        delay: Delay between test executions in milliseconds
    """
    def __init__(self, tests: List[Test], timestamp: str = None, comment: str = "", numOfTest: int = 0, delay: int = 0):
        """Initialize a new test list.
        
        Args:
            tests: List of Test objects to include in the collection
            timestamp: Creation timestamp (default: current time)
            comment: Comment describing the test collection (default: "")
            numOfTest: Number of tests (default: 0, auto-calculated from tests list)
            delay: Delay between test executions in milliseconds (default: 0)
        """
        self.tests = tests  # List[Test]
        self.timestamp = timestamp if timestamp else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.comment = comment  # string
        self.numOfTest = numOfTest  # integer
        self.delay = delay  # integer (ms or s, depending on your use case)

    def add_test(self, test: Test):
        """Add a test to the collection.
        
        Args:
            test: Test object to add to the collection
            
        Note:
            This method automatically updates the numOfTest count.
        """
        self.tests.append(test)
        self.numOfTest = len(self.tests)

    def to_dict(self):
        """Convert the test list to a dictionary format.
        
        Returns:
            dict: Dictionary representation of the test list with all tests serialized
        """
        return {
            'tests': [t.to_dict() for t in self.tests],
            'timestamp': self.timestamp,
            'comment': self.comment,
            'numOfTest': self.numOfTest,
            'delay': self.delay
        }

    @classmethod
    def from_dict(cls, data):
        """Create a TeslList instance from a dictionary.
        
        Args:
            data: Dictionary containing test list data
            
        Returns:
            TeslList: New TeslList instance with data from the dictionary
        """
        tests = [Test.from_dict(t) for t in data.get('tests', [])]
        return cls(
            tests=tests,
            timestamp=data.get('timestamp', None),
            comment=data.get('comment', ""),
            numOfTest=data.get('numOfTest', len(tests)),
            delay=data.get('delay', 0)
        ) 
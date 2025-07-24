"""Event class for storing mouse and keyboard events.

This module defines the Event class which represents individual mouse and keyboard
events captured during test recording. Each event contains comprehensive information
about the action, timing, position, and associated screenshots or templates.
"""

from PIL import Image

class Event:
    """Represents a single mouse or keyboard event in the automation testing system.
    
    This class stores all information related to a user interaction event, including
    timing, position, action details, priority, and associated images. It supports
    serialization to/from dictionaries for storage and transmission.
    
    Attributes:
        PRIORITY_HIGH (str): High priority constant
        PRIORITY_MEDIUM (str): Medium priority constant (default)
        PRIORITY_LOW (str): Low priority constant
        
    Note:
        The Event class is designed to be comprehensive and capture all necessary
        information for replaying user interactions during test execution.
    """
    # Priority levels
    PRIORITY_HIGH = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW = "low"
    
    def __init__(self, counter: int, time: int, position: tuple, event_type: str, 
                 action: str, neto_time: int = 0, priority: str = PRIORITY_MEDIUM, step_on: str = "",
                 time_from_last: int = 0, time_in_screenshot_dialog: int = 0, step_desc: str = "none", 
                 step_accep: str = "none", step_resau: str = "none", step_resau_num: int = 0,
                 pic_path: str = "noPic", screenshot_counter: int = 0, image_name: str = "noPic",
                 pic_width: int = 0, pic_height: int = 0, pic_x: int = 0, pic_y: int = 0,
                 pic_template_path: str = "noTemplatePic", pic_template_name: str = "noTemplatePic",
                 pic_template_width: int = 1, pic_template_height: int = 1, pic_template_x: int = 1, pic_template_y: int = 1,
                 pic_rotation_start: int = 0, pic_rotation_end: int = 0, pic_rotation_state: bool = False,
                 pic_template_loc_x: int = 0, pic_template_loc_y: int = 0, pic_template_confidence: float = 0):
        """Initialize a new Event instance.
        
        Args:
            counter: Event counter/sequence number
            time: Time since last event in milliseconds
            position: Mouse position as (x, y) tuple
            event_type: Type of event (e.g., "mouse_left", "keyboard")
            action: Description of the action performed
            neto_time: Net time since last event in milliseconds
            priority: Event priority level (high/medium/low)
            step_on: Step number or identifier
            time_from_last: Time from last event in milliseconds
            time_in_screenshot_dialog: Time spent in screenshot dialog in milliseconds
            step_desc: Description of what this step does
            step_accep: Expected outcome of the step
            step_resau: Actual result of the step
            step_resau_num: Numeric result value
            pic_path: Path to associated screenshot image
            screenshot_counter: Counter for screenshots
            image_name: Name of the image file
            pic_width: Width of the screenshot in pixels
            pic_height: Height of the screenshot in pixels
            pic_x: X coordinate of the screenshot region
            pic_y: Y coordinate of the screenshot region
            pic_template_path: Path to the template image
            pic_template_name: Name of the template image
            pic_template_width: Width of the template in pixels
            pic_template_height: Height of the template in pixels
            pic_template_x: X coordinate of the template region
            pic_template_y: Y coordinate of the template region
            pic_rotation_start: Starting rotation angle for image matching
            pic_rotation_end: Ending rotation angle for image matching
            pic_rotation_state: Whether rotation matching is enabled
            pic_template_loc_x: X coordinate of template match location
            pic_template_loc_y: Y coordinate of template match location
            pic_template_confidence: Confidence score of template match (0.0-1.0)
        """
        self.counter = counter
        self.time = time
        self.neto_time = neto_time
        self.position = position
        self.event_type = event_type
        self.action = action
        self.priority = priority
        self.step_on = step_on
        self.time_from_last = time_from_last
        self.time_in_screenshot_dialog = time_in_screenshot_dialog
        self.step_desc = step_desc
        self.step_accep = step_accep
        self.step_resau = step_resau
        self.step_resau_num = step_resau_num
        self.pic_path = pic_path
        self.screenshot_counter = screenshot_counter
        self.image_name = image_name
        self.pic_width = pic_width
        self.pic_height = pic_height
        self.pic_x = pic_x
        self.pic_y = pic_y
        self.pic_template_path = pic_template_path
        self.pic_template_name = pic_template_name
        self.pic_template_width = pic_template_width
        self.pic_template_height = pic_template_height
        self.pic_template_x = pic_template_x
        self.pic_template_y = pic_template_y
        self.pic_rotation_start = pic_rotation_start
        self.pic_rotation_end = pic_rotation_end
        self.pic_rotation_state = pic_rotation_state
        self.pic_template_loc_x = pic_template_loc_x
        self.pic_template_loc_y = pic_template_loc_y
        self.pic_template_confidence = pic_template_confidence
        self.screenshot = None  # Store the screenshot image


    def __str__(self) -> str:
        """Get string representation of the Event.
        
        Returns:
            str: Human-readable string representation of the event
        """
        return f"Event(counter={self.counter}, time={self.time}, neto_time={self.neto_time}, position={self.position}, " \
               f"type='{self.event_type}', action='{self.action}', priority={self.priority}, " \
               f"step_on='{self.step_on}', time_from_last={self.time_from_last}, " \
               f"time_in_screenshot_dialog={self.time_in_screenshot_dialog}, " \
               f"step_desc='{self.step_desc}', step_accep='{self.step_accep}', " \
               f"step_resau='{self.step_resau}', pic_path='{self.pic_path}', " \
               f"screenshot_counter={self.screenshot_counter}, image_name='{self.image_name}', " \
               f"pic_width={self.pic_width}, pic_height={self.pic_height}, " \
               f"pic_x={self.pic_x}, pic_y={self.pic_y}, pic_template_path='{self.pic_template_path}', " \
               f"pic_template_name='{self.pic_template_name}', pic_template_width={self.pic_template_width}, " \
               f"pic_template_height={self.pic_template_height}, pic_template_x={self.pic_template_x}, " \
               f"pic_template_y={self.pic_template_y}, pic_rotation_start={self.pic_rotation_start}, " \
               f"pic_rotation_end={self.pic_rotation_end}, pic_rotation_state={self.pic_rotation_state}, " \
               f"pic_template_loc_x={self.pic_template_loc_x}, pic_template_loc_y={self.pic_template_loc_y}, " \
               f"pic_template_confidence={self.pic_template_confidence})"
    
    
    def __repr__(self) -> str:
        """Get detailed string representation of the Event.
        
        Returns:
            str: Detailed string representation for debugging
        """
        return self.__str__()
    
    def to_dict(self) -> dict:
        """Convert event to dictionary format for serialization.
        
        Returns:
            dict: Dictionary representation of the event with all attributes
        """
        return {
            'counter': self.counter,
            'time': self.time,
            'neto_time': self.neto_time,
            'position': self.position,
            'type': self.event_type,
            'action': self.action,
            'priority': self.priority,
            'step_on': self.step_on,
            'time_from_last': self.time_from_last,
            'time_in_screenshot_dialog': self.time_in_screenshot_dialog,
            'step_desc': self.step_desc,
            'step_accep': self.step_accep,
            'step_resau': self.step_resau,
            'step_resau_num': self.step_resau_num,
            'pic_path': self.pic_path,
            'screenshot_counter': self.screenshot_counter,
            'image_name': self.image_name,
            'pic_width': self.pic_width,
            'pic_height': self.pic_height,
            'pic_x': self.pic_x,
            'pic_y': self.pic_y,
            'pic_template_path': self.pic_template_path,
            'pic_template_name': self.pic_template_name,
            'pic_template_width': self.pic_template_width,
            'pic_template_height': self.pic_template_height,
            'pic_template_x': self.pic_template_x,
            'pic_template_y': self.pic_template_y,
            'pic_rotation_start': self.pic_rotation_start,
            'pic_rotation_end': self.pic_rotation_end,
            'pic_rotation_state': self.pic_rotation_state,
            'pic_template_loc_x': self.pic_template_loc_x,
            'pic_template_loc_y': self.pic_template_loc_y,
            'pic_template_confidence': self.pic_template_confidence
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        """Create an Event instance from a dictionary.
        
        Args:
            data: Dictionary containing event data
            
        Returns:
            Event: New Event instance created from the dictionary data
            
        Note:
            This method handles missing keys gracefully by providing default values.
        """
        return cls(
            counter=data['counter'],
            time=data['time'],
            neto_time=data['neto_time'],
            position=data['position'],
            event_type=data['type'],
            action=data['action'],
            priority=data['priority'],
            step_on=data['step_on'],
            time_from_last=data['time_from_last'],
            time_in_screenshot_dialog=data['time_in_screenshot_dialog'],
            step_desc=data['step_desc'],
            step_accep=data['step_accep'],
            step_resau=data.get('step_resau', 'none'),
            step_resau_num=data.get('step_resau_num', 0),
            pic_path=data.get('pic_path', 'none'),
            screenshot_counter=data.get('screenshot_counter', 0),
            image_name=data.get('image_name', 'none'),
            pic_width=data.get('pic_width', 0),
            pic_height=data.get('pic_height', 0),
            pic_x=data.get('pic_x', 0),
            pic_y=data.get('pic_y', 0),
            pic_template_path=data.get('pic_template_path', 'none'),
            pic_template_name=data.get('pic_template_name', 'none'),
            pic_template_width=data.get('pic_template_width', 0),
            pic_template_height=data.get('pic_template_height', 0),
            pic_template_x=data.get('pic_template_x', 0),
            pic_template_y=data.get('pic_template_y', 0),
            pic_rotation_start=data.get('pic_rotation_start', 0),
            pic_rotation_end=data.get('pic_rotation_end', 0),
            pic_rotation_state=data.get('pic_rotation_state', False),
            pic_template_loc_x=data.get('pic_template_loc_x', 0),
            pic_template_loc_y=data.get('pic_template_loc_y', 0),
            pic_template_confidence=data.get('pic_template_confidence', 0)
        )
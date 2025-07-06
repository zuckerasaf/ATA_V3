"""
Utility module for handling pictures and screenshots in the ATA testing framework.

This module provides functionality for:
- Capturing screenshots of specific screen regions
- Generating and managing screenshot filenames
- Comparing images with tolerance and position matching
- Finding image offsets and matches
- Saving screenshots to disk

The module uses OpenCV for image processing and PIL for screenshot capture.
"""

import os
from PIL import ImageGrab, Image
import cv2
import numpy as np
from src.utils.config import Config
from datetime import datetime

config = Config()

# Define project root path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

def capture_screen(x, y, width, height):
    """
    Capture a screenshot of a specific region of the screen.
    
    This function captures a rectangular region of the screen based on the provided
    coordinates and dimensions. It uses PIL's ImageGrab for the actual capture.
    
    Args:
        x (int): X-coordinate of the top-left corner
        y (int): Y-coordinate of the top-left corner
        width (int): Width of the capture region
        height (int): Height of the capture region
    
    Returns:
        PIL.Image: The captured screenshot, or None if capture fails
    """
    try:
        # Capture the screen with configured dimensions and position
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        
        return screenshot
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return None

def generate_screenshot_filename(test_name, counter, image_name, state, result_folder_path):
    """
    Generate a filename for a screenshot based on test context and state.
    
    This function creates appropriate filenames for screenshots based on whether
    they are being taken during test recording or result comparison. It handles
    both test and result directory structures.
    
    Args:
        test_name (str): Name of the test
        counter (int): Screenshot counter number
        image_name (str): Name to use for the image
        state (str): Current state ("Recording" or "Result")
        result_folder_path (str): Path to the result folder when in result state
        
    Returns:
        tuple: (filename, full_path) or (None, None) if generation fails
    """
    try:
        if not test_name:
            print("No test name provided to generate screenshot filename")
            return None, None
            
        # Get paths from config
        paths_config = config.get('paths', {})
        db_path = paths_config.get('db_path', os.path.join(project_root, "DB")) 
        if state == "Recording":
            test_path = paths_config.get('test_path', "Test")
            # Create full path in test directory
            test_dir = os.path.join(db_path, test_path, test_name)
            # Generate screenshot filename
            screenshot_filename = f"{test_name}_{image_name}.jpg"
        else:
            # Generate screenshot filename and path in result folder
            test_dir = result_folder_path
            screenshot_filename = f"{image_name.split('.')[0]}_Result.jpg"   

        screenshot_path = os.path.join(test_dir, screenshot_filename)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        
        return screenshot_filename, screenshot_path
    except Exception as e:
        print(f"Error generating screenshot filename: {e}")
        return None, None

def debug_print(debug, debug_log, *args, **kwargs):
    """Helper function to print to both console and debug log"""
    print(*args, **kwargs)
    if debug and debug_log:
        debug_log.write(" ".join(str(arg) for arg in args) + "\n")

def compare_images(source, target, result_folder):
    """
    Compare two images and generate a visual difference map with detailed analysis.
    
    This function performs a comprehensive comparison between source and target images:
    1. Position Matching:
       - Uses template matching to find the target image within the source
       - Applies configurable position tolerance
       - Trims images to matched regions for accurate comparison
    
    2. Pixel Analysis:
       - Converts images to grayscale for comparison
       - Calculates absolute difference between images
       - Applies threshold to identify significant differences
       - Generates difference visualization
    
    3. Debug Features (when enabled):
       - Saves intermediate images (grayscale, difference, threshold)
       - Creates detailed debug log with pixel statistics
       - Generates visual difference map
       - Provides percentage match calculation
    
    Args:
        source (str): Path to the source (reference) image
        target (str): Path to the target (test) image to compare against source
        result_folder (str): Directory to save comparison results and debug outputs
        
    Returns:
        tuple: (match_percentage, result_image_path)
            - match_percentage (int): Percentage of matching pixels (0-100)
            - result_image_path (str): Path to the generated difference visualization
    """
    config = Config()
    image_compare_config = config.get('Image_compare', {})
    tolerance = image_compare_config.get('tolerance', 0.95)
    position_tolerance = image_compare_config.get('position_tolerance', 10)
    debug = image_compare_config.get('debug', True)
    source_name = os.path.basename(source).split(".")[0]
    target_name = os.path.basename(target).split(".")[0]

    # Initialize debug logging if debug mode is enabled
    debug_log = None
    if debug:
        debug_log_path = os.path.join(result_folder, f"{target_name}_debug_log.txt")
        debug_log = open(debug_log_path, 'a', encoding='utf-8')
        # Write header with timestamp
        debug_print(True,debug_log,f"\n Debug Log for {target_name}\n")
        debug_print(True,debug_log,f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        debug_print(True,debug_log,"="*50 + "\n\n")



    try:
        # Read images
        source_img = cv2.imread(source)
        target_img = cv2.imread(target)
        
        if source_img is None or target_img is None:
            print("Error: Could not read one or both images")
            return 0, None
        
        # Ensure both images are the same size
        if source_img.shape != target_img.shape:
            target_img = cv2.resize(target_img, (source_img.shape[1], source_img.shape[0]))
        
        # Convert images to grayscale
        source_gray = cv2.cvtColor(source_img, cv2.COLOR_BGR2GRAY)
        target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)

        # Save grayscale images for debugging if requested
        if debug:
            # Save source grayscale image
            source_gray_path = os.path.join(result_folder, source_name+"_gray.jpg")
            cv2.imwrite(source_gray_path, source_gray)
            print(f"Saved source grayscale image to: {source_gray_path}")
            
            # Save target grayscale image
            target_gray_path = os.path.join(result_folder, target_name+"_gray.jpg")
            cv2.imwrite(target_gray_path, target_gray)
            print(f"Saved target grayscale image to: {target_gray_path}")

        
        found, offset_x, offset_y, w, h, match_confidence, matched_region = find_image_offset(source_gray, target_gray, result_folder, debug, target_name)
        
        if found:
            #cut the source image to the size of the matched region 
            source_gray = source_gray[offset_y:offset_y+h, offset_x:offset_x+w]
            #cut the target image to the size of config.get_Image_compare_config().get('frame_threshold')
            cut_threshold = config.get_Image_compare_config().get('frame_threshold')
            target_gray = target_gray[cut_threshold:cut_threshold+h, cut_threshold:cut_threshold+w]
            
        if debug:
            # present the trimed source and trimed  grayscale image
            source_trimed_path = os.path.join(result_folder, target_name +"_trimmed_source.jpg")
            cv2.imwrite(source_trimed_path, source_gray)
            print(f"Saved matched region to: {source_trimed_path}")
                
            target_trimmed_path = os.path.join(result_folder, target_name +"_trimmed_target.jpg")
            cv2.imwrite(target_trimmed_path, target_gray)
            print(f"Saved trimmed target to: {target_trimmed_path}")
        
        # Calculate absolute difference
        diff = cv2.absdiff(source_gray, target_gray)
        
        # Save difference image for debugging if requested
        if debug:
            # Calculate and log pixel statistics
            total_pixels = diff.shape[0] * diff.shape[1]
            non_zero_pixels = cv2.countNonZero(diff)
            debug_print(debug,debug_log,f"Total pixels in image: {total_pixels} in {target_name}")
            debug_print(debug,debug_log,f"According to Diff Number of non-zero pixels (differences) between {target_name} and {source_name}: {non_zero_pixels}")
            debug_print(debug,debug_log,f"Percentage of different pixels: {(non_zero_pixels/total_pixels)*100:.2f}%")
            print(f"Total pixels in image: {total_pixels} in {target_name}")
            print(f" According to Diff Number of non-zero pixels (differences) between {target_name} and {source_name}: {non_zero_pixels}")
            print(f"Thresh Percentage of different pixels: {(non_zero_pixels/total_pixels)*100:.2f}%")
            diff_path = os.path.join(result_folder,target_name+"_diff.jpg")
            cv2.imwrite(diff_path, diff)
            print(f"Saved difference image to: {diff_path}")
        
        tolerance = config.get('Image_compare', {}).get('tolerance', 10)
        _, thresh = cv2.threshold(diff, tolerance, 255, cv2.THRESH_BINARY)
        
        # Save threshold image for debugging if requested
        if debug:
            thresh_path = os.path.join(result_folder, target_name+"_thresh.jpg")
            non_zero_pixels = cv2.countNonZero(thresh)
            debug_print(debug,debug_log,f"according to Thresh Number of non-zero pixels (differences) with {tolerance}: {non_zero_pixels}")
            debug_print(debug,debug_log,f"Thresh Percentage of different pixels: {(non_zero_pixels/total_pixels)*100:.2f}% ")
            print(f"according to Thresh Number of non-zero pixels (differences) with {tolerance}: {non_zero_pixels}")
            print(f"Percentage of different pixels: {(non_zero_pixels/total_pixels)*100:.2f}%")
            cv2.imwrite(thresh_path, thresh)
            print(f"Saved threshold image to: {thresh_path}")
        
        # # Find contours of differences
        # contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # # Create a mask for differences
        # mask = np.zeros_like(source_gray)
        # cv2.drawContours(mask, contours, -1, (0, 0, 255), -1)  # Red color for differences
        
        # # Create result image (only showing differences)
        # result = cv2.bitwise_and(source_gray, mask)
        
        # Calculate match percentage
        total_pixels = source_gray.size
        diff_pixels = cv2.countNonZero(thresh)
        match_percentage = ((total_pixels - diff_pixels) / total_pixels) * 100
        debug_print(debug,debug_log,f"Match percentage: {match_percentage}")
        
        # Generate result filename
        result_dif_filename = target_name+"_diffrence.jpg"
        result_dif_path = os.path.join(result_folder, result_dif_filename)
        
        # Save result image
        cv2.imwrite(result_dif_path, thresh)
        
        return int(match_percentage), result_dif_path
        
    except Exception as e:
        print(f"Error comparing images: {e}")
        return 0, None
    finally:
        # Close debug log file if it was opened
        if debug_log:
            debug_log.close()

def find_image_offset(source_gray, target_gray, result_folder=None, debug=False, target_name=None):
    """
    Find if target image exists within source image and calculate its offset.
    
    This function uses template matching to find if the target image exists within
    the source image, accounting for potential position differences. It includes:
    - Edge trimming to improve matching
    - Confidence scoring
    - Debug visualization
    - Position offset calculation
    - Extraction of matching region from source image
    
    Args:
        source_gray (numpy.ndarray): Grayscale source image
        target_gray (numpy.ndarray): Grayscale target image to find
        result_folder (str, optional): Folder to save debug visualization
        debug (bool): If True, saves visualization of the match
        target_name (str, optional): Name of the target image for debug files
        
    Returns:
        tuple: (found, offset_x, offset_y, match_confidence, matched_region)
            - found (bool): True if target was found in source
            - offset_x (int): X coordinate of the match
            - offset_y (int): Y coordinate of the match
            - match_confidence (float): Confidence of the match (0-1)
            - matched_region (numpy.ndarray): The region from source image that matches the trimmed target
    """
    debug_log_path = os.path.join(result_folder, f"{target_name}_debug_log.txt")
    debug_log = open(debug_log_path, 'a', encoding='utf-8')

    try:
        # Trim 10 pixels from each edge of the target image
        h, w = target_gray.shape
        frame_threshold = config.get_Image_compare_config().get('frame_threshold')
        if h > frame_threshold *2 and w > frame_threshold *2:  # Only trim if image is large enough
            target_gray = target_gray[frame_threshold:h-frame_threshold, frame_threshold:w-frame_threshold]
            print(f"Trimmed target image to shape: {target_gray.shape}")
        
        # Perform template matching
        result = cv2.matchTemplate(source_gray, target_gray, cv2.TM_CCOEFF_NORMED)
        
        # Get the best match location
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Print detailed matching information
        print("\nTemplate Matching Results:")
        print(f"Max Value (Best Match Confidence): {max_val:.4f}")
        print(f"Max Location (Best Match Position): {max_loc}")
        print(f"Min Value (Worst Match): {min_val:.4f}")
        print(f"Min Location (Worst Match Position): {min_loc}")
        print(f"Result Matrix Shape: {result.shape}")
        print(f"Result Matrix Type: {result.dtype}")
        print(f"Result Matrix Range: [{result.min():.4f}, {result.max():.4f}]")
        debug_print(debug,debug_log,f"Template Matching Results:")
        debug_print(debug,debug_log,f"Max Value (Best Match Confidence): {max_val:.4f}")
        debug_print(debug,debug_log,f"Max Location (Best Match Position): {max_loc}")
        debug_print(debug,debug_log,f"Min Value (Worst Match): {min_val:.4f}")
        debug_print(debug,debug_log,f"Min Location (Worst Match Position): {min_loc}")
        debug_print(debug,debug_log,f"Result Matrix Shape: {result.shape}")
        debug_print(debug,debug_log,f"Result Matrix Type: {result.dtype}")
        debug_print(debug,debug_log,f"Result Matrix Range: [{result.min():.4f}, {result.max():.4f}]")
        # Get dimensions of trimmed target
        h, w = target_gray.shape
        
        # Calculate match confidence
        match_confidence = max_val
        
        # Define threshold for considering it a match (adjust as needed)
        threshold = config.get('Image_compare', {}).get('threshold', 0.8)
        debug = config.get('Image_compare', {}).get('debug', True)
        
        if match_confidence >= threshold:
            # Get the offset coordinates (add 10 to account for the trimming)
            offset_x, offset_y = max_loc[0] , max_loc[1] 
            
            # Extract the matching region from source image
            matched_region = source_gray[max_loc[1]:max_loc[1] + h, max_loc[0]:max_loc[0] + w]
            
            print("\nMatch Found!")
            print(f"Offset X: {offset_x}")
            print(f"Offset Y: {offset_y}")
            print(f"Match Confidence: {match_confidence:.4f}")
            print(f"Threshold: {threshold}")
            print(f"Matched Region Shape: {matched_region.shape}")
            
            if debug and result_folder:
                # Create a visualization
                debug_img = source_gray.copy()
                # Draw rectangle around the match (add 10 to account for the trimming)
                cv2.rectangle(debug_img, 
                            (max_loc[0] , max_loc[1]), 
                            (max_loc[0] + w , max_loc[1] + h ), 
                            (0, 255, 0), 2)
                # Add text showing offset and confidence
                text = f"Offset: ({offset_x}, {offset_y}), Confidence: {match_confidence:.2f}"
                cv2.putText(debug_img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Save debug visualization
                offset_debug_path = os.path.join(result_folder, target_name +"_offest_in_source.jpg")
                cv2.imwrite(offset_debug_path, debug_img)
                print(f"Saved match visualization to: {offset_debug_path}")
                
                # # Save the matched region
                # source_triimed_path = os.path.join(result_folder, target_name +"_trimmed_source.jpg")
                # cv2.imwrite(source_triimed_path, matched_region)
                # print(f"Saved matched region to: {source_triimed_path}")
                
                # # Save the trimmed target for comparison
                # target_trimmed_path = os.path.join(result_folder, target_name +"_trimmed_target.jpg")
                # cv2.imwrite(target_trimmed_path, target_gray)
                # print(f"Saved trimmed target to: {target_trimmed_path}")
            
            return True, offset_x, offset_y, w, h, match_confidence, matched_region
            
        else:
            print("\nNo Match Found!")
            print(f"Best Match Confidence: {match_confidence:.4f}")
            print(f"Required Threshold: {threshold}")
            return False, 0, 0, 0, 0, match_confidence, None
            debug_print(debug,debug_log,f"No Match Found!")
            debug_print(debug,debug_log,f"Best Match Confidence: {match_confidence:.4f}")
            debug_print(debug,debug_log,f"Required Threshold: {threshold}") 
            
    except Exception as e:
        print(f"Error finding image offset: {e}")
        return False, 0, 0, 0, 0, 0.0, None

def save_screenshot(screenshot, filepath: str) -> None:
    """
    Save a screenshot to disk.
    
    This function saves a PIL Image object to the specified filepath in JPEG format.
    
    Args:
        screenshot (PIL.Image): The screenshot to save
        filepath (str): The path where the screenshot should be saved
        
    Returns:
        str: The filepath where the screenshot was saved, or None if save fails
    """
    if screenshot:
        screenshot.save(filepath, 'JPEG')
        return filepath  # Update the pic_path field with the saved file path
    
def find_image(template_path, image_path, threshold=0.8, method=cv2.TM_CCOEFF_NORMED, rotation_start=0, rotation_end=0, rotation_step=0):
    """
    Find a template image within a larger image.
    
    Args:
        template_path (str): Path to the template image
        image_path (str): Path to the larger image
        threshold (float): Matching threshold (0-1)
        method: OpenCV template matching method
    
    Returns:
        tuple: (success, result_image, matches, confidences, locations)
    """

    try:
    # Read the images
        template = cv2.imread(template_path)
        image = cv2.imread(image_path)

        points, confidences_lowR, best_angle_lowR, best_confidence_lowR, results_low_res = find_image_multiscale(image, template, threshold, method, rotation_start, rotation_end, rotation_step)

        # cv2.imshow("template_low_res", template_low_res)
        # cv2.imshow("image_low_res", image_low_res)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        if template is None or image is None:
            print("Error: Could not read one or both images")
            return False, None, [], [], []
        
        # If no points found from low-res search, return failure
        if not points:
            print("No matches found in low-resolution search")
            return False, None, [], [], []
        
        h, w = template.shape[:2]
        
        # Convert low-res points to high-res coordinates (multiply by 2)
        high_res_points = [(x * 2, y * 2) for (x, y) in points]
        
        # Rotate template for the best angle found
        rotated_template = rotate_image(template, best_angle_lowR)
        rotated_h, rotated_w = rotated_template.shape[:2]
        
        # Define search region size (template size + some margin)
        margin = 20  # pixels margin around the low-res point
        search_h = rotated_h + 2 * margin
        search_w = rotated_w + 2 * margin
        
        best_high_res_confidence = -1
        best_high_res_location = None
        all_high_res_results = []
        
        print(f"Running high-resolution search on {len(high_res_points)} regions...")
        
        print(f"Points: {points}")
        points_cleaned = remove_duplicate_points(points)
        print(f"Points cleaned: {points_cleaned}")
        # For each low-res point, search in the corresponding high-res region
        for i, (low_x, low_y) in enumerate(points_cleaned):
            
            # Convert to high-res coordinates
            high_x, high_y = low_x * 2, low_y * 2
            
            # Define search region bounds
            start_x = max(0, high_x - margin)
            start_y = max(0, high_y - margin)
            end_x = min(image.shape[1] - rotated_w, high_x + margin)
            end_y = min(image.shape[0] - rotated_h, high_y + margin)
            
            # Extract the search region
            search_region = image[start_y:end_y + rotated_h, start_x:end_x + rotated_w]
            
            if search_region.size == 0:
                print(f"Warning: Empty search region for point {i}")
                continue
            
            angles = np.arange(best_angle_lowR-10, best_angle_lowR+10, 1)
            for angle in angles:
               
                # print(f"Processing angle in high-res: {angle} region {i}")
                # Run template matching on this specific region
                rotated_template = rotate_image(template, angle)
                result = cv2.matchTemplate(search_region, rotated_template, method)
                
                # Find best match in this region
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                # For SQDIFF, use minimum value; for others, use maximum
                if method == cv2.TM_SQDIFF_NORMED:
                    confidence = 1.0 - min_val  # Convert to similarity score
                    loc = min_loc
                else:
                    confidence = max_val
                    loc = max_loc
                
                # Convert local coordinates to global image coordinates
                global_x = start_x + loc[0]
                global_y = start_y + loc[1]
                
                all_high_res_results.append({
                    'confidence': confidence,
                    'location': (global_x, global_y),
                    'angle': angle,
                    'region_index': i
                })
                
                # Update best result if this region gives better confidence
                if confidence > best_high_res_confidence:
                    best_high_res_confidence = confidence
                    best_high_res_location = (global_x, global_y)
                    best_high_res_angle = angle
        
        # Sort results by confidence
        all_high_res_results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # # Extract top results for return
        # top_confidences = [result['confidence'] for result in all_high_res_results[:10]]
        # top_locations = [result['location'] for result in all_high_res_results[:10]]
        
        print(f"Best high-res confidence: {best_high_res_confidence:.4f}")
        print(f"Best high-res location: {best_high_res_location}")
        print(f"Best high-res angle: {best_high_res_angle}")
        
        # Create result image with the best match
        result_image = create_result_image(image, best_high_res_confidence, threshold, method, best_high_res_location, best_high_res_angle, rotated_w, rotated_h)

        return True, result_image, [len(all_high_res_results)], [best_high_res_confidence], [best_high_res_location]

    except Exception as e:
        print(f"Error during image processing: {str(e)}")
        return False, None, [], [], []

def create_result_image(image, best_confidence, threshold, method, locations, best_angle=0, w=0, h=0):
    """
    Create a result image with the template image and the result image.
    """
    # Create a copy of the image for drawing
    result_image = image.copy()
        
    #if the result is greater than the threshold, the color is green, otherwise red
    if best_confidence >= threshold:
        RGB = (0, 0, 0)
    else:
        RGB = (0, 0, 255)

    # Draw rectangle only at the highest confidence location
    if locations:  # Check if any matches were found
        #best_location = locations[0]  # First location has highest confidence
        cv2.rectangle(result_image, locations, 
                     (locations[0] + w, locations[1] + h), RGB, 2)
            
        # Add information to image (fixed positioning and method name)
        method_name = "TM_CCOEFF_NORMED" if method == cv2.TM_CCOEFF_NORMED else \
                     "TM_CCORR_NORMED" if method == cv2.TM_CCORR_NORMED else \
                     "TM_SQDIFF_NORMED" if method == cv2.TM_SQDIFF_NORMED else "Unknown"
        
        draw_text_with_background(result_image, f"Method: {method_name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, RGB, 2)
        draw_text_with_background(result_image, f"Threshold: {threshold:.2f}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, RGB, 2)
        draw_text_with_background(result_image, f"Best angle: {best_angle:.1f} deg", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, RGB, 2)
        draw_text_with_background(result_image, f"Confidence: {best_confidence:.4f}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, RGB, 2)
    else:
        draw_text_with_background(result_image, "No matches found", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    return result_image

def draw_text_with_background(img, text, org, font, font_scale, color, thickness, bg_color=(0,0,0), alpha=0.5):
    # Get the text size
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    x, y = org
    # Rectangle coordinates
    rect_x1, rect_y1 = x, y - text_h - baseline
    rect_x2, rect_y2 = x + text_w, y + baseline

    # Make a copy of the ROI
    overlay = img.copy()
    cv2.rectangle(overlay, (rect_x1, rect_y1), (rect_x2, rect_y2), bg_color, -1)
    # Blend the rectangle with the image
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    # Draw the text
    cv2.putText(img, text, org, font, font_scale, color, thickness, cv2.LINE_AA)

def rotate_image(image, angle):
    """
    Rotate an image by a given angle.
    
    Args:
        image: Input image
        angle: Rotation angle in degrees (positive = counterclockwise)
    
    Returns:
        Rotated image
    """
    # Get image dimensions
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    
    # Get rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Perform rotation
    rotated = cv2.warpAffine(image, rotation_matrix, (width, height), 
                            flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, 
                            borderValue=(255, 255, 255))
    
    return rotated

def test_template_rotations(template_path, image_path, threshold=0.8, method=cv2.TM_CCOEFF_NORMED,
                          start_angle=-30, end_angle=30, step=1.0):
    """
    Test template matching with different rotations and return results.
    
    Args:
        template_path (str): Path to the template image
        image_path (str): Path to the larger image
        threshold (float): Matching threshold (0-1)
        method: OpenCV template matching method
        start_angle (float): Starting rotation angle in degrees
        end_angle (float): Ending rotation angle in degrees
        step (float): Rotation step in degrees
    
    Returns:
        list: List of tuples (angle, best_confidence, num_matches, best_location)
    """
    try:
        # Read the images
        template = cv2.imread(template_path)
        image = cv2.imread(image_path)
        
        if template is None or image is None:
            print("Error: Could not read one or both images")
            return []
        
        results = []
        angles = np.arange(start_angle, end_angle + step, step)
        
        for angle in angles:
            # Rotate template
            rotated_template = rotate_image(template, angle)
            
            # Perform template matching
            result = cv2.matchTemplate(image, rotated_template, method)
            
            # Find best match for this angle
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # For SQDIFF, use minimum value; for others, use maximum
            if method == cv2.TM_SQDIFF_NORMED:
                confidence = 1.0 - min_val  # Convert to similarity score
                best_loc = min_loc
                locations = np.where(result <= (1.0 - threshold))
            else:
                confidence = max_val
                best_loc = max_loc
                locations = np.where(result >= threshold)
            
            num_matches = len(locations[0])
            
            results.append((angle, confidence, num_matches, best_loc))
        
        return results
        
    except Exception as e:
        print(f"Error during rotation testing: {str(e)}")
        return []

def create_rotation_result_image(image_path, template_path, rotation_results, method):
    """
    Create a result image with squares drawn based on rotation test results.
    
    Args:
        image_path (str): Path to the main image
        template_path (str): Path to the template image
        rotation_results (list): List of tuples (angle, best_confidence, num_matches, best_location)
        method: OpenCV template matching method
    
    Returns:
        result_image: Result image with squares drawn
    """
    try:
        # Read the images
        image = cv2.imread(image_path)
        template = cv2.imread(template_path)
        
        if image is None or template is None:
            print("Error: Could not read one or both images")
            return None
        
        # Get template dimensions
        template_h, template_w = template.shape[:2]
        
        # Create result image
        result_image = image.copy()
        
        # Find the best result to highlight
        best_result = max(rotation_results, key=lambda x: x[1])
        best_angle, best_conf, best_matches, best_loc = best_result
        
        # Draw squares for all results with different colors based on confidence
        for angle, confidence, num_matches, location in rotation_results:
            if location is None:
                continue
                
            # Color based on confidence (green for high confidence, red for low)
            if confidence > 0.8:
                color = (0, 255, 0)  # Green
            elif confidence > 0.6:
                color = (0, 255, 255)  # Yellow
            else:
                color = (0, 0, 255)  # Red
            
            # Make the best match thicker
            thickness = 3 if (angle, confidence, num_matches, location) == best_result else 1
            
            # Draw rectangle around the match
            cv2.rectangle(result_image, location, 
                         (location[0] + template_w, location[1] + template_h), 
                         color, thickness)
            
            # Add angle and confidence text
            text = f"{angle:.1f}° ({confidence:.3f})"
            cv2.putText(result_image, text, 
                       (location[0], location[1] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Add summary information
        cv2.putText(result_image, f"Best angle: {best_angle:.1f}°", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(result_image, f"Best confidence: {best_conf:.4f}", 
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(result_image, f"Total angles tested: {len(rotation_results)}", 
                   (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        return result_image
        
    except Exception as e:
        print(f"Error during result image creation: {str(e)}")
        return None

def remove_duplicate_points(points, distance_threshold=2):
    """
    Remove duplicate points that are within a certain distance of each other.
    
    Args:
        points (list): List of (x, y) coordinate tuples
        distance_threshold (int): Minimum distance between points to consider them different
    
    Returns:
        list: Filtered list of points with duplicates removed
    """
    if not points:
        return []
    
    filtered_points = [points[0]]  # Keep the first point
    
    for point in points[1:]:
        is_duplicate = False
        
        # Check distance to all existing filtered points
        for existing_point in filtered_points:
            distance = ((point[0] - existing_point[0])**2 + (point[1] - existing_point[1])**2)**0.5
            if distance <= distance_threshold:
                is_duplicate = True
                break
        
        # Add point only if it's not a duplicate
        if not is_duplicate:
            filtered_points.append(point)
    
    return filtered_points

def find_image_multiscale(image, template, threshold, method, rotation_start=0, rotation_end=0, rotation_step=0):
    """
    Multi-scale template matching with rotation testing: first on low-res, then refine on high-res.
    Displays the 10 highest correlation points on the low-res image for the best rotation.
    Uses step * 20 for rotation testing to speed up the process.
    """

    template_low_res = cv2.resize(template, (0,0), fx=0.5, fy=0.5)
    image_low_res = cv2.resize(image, (0,0), fx=0.5, fy=0.5)
    # Check if rotation testing is enabled
    if rotation_start == 0 and rotation_end == 0 and rotation_step == 0:
        # No rotation testing - just do regular multiscale matching

        th, tw = template_low_res.shape[:2]

       
    # Use 5x larger step for rotation testing
    rotation_range = rotation_end - rotation_start
    if rotation_range < 20:
        rotation_step = 1
    else:
        rotation_step = int(rotation_range / 20)
    angles = np.arange(rotation_start, rotation_end + rotation_step, rotation_step)
    
    best_confidence = -1
    best_angle = 0
    best_points = []
    best_confidences = []
    results_low_res = []
    
    # # Downscale main image for quick search
    # image_low_res = cv2.resize(image, (0,0), fx=0.5, fy=0.5)

    # Test different rotations
    for angle in angles:
        try:
            # print(f"Processing angle in small image: {angle}")
            # Rotate template first, then resize for low-res matching
            rotated_template_low_res = rotate_image(template_low_res, angle)
            # template_low_res = cv2.resize(rotated_template, (0,0), fx=0.5, fy=0.5)
            # th, tw = template_low_res.shape[:2]
            
            # Match on low-res
            result = cv2.matchTemplate(image_low_res, rotated_template_low_res, method)
            result_flat = result.flatten()
            
            if method == cv2.TM_SQDIFF_NORMED:
                # For SQDIFF, lower is better
                idxs = np.argpartition(result_flat, 10)[:10]
                scores = result_flat[idxs]
                sorted_idxs = idxs[np.argsort(scores)]
                best_score = np.min(result_flat)
                confidence = 1.0 - best_score  # Convert to similarity score
            else:
                # For others, higher is better
                idxs = np.argpartition(-result_flat, 10)[:10]
                scores = result_flat[idxs]
                sorted_idxs = idxs[np.argsort(-scores)]
                best_score = np.max(result_flat)
                confidence = best_score

            # Update best result if this angle gives better confidence
            if confidence > best_confidence:
                best_confidence = confidence
                best_angle = angle
                
                # Convert flat indices to 2D coordinates
                h, w = result.shape
                best_points = [(int(idx % w), int(idx // w)) for idx in sorted_idxs]
                best_confidences = [float(result[y, x]) for (x, y) in best_points]
                
                # Create results_low_res structure for this angle
                results_low_res = []
                for i, (x, y) in enumerate(best_points):
                    conf = best_confidences[i]
                    if method == cv2.TM_SQDIFF_NORMED:
                        conf = 1.0 - conf  # Convert to similarity score
                    results_low_res.append([conf, angle, x, y])
                
        except Exception as e:
            print(f"Error processing angle {angle}: {str(e)}")
            continue

    # If no valid results found, return default values
    if not best_points:
        print("No valid matches found")
        return [], [], 0, 0, []

    # Draw rectangles on a copy of the low-res image for the best rotation
    rotated_template = rotate_image(template, best_angle)
    template_low_res = cv2.resize(rotated_template, (0,0), fx=0.5, fy=0.5)
    th, tw = template_low_res.shape[:2]
    if (False): # debug
        vis = image_low_res.copy()
        for i, (x, y) in enumerate(best_points):
            color = (0, 255, 0) if i == 0 else (255, 0, 0)
            cv2.rectangle(vis, (x, y), (x+tw, y+th), color, 2)
            cv2.putText(vis, f"{i+1}", (x, y+15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Add rotation information to the image
        cv2.putText(vis, f"Best angle: {best_angle:.1f} deg", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(vis, f"Best confidence: {best_confidence:.4f}", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(vis, f"Rotation step: {rotation_step:.1f} deg", (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Display the annotated low-res image
        cv2.imshow('Top 10 Low-Res Matches (with rotation)', vis)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Return the top 10 points for further high-res refinement
    return best_points, best_confidences, best_angle, best_confidence, results_low_res
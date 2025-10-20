import glob
import shutil
import os

label_paths = glob.glob(r"C:\Users\524ha\Desktop\data_managment\detection_results\maksisarikapaktbksiz\frames\*txt")

def is_corner_close(center_y, threshold=0.1):
    print(center_y)
    return (center_y < threshold or center_y > 1 - threshold)

def process_labels(label_paths):
    # Define the destination folder
    destination_folder = r"C:\Users\524ha\Desktop\data_managment\detection_results\maksisarikapaktbksiz\hatali"
    
    # Ensure the destination folder exists
    os.makedirs(destination_folder, exist_ok=True)
    
    for label in label_paths:
        move_frame = False  # Initialize the variable at the start of the loop
        with open(label, "r") as file:
            data = file.read()
            rows = data.split("\n")

            # Process each row
            for row in rows:
                if row.strip():  # Skip empty lines
                    elements = row.split(" ")

                    # Check if the row has enough elements
                    if len(elements) < 3:
                        print(f"Warning: Row in file {label} does not have enough elements: {row}")
                        continue

                    try:
                        center_y = float(elements[2])
                    except ValueError:
                        print(f"Warning: Unable to parse center_y as float in file {label}: {row}")
                        continue

                    base_name = os.path.splitext(label)[0]  # File name (without extension)

                    image_path = base_name + ".jpg"

                    if is_corner_close(center_y):
                        move_frame = True
                        break

        if move_frame:  # Check the updated value of move_frame
            print(base_name)
            base_name_without_extension = os.path.splitext(os.path.basename(label))[0]

            base = os.path.basename(label)
            
            # Move the label file
            new_label_path = os.path.join(destination_folder, base)
            shutil.move(label, new_label_path)

            # Move the image file
            new_image_path = os.path.join(destination_folder, base_name_without_extension + ".jpg")
            
            # Check if the image file exists before attempting to move
            if os.path.exists(image_path):
                shutil.move(image_path, new_image_path)
            else:
                print(f"Warning: Image file {image_path} does not exist!")

# Usage
process_labels(label_paths)
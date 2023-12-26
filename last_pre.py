import os
import json
from shutil import copyfile
#1111
def normalize_coordinates(x, y, image_width, image_height):
    normalized_x = x / image_width
    normalized_y = y / image_height
    #print(x,y,normalized_x,normalized_y)
    return normalized_x, normalized_y
def test(a):
    a=a*a
    return a
def normalize_polygon_coordinates(polygon, image_width, image_height):
    normalized_polygon = [normalize_coordinates(polygon[i], polygon[i+1], image_width, image_height) for i in range(0, len(polygon), 2)]
    flattened_normalized_polygon = [coord for pair in normalized_polygon for coord in pair]
    return flattened_normalized_polygon
def save_image_and_label(json_path, image_folder, output_folder, label_folder, class_mapping):
    with open(json_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    environment_meta = data.get('Environment_meta', {})
    road_type = environment_meta.get('road_type', 'unknown')
    road_type_folder = os.path.join(output_folder, 'train_folderfor', road_type)

    # Find corresponding image file
    json_filename = os.path.basename(json_path)
    image_filename = os.path.splitext(json_filename)[0] + '.jpg'
    image_folder_base = os.path.basename(os.path.dirname(json_path))
    image_folder_with_camera = f"{image_folder_base}_camera"
    image_path_original = os.path.join(image_folder, image_folder_with_camera, image_filename)

    # Skip if image file not found
    if not os.path.exists(image_path_original):
        print(f"Image file not found: {image_path_original}")
        return

    os.makedirs(road_type_folder, exist_ok=True)

    # Copy image to 'images' folder
    output_image_folder = os.path.join(road_type_folder, 'images')
    os.makedirs(output_image_folder, exist_ok=True)
    output_image_path = os.path.join(output_image_folder, image_filename)
    copyfile(image_path_original, output_image_path)

    # Get image width and height
    image_width, image_height = data.get('width', 1980), data.get('height', 1080)
    #print(image_width,image_height)

    annotations = data.get('annotations', [])
    yolo_labels = []
    for annotation in annotations:
        class_name = annotation.get('class', 'unknown')
        class_id = class_mapping.get(class_name, -1)
        if class_id != -1:
            polygon_coordinates = normalize_polygon_coordinates(annotation.get('polygon', []), image_width, image_height)
            #print(polygon_coordinates)
            yolo_labels.append(f"{class_id} {' '.join(map(str, polygon_coordinates))}")

    # Save YOLO label file to 'labels' folder
    label_filename = os.path.splitext(image_filename)[0] + '.txt'
    label_filepath = os.path.join(road_type_folder, 'labels', label_filename)
    os.makedirs(os.path.join(road_type_folder, 'labels'), exist_ok=True)
    with open(label_filepath, 'w') as label_file:
        label_file.write('\n'.join(yolo_labels))

if __name__ == "__main__":
    json_input_base_folder = r"C:\Users\S340\Desktop\새 폴더_필터링"
    image_input_base_folder = r"C:\Users\S340\Desktop\New_Folder2"
    output_base_folder = r"C:\Users\S340\Desktop"
    label_folder = "labels"

    class_mapping = {
        "blueLane": 0,
        "crossWalk": 1,
        "curb": 2,
        "redLane": 3,
        "stopLane": 4,
        "whiteLane": 5,
        "yellowLane": 6
    }

    for root, dirs, files in os.walk(json_input_base_folder):
        for file in files:
            if file.endswith('.json'):
                json_path = os.path.join(root, file)
                save_image_and_label(json_path, image_input_base_folder, output_base_folder, label_folder, class_mapping)

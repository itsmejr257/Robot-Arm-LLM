from xarm.wrapper import XArmAPI
from drawable_objects import DRAWABLE_OBJECTS
from linedraw import linedraw
from PIL import Image

ip = '192.168.1.189'
arm = XArmAPI(ip)

def mirror_image(image_path, output_path):
    # Open the image file
    with Image.open(image_path) as img:
        # Mirror the image horizontally
        mirrored_img = img.transpose(Image.FLIP_LEFT_RIGHT)
        
        # Save the mirrored image
        mirrored_img.save(output_path)
        print(f"Mirrored image saved to {output_path}")

def move_arm(x, y, z):
    arm.set_position(x, y, z)
    return f"Moved arm to position ({x}, {y}, {z})"

def get_position(is_radian=None):
    return arm.get_position(is_radian=is_radian)

def draw_realistic(image):
    file_name = DRAWABLE_OBJECTS.get(image)
    image_path= f"images/{file_name}"
    mirror_image(image_path,image_path)

    lines = linedraw.sketch(image_path,draw_hatch=False, contour_simplify=1)

    # Initialize the min and max values to extremes
    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')

    robot_z = 188

    # Find the min and max values for x and y
    for line in lines:
        for point in line:
            x, y = point
            if x < min_x:
                min_x = x
            if y < min_y:
                min_y = y
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y

    # Define the target bounds
    x_min = 160
    x_max = 330
    x_bound = x_max - x_min # 170

    y_min = -235
    y_max = 80
    y_bound = y_max - y_min # 315

    # Calculate the scale factor based on the larger dimension
    scale_factor = min(x_bound / (max_x - min_x), y_bound / (max_y - min_y))

    # Scale the points proportionally
    scaled_lines = []
    for line in lines:
        scaled_line = []
        for point in line:
            x, y = point
            scaled_x = x_min + (x - min_x) * scale_factor
            scaled_y = y_min + (y - min_y) * scale_factor
            scaled_line.append((int(scaled_x), int(scaled_y)))
        scaled_lines.append(scaled_line)

    ip = '192.168.1.189'
    arm = XArmAPI(ip)
    arm.set_position(208, -3.9, 230, 180, 0, 0)

    total_points = sum(len(line) for line in scaled_lines)
    current_point = 0

    point_start = scaled_lines[0][0]
    print(point_start)
    x_start, y_start = point_start

    arm.set_position(x_start, y_start, 200)

    for scaled_line in scaled_lines:
        arm.set_position(z=200)

        for point in scaled_line:
            x_scaled, y_scaled = point
            arm.set_position(x_scaled, y_scaled, 188)
            current_point += 1
            percentage_done = (current_point / total_points) * 100
            print(f"Percentage done: {percentage_done:.2f}%")

    arm.set_position(208, -3.9, 230, 180, 0, 0)
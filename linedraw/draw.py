import linedraw
from xarm.wrapper import XArmAPI


def draw(image):
    # Assuming you have loaded the lines array using linedraw
    lines = linedraw.sketch(image, hatch_size=8, contour_simplify=1)

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

    # Calculate the scale factors
    x_scale = x_bound / (max_x - min_x)
    y_scale = y_bound / (max_y - min_y)

    # Scale the points
    scaled_lines = []
    for line in lines:
        scaled_line = []
        for point in line:
            x, y = point
            scaled_x = x_min + (x - min_x) * x_scale
            scaled_y = y_min + (y - min_y) * y_scale
            scaled_line.append((int(scaled_x), int(scaled_y)))
        scaled_lines.append(scaled_line)

    ip = '192.168.1.189'
    arm = XArmAPI(ip)

    arm.set_position(208, -3.9, 230, 180, 0, 0)

    total_points = sum(len(line) for line in scaled_lines)
    current_point = 0

    point_start = scaled_line[0]
    print(point_start)
    x_start, y_start = point_start

    arm.set_position(x_start, y_start, 220)

    for scaled_line in scaled_lines:
        arm.set_position(z=200)

        for point in scaled_line:
            x_scale, y_scale = point
            arm.set_position(x_scale, y_scale, 188)
            current_point += 1
            percentage_done = (current_point / total_points) * 100
            print(f"Percentage done: {percentage_done:.2f}%")

    arm.set_position(208, -3.9, 230, 180, 0, 0)



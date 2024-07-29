from xarm.wrapper import XArmAPI
import cv2
import base64
import openai
import pyrealsense2 as rs

ip = '192.168.1.189'
arm = XArmAPI(ip)
home_position = [-26, 1.4, 35.4, 0, 34, -25.7] #Joint Values NOT XYZRPY

#----------------------Used for Calibration----------------
arm_origin_x = 242
arm_origin_y = -95

arm_scissors_x = 232
arm_scissors_y = 45

arm_scissor_x_to_move = arm_scissors_x - arm_origin_x
arm_scissor_y_to_move = arm_scissors_y - arm_origin_y

cam_origin_x = 0
cam_origin_y = 0

cam_scissors_x = 18
cam_scissors_y = -229
#---------------------------------------------------------------------

def calculate_arm_coordinates(cam_x, cam_y):
    arm_to_move_x = round(cam_x * (arm_scissor_x_to_move / cam_scissors_x), 1)
    arm_to_move_y = round(cam_y * (arm_scissor_y_to_move / cam_scissors_y),1)

    final_x = arm_origin_x + arm_to_move_x
    final_y = arm_origin_y + arm_to_move_y

    return final_x, final_y


def arm_point_from_camera_coord(cam_x, cam_y):
    arm_coord = calculate_arm_coordinates(cam_y, cam_x)
    arm_coord_x, arm_coord_y = arm_coord

    arm.motion_enable(enable=True)
    arm.set_mode(0)  # Set the arm to position control mode
    arm.set_state(state=0) 
    arm.set_position(x= arm_coord_x, y=arm_coord_y)

    #Pointing Action
    initial_pos = arm.get_position()
    arm.set_position(z=initial_pos[1][2]-30)
    next_pos = arm.get_position()
    arm.set_position(z=next_pos[1][2]+30)

    return_home()

def return_home():
    arm.set_servo_angle(angle=home_position, speed=50, wait=True)

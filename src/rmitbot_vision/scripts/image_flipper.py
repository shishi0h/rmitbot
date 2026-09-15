#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class ImageFlipper(Node):
    def __init__(self):
        super().__init__('image_flipper')
        self.subscription = self.create_subscription(
            Image,
            '/test_camera/image_raw',
            self.listener_callback,
            10)
        self.publisher = self.create_publisher(Image, '/test_camera/image_flipped', 10)
        self.bridge = CvBridge()

    def listener_callback(self, msg):
        try:
            # Convert ROS Image message to OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # Flip the image.
            # -1 means flipping around both axes (180 degree rotation, fixing an upside-down camera)
            flipped_image = cv2.flip(cv_image, -1)
            
            # Note: The parking lines are permanently baked into the pixels by the camera's analog chip.
            # We cannot "remove" them to see what is behind them. The only way to remove them in software 
            # is to crop the image (e.g., crop out the bottom 30% of the image), which loses field of view.
            
            # Convert back to ROS Image message
            flipped_msg = self.bridge.cv2_to_imgmsg(flipped_image, "bgr8")
            flipped_msg.header = msg.header
            
            self.publisher.publish(flipped_msg)
        except Exception as e:
            self.get_logger().error(f"Failed to flip image: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = ImageFlipper()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

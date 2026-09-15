#!/usr/bin/env python3

import math
import rclpy
import numpy as np
import array
from rclpy.node import Node

from nav_msgs.msg import OccupancyGrid


from tf2_ros import Buffer, TransformListener

class MapMergeNode(Node):

    def __init__(self):
        super().__init__("map_merge_node")

        self.declare_parameter("robot0_topic", "/robot_0/map")
        self.declare_parameter("robot1_topic", "/robot_1/map")
        self.declare_parameter("merged_topic", "/map")

        robot0_topic = self.get_parameter("robot0_topic").get_parameter_value().string_value
        robot1_topic = self.get_parameter("robot1_topic").get_parameter_value().string_value
        merged_topic = self.get_parameter("merged_topic").get_parameter_value().string_value

        self.get_logger().info(f"Map Merge Node Started. Subscribing to {robot0_topic}, {robot1_topic}. Publishing to {merged_topic}")

        # TF Buffer and Listener for map offsets
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        self.tf0_x = 0.0
        self.tf0_y = 0.0
        self.tf1_x = 0.0
        self.tf1_y = 0.0

        # Store latest maps
        self.robot0_map = None
        self.robot1_map = None

        # Connection flags
        self.robot0_received = False
        self.robot1_received = False
        self.both_maps_ready = False

        # Print map information only once
        self.map_info_printed = False

        # Subscribers
        self.robot0_sub = self.create_subscription(
            OccupancyGrid,
            robot0_topic,
            self.robot0_callback,
            10
        )

        self.robot1_sub = self.create_subscription(
            OccupancyGrid,
            robot1_topic,
            self.robot1_callback,
            10
        )

        # Publisher
        self.map_pub = self.create_publisher(
            OccupancyGrid,
            merged_topic,
            10
        )

    def robot0_callback(self, msg):

        self.robot0_map = msg

        if not self.robot0_received:
            self.get_logger().info("Robot 0 map connected")
            self.robot0_received = True

        self.try_merge()

    def robot1_callback(self, msg):

        self.robot1_map = msg

        if not self.robot1_received:
            self.get_logger().info("Robot 1 map connected")
            self.robot1_received = True

        self.try_merge()

    def try_merge(self):

        # Wait until at least one map exists
        if self.robot0_map is None and self.robot1_map is None:
            return

        # Lookup TF for both robots if their maps are available
        try:
            if self.robot0_map is not None:
                trans0 = self.tf_buffer.lookup_transform('map', 'robot_0/map', rclpy.time.Time())
                self.tf0_x = trans0.transform.translation.x
                self.tf0_y = trans0.transform.translation.y
            
            if self.robot1_map is not None:
                trans1 = self.tf_buffer.lookup_transform('map', 'robot_1/map', rclpy.time.Time())
                self.tf1_x = trans1.transform.translation.x
                self.tf1_y = trans1.transform.translation.y
        except Exception as e:
            # Silently wait until TF is available
            return

        if not self.both_maps_ready and ((self.robot0_map is not None) or (self.robot1_map is not None)):
            self.get_logger().info("Map(s) and TF available for merging")
            self.both_maps_ready = True

        merged_map = self.merge_maps()

        # self.get_logger().info("Publishing merged map...")

        self.map_pub.publish(merged_map)

    def merge_maps(self):

        # --------------------------------------------------
        # Print map information (only once)
        # --------------------------------------------------
        if not self.map_info_printed:

            if self.robot0_map is not None:
                self.get_logger().info("==============================")
                self.get_logger().info("Robot 0 Map")
                self.get_logger().info("==============================")
                self.get_logger().info(f"Resolution : {self.robot0_map.info.resolution}")
                self.get_logger().info(f"Width      : {self.robot0_map.info.width}")
                self.get_logger().info(f"Height     : {self.robot0_map.info.height}")
                self.get_logger().info(f"Origin X   : {self.robot0_map.info.origin.position.x:.2f}")
                self.get_logger().info(f"Origin Y   : {self.robot0_map.info.origin.position.y:.2f}")

            if self.robot1_map is not None:
                self.get_logger().info("==============================")
                self.get_logger().info("Robot 1 Map")
                self.get_logger().info("==============================")
                self.get_logger().info(f"Resolution : {self.robot1_map.info.resolution}")
                self.get_logger().info(f"Width      : {self.robot1_map.info.width}")
                self.get_logger().info(f"Height     : {self.robot1_map.info.height}")
                self.get_logger().info(f"Origin X   : {self.robot1_map.info.origin.position.x:.2f}")
                self.get_logger().info(f"Origin Y   : {self.robot1_map.info.origin.position.y:.2f}")

            self.map_info_printed = True

        # --------------------------------------------------
        # Compute merged map boundary (EVERY callback)
        # --------------------------------------------------

        base_map = self.robot0_map if self.robot0_map is not None else self.robot1_map
        res = base_map.info.resolution

        merged_min_x = float('inf')
        merged_min_y = float('inf')
        merged_max_x = float('-inf')
        merged_max_y = float('-inf')

        # Robot 0 bounds
        if self.robot0_map is not None:
            min_x0 = self.robot0_map.info.origin.position.x + self.tf0_x
            min_y0 = self.robot0_map.info.origin.position.y + self.tf0_y
            max_x0 = min_x0 + self.robot0_map.info.width * res
            max_y0 = min_y0 + self.robot0_map.info.height * res
            merged_min_x = min(merged_min_x, min_x0)
            merged_min_y = min(merged_min_y, min_y0)
            merged_max_x = max(merged_max_x, max_x0)
            merged_max_y = max(merged_max_y, max_y0)

        # Robot 1 bounds
        if self.robot1_map is not None:
            min_x1 = self.robot1_map.info.origin.position.x + self.tf1_x
            min_y1 = self.robot1_map.info.origin.position.y + self.tf1_y
            max_x1 = min_x1 + self.robot1_map.info.width * res
            max_y1 = min_y1 + self.robot1_map.info.height * res
            merged_min_x = min(merged_min_x, min_x1)
            merged_min_y = min(merged_min_y, min_y1)
            merged_max_x = max(merged_max_x, max_x1)
            merged_max_y = max(merged_max_y, max_y1)

        merged_width = math.ceil((merged_max_x - merged_min_x) / res)
        merged_height = math.ceil((merged_max_y - merged_min_y) / res)

        # Print merged map info only once
        if not hasattr(self, "merged_info_printed"):
            self.get_logger().info("========== MERGED MAP ==========")
            self.get_logger().info(f"Origin X : {merged_min_x:.2f}")
            self.get_logger().info(f"Origin Y : {merged_min_y:.2f}")
            self.get_logger().info(f"Width    : {merged_width}")
            self.get_logger().info(f"Height   : {merged_height}")
            self.merged_info_printed = True

        # --------------------------------------------------
        # Create merged OccupancyGrid
        # --------------------------------------------------

        merged_map = OccupancyGrid()

        # Header
        merged_map.header = base_map.header
        merged_map.header.frame_id = "map"

        # Map information
        merged_map.info.resolution = res
        merged_map.info.width = merged_width
        merged_map.info.height = merged_height

        merged_map.info.origin.position.x = merged_min_x
        merged_map.info.origin.position.y = merged_min_y
        merged_map.info.origin.position.z = 0.0

        merged_map.info.origin.orientation.x = 0.0
        merged_map.info.origin.orientation.y = 0.0
        merged_map.info.origin.orientation.z = 0.0
        merged_map.info.origin.orientation.w = 1.0

        # Fill every cell with UNKNOWN (-1)
        merged_map.data = [-1] * (merged_width * merged_height)

        # Copy maps if available
        if self.robot0_map is not None:
            self.copy_map(self.robot0_map, merged_map, self.tf0_x, self.tf0_y)

        if self.robot1_map is not None:
            self.copy_map(self.robot1_map, merged_map, self.tf1_x, self.tf1_y)

        return merged_map

    def copy_map(self, source_map, merged_map, offset_x_m, offset_y_m):

        width = source_map.info.width
        height = source_map.info.height

        resolution = source_map.info.resolution

        # Calculate offset in grid cells
        origin_x = source_map.info.origin.position.x + offset_x_m
        origin_y = source_map.info.origin.position.y + offset_y_m
        offset_x = int(round((origin_x - merged_map.info.origin.position.x) / resolution))
        offset_y = int(round((origin_y - merged_map.info.origin.position.y) / resolution))

        # Convert maps to 2D numpy arrays
        src_data = np.array(source_map.data, dtype=np.int8).reshape((height, width))
        merged_data = np.array(merged_map.data, dtype=np.int8).reshape((merged_map.info.height, merged_map.info.width))

        # Define bounds within the merged map
        end_x = offset_x + width
        end_y = offset_y + height

        # Ensure bounds are within merged map
        start_x_merged = max(0, offset_x)
        start_y_merged = max(0, offset_y)
        end_x_merged = min(merged_map.info.width, end_x)
        end_y_merged = min(merged_map.info.height, end_y)

        start_x_src = max(0, -offset_x)
        start_y_src = max(0, -offset_y)
        end_x_src = start_x_src + (end_x_merged - start_x_merged)
        end_y_src = start_y_src + (end_y_merged - start_y_merged)

        # Get region of interest (ROI)
        roi = merged_data[start_y_merged:end_y_merged, start_x_merged:end_x_merged]
        src_roi = src_data[start_y_src:end_y_src, start_x_src:end_x_src]

        # Overlay logic
        mask_src_known = (src_roi != -1)
        mask_roi_unknown = (roi == -1)

        # 1. Update unknown cells in merged map with known cells from source map
        roi[mask_roi_unknown & mask_src_known] = src_roi[mask_roi_unknown & mask_src_known]

        # 2. For known cells in both, take the maximum cost
        mask_both_known = (~mask_roi_unknown) & mask_src_known
        roi[mask_both_known] = np.maximum(roi[mask_both_known], src_roi[mask_both_known])

        merged_map.data = array.array('b', merged_data.ravel().astype(np.int8).tobytes())


def main(args=None):

    rclpy.init(args=args)

    node = MapMergeNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
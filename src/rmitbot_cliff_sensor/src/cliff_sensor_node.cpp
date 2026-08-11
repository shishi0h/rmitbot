#include "rmitbot_cliff_sensor/cliff_sensor_node.hpp"
#include <sstream>

CliffSensorNode::CliffSensorNode() : Node("cliff_sensor_node") {
    this->declare_parameter("port", "/dev/ttyUSB0");
    this->declare_parameter("cliff_threshold", 0.08); // 80 mm

    port_name_ = this->get_parameter("port").as_string();
    cliff_threshold_ = this->get_parameter("cliff_threshold").as_double();

    estop_pub_ = this->create_publisher<std_msgs::msg::Bool>("emergency_stop", 10);
    array_pub_ = this->create_publisher<std_msgs::msg::Int32MultiArray>("sensors/cliff/all_ranges", 10);
    
    for (int i = 0; i < 6; i++) {
        range_pubs_.push_back(this->create_publisher<sensor_msgs::msg::Range>(
            "sensors/cliff/range_" + std::to_string(i), 10));
    }

    try {
        serial_port_.Open(port_name_);
        serial_port_.SetBaudRate(LibSerial::BaudRate::BAUD_115200);
        RCLCPP_INFO(this->get_logger(), "Successfully opened serial port: %s", port_name_.c_str());
    } catch (...) {
        RCLCPP_ERROR(this->get_logger(), "Failed to open serial port: %s", port_name_.c_str());
    }

    timer_ = this->create_wall_timer(
        std::chrono::milliseconds(20),
        std::bind(&CliffSensorNode::read_serial, this));
}

CliffSensorNode::~CliffSensorNode() {
    if (serial_port_.IsOpen()) {
        serial_port_.Close();
    }
}

void CliffSensorNode::read_serial() {
    if (!serial_port_.IsOpen()) return;

    if (serial_port_.IsDataAvailable()) {
        std::string message;
        serial_port_.ReadLine(message);

        message.erase(std::remove(message.begin(), message.end(), '\n'), message.end());
        message.erase(std::remove(message.begin(), message.end(), '\r'), message.end());

        // RCLCPP_INFO(this->get_logger(), "Raw serial: %s", message.c_str());

        if (!message.empty() && (message.front() == '[' || message.front() == '<') && (message.back() == ']' || message.back() == '>')) {
            std::string data = message.substr(1, message.size() - 2);
            std::stringstream ss(data);
            std::string token;
            std::vector<uint16_t> distances;

            while (std::getline(ss, token, '\t')) {
                try {
                    distances.push_back(std::stoi(token));
                } catch (...) {
                    distances.push_back(0);
                }
            }

            bool emergency_stop = false;

            for (size_t i = 0; i < distances.size() && i < range_pubs_.size(); ++i) {
                double distance_m = distances[i] / 1000.0;
                
                sensor_msgs::msg::Range range_msg;
                range_msg.header.stamp = this->now();
                range_msg.header.frame_id = "cliff_sensor_" + std::to_string(i) + "_link";
                range_msg.radiation_type = sensor_msgs::msg::Range::INFRARED;
                range_msg.field_of_view = 0.436332; // 25 degrees for VL53L0X
                range_msg.min_range = 0.0;
                range_msg.max_range = 2.0;
                range_msg.range = distance_m;
                
                range_pubs_[i]->publish(range_msg);

                // If distance is greater than threshold, it's a cliff
                // Or if it's 0 it might be an error, but let's just trigger on > threshold
                if (distance_m > cliff_threshold_) {
                    emergency_stop = true;
                }
            }
            
            std_msgs::msg::Int32MultiArray array_msg;
            for (size_t i = 0; i < distances.size(); ++i) {
                array_msg.data.push_back(distances[i]); // Push raw mm values
            }
            array_pub_->publish(array_msg);

            std_msgs::msg::Bool estop_msg;
            estop_msg.data = emergency_stop;
            estop_pub_->publish(estop_msg);
        }
    }
}

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<CliffSensorNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}

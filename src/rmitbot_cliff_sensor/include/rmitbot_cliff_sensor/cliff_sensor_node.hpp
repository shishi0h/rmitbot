#ifndef CLIFF_SENSOR_NODE_HPP
#define CLIFF_SENSOR_NODE_HPP

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/bool.hpp>
#include <sensor_msgs/msg/range.hpp>
#include <libserial/SerialPort.h>

class CliffSensorNode : public rclcpp::Node {
public:
    CliffSensorNode();
    ~CliffSensorNode();

private:
    void read_serial();
    
    LibSerial::SerialPort serial_port_;
    std::string port_name_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr estop_pub_;
    std::vector<rclcpp::Publisher<sensor_msgs::msg::Range>::SharedPtr> range_pubs_;
    
    double cliff_threshold_;
};

#endif

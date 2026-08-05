#ifndef CLIFF_SAFETY_FILTER_NODE_HPP
#define CLIFF_SAFETY_FILTER_NODE_HPP

#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <sensor_msgs/msg/range.hpp>
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>

class CliffSafetyFilterNode : public rclcpp::Node {
public:
    CliffSafetyFilterNode();

private:
    void cmd_vel_callback(const geometry_msgs::msg::Twist::SharedPtr msg);
    void range_callback(const sensor_msgs::msg::Range::SharedPtr msg, const std::string& topic_name);

    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;

    std::vector<std::string> front_topics_;
    std::vector<std::string> back_topics_;
    std::vector<std::string> left_topics_;
    std::vector<std::string> right_topics_;

    std::unordered_map<std::string, double> latest_ranges_;
    std::vector<rclcpp::Subscription<sensor_msgs::msg::Range>::SharedPtr> range_subs_;

    double cliff_threshold_;

    bool is_cliff_detected(const std::vector<std::string>& topics);
};

#endif

#include "rmitbot_cliff_sensor/cliff_safety_filter_node.hpp"

CliffSafetyFilterNode::CliffSafetyFilterNode() : Node("cliff_safety_filter_node") {
    // Declare parameters for topic lists
    this->declare_parameter("front_sensor_topics", std::vector<std::string>{"/sensors/cliff/range_0", "/sensors/cliff/range_1"});
    this->declare_parameter("back_sensor_topics", std::vector<std::string>{});
    this->declare_parameter("left_sensor_topics", std::vector<std::string>{});
    this->declare_parameter("right_sensor_topics", std::vector<std::string>{});
    this->declare_parameter("cliff_threshold", 0.08);

    front_topics_ = this->get_parameter("front_sensor_topics").as_string_array();
    back_topics_ = this->get_parameter("back_sensor_topics").as_string_array();
    left_topics_ = this->get_parameter("left_sensor_topics").as_string_array();
    right_topics_ = this->get_parameter("right_sensor_topics").as_string_array();
    cliff_threshold_ = this->get_parameter("cliff_threshold").as_double();

    // Create subscriptions for all configured topics
    auto create_subs = [this](const std::vector<std::string>& topics) {
        for (const auto& topic : topics) {
            if (latest_ranges_.find(topic) == latest_ranges_.end()) {
                latest_ranges_[topic] = 0.0; // Initialize safe value
                auto sub = this->create_subscription<sensor_msgs::msg::Range>(
                    topic, 10,
                    [this, topic](sensor_msgs::msg::Range::SharedPtr msg) {
                        this->range_callback(msg, topic);
                    }
                );
                range_subs_.push_back(sub);
            }
        }
    };

    create_subs(front_topics_);
    create_subs(back_topics_);
    create_subs(left_topics_);
    create_subs(right_topics_);

    cmd_vel_sub_ = this->create_subscription<geometry_msgs::msg::Twist>(
        "cmd_vel_in", 10, std::bind(&CliffSafetyFilterNode::cmd_vel_callback, this, std::placeholders::_1));
    cmd_vel_pub_ = this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel_out", 10);
    
    RCLCPP_INFO(this->get_logger(), "Cliff Safety Filter Node Started.");
}

void CliffSafetyFilterNode::range_callback(const sensor_msgs::msg::Range::SharedPtr msg, const std::string& topic_name) {
    latest_ranges_[topic_name] = msg->range;
}

bool CliffSafetyFilterNode::is_cliff_detected(const std::vector<std::string>& topics) {
    for (const auto& topic : topics) {
        if (latest_ranges_[topic] > cliff_threshold_) {
            return true;
        }
    }
    return false;
}

void CliffSafetyFilterNode::cmd_vel_callback(const geometry_msgs::msg::Twist::SharedPtr msg) {
    auto filtered_cmd = *msg;

    // Check Linear X (Forward/Backward)
    if (filtered_cmd.linear.x > 0.0 && is_cliff_detected(front_topics_)) {
        filtered_cmd.linear.x = 0.0;
        RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000, "Forward motion blocked by front cliff sensor!");
    } else if (filtered_cmd.linear.x < 0.0 && is_cliff_detected(back_topics_)) {
        filtered_cmd.linear.x = 0.0;
        RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000, "Backward motion blocked by rear cliff sensor!");
    }

    // Check Angular Z (Turning Left/Right)
    if (filtered_cmd.angular.z > 0.0 && is_cliff_detected(left_topics_)) {
        filtered_cmd.angular.z = 0.0;
        RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000, "Left turn blocked by left cliff sensor!");
    } else if (filtered_cmd.angular.z < 0.0 && is_cliff_detected(right_topics_)) {
        filtered_cmd.angular.z = 0.0;
        RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000, "Right turn blocked by right cliff sensor!");
    }

    cmd_vel_pub_->publish(filtered_cmd);
}

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<CliffSafetyFilterNode>());
    rclcpp::shutdown();
    return 0;
}

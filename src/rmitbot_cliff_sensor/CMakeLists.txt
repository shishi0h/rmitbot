cmake_minimum_required(VERSION 3.8)
project(rmitbot_cliff_sensor)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(PkgConfig REQUIRED)

pkg_check_modules(SERIAL libserial REQUIRED)

add_executable(cliff_sensor_node src/cliff_sensor_node.cpp)
target_include_directories(cliff_sensor_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
target_link_libraries(cliff_sensor_node "${SERIAL_LDFLAGS}")
ament_target_dependencies(cliff_sensor_node
  rclcpp
  std_msgs
  sensor_msgs
)

add_executable(cliff_safety_filter_node src/cliff_safety_filter_node.cpp)
target_include_directories(cliff_safety_filter_node PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(cliff_safety_filter_node
  rclcpp
  std_msgs
  sensor_msgs
  geometry_msgs
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

install(
  DIRECTORY urdf include launch
  DESTINATION share/${PROJECT_NAME}
)

install(TARGETS cliff_sensor_node cliff_safety_filter_node
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()

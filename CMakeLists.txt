cmake_minimum_required(VERSION 3.8)
project(dif_bot)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf launch config worlds maps rviz
  DESTINATION share/${PROJECT_NAME})

install(PROGRAMS scripts/mision.py scripts/cmd_vel_to_stamped.py scripts/comparar_odom.py
  DESTINATION lib/${PROJECT_NAME})

ament_package()

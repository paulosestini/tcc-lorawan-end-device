# Install script for directory: C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "C:/tcc-lorawan-end-device/active_ap/build/esp-idf/espressif__eigen/eigen-build/install")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Debug")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "TRUE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "C:/Espressif/tools/xtensa-esp32-elf/esp-2021r2-patch5-8.4.0/xtensa-esp32-elf/bin/xtensa-esp32-elf-objdump.exe")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xDevelx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/eigen3/unsupported/Eigen" TYPE FILE FILES
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/AdolcForward"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/AlignedVector3"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/ArpackSupport"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/AutoDiff"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/BVH"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/EulerAngles"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/FFT"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/IterativeSolvers"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/KroneckerProduct"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/LevenbergMarquardt"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/MatrixFunctions"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/MoreVectorization"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/MPRealSupport"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/NonLinearOptimization"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/NumericalDiff"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/OpenGLSupport"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/Polynomials"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/Skyline"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/SparseExtra"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/SpecialFunctions"
    "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/Splines"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xDevelx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/eigen3/unsupported/Eigen" TYPE DIRECTORY FILES "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen/unsupported/Eigen/src" FILES_MATCHING REGEX "/[^/]*\\.h$")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("C:/tcc-lorawan-end-device/active_ap/build/esp-idf/espressif__eigen/eigen-build/unsupported/Eigen/CXX11/cmake_install.cmake")

endif()


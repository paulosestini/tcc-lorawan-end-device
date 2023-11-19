# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "C:/tcc-lorawan-end-device/active_ap/managed_components/espressif__eigen/eigen"
  "C:/tcc-lorawan-end-device/active_ap/build/esp-idf/espressif__eigen/eigen-build"
  "C:/tcc-lorawan-end-device/active_ap/build/esp-idf/espressif__eigen/eigen_proj-prefix"
  "C:/tcc-lorawan-end-device/active_ap/build/esp-idf/espressif__eigen/eigen_proj-prefix/tmp"
  "C:/tcc-lorawan-end-device/active_ap/build/esp-idf/espressif__eigen/eigen_proj-prefix/src/eigen_proj-stamp"
  "C:/tcc-lorawan-end-device/active_ap/build/esp-idf/espressif__eigen/eigen_proj-prefix/src"
  "C:/tcc-lorawan-end-device/active_ap/build/esp-idf/espressif__eigen/eigen_proj-prefix/src/eigen_proj-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "C:/tcc-lorawan-end-device/active_ap/build/esp-idf/espressif__eigen/eigen_proj-prefix/src/eigen_proj-stamp/${subDir}")
endforeach()

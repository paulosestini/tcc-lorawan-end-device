# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "C:/Espressif/frameworks/esp-idf-v4.4.5/components/bootloader/subproject"
  "C:/tcc-lorawan-end-device/active_ap/build/bootloader"
  "C:/tcc-lorawan-end-device/active_ap/build/bootloader-prefix"
  "C:/tcc-lorawan-end-device/active_ap/build/bootloader-prefix/tmp"
  "C:/tcc-lorawan-end-device/active_ap/build/bootloader-prefix/src/bootloader-stamp"
  "C:/tcc-lorawan-end-device/active_ap/build/bootloader-prefix/src"
  "C:/tcc-lorawan-end-device/active_ap/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "C:/tcc-lorawan-end-device/active_ap/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()

cmake_minimum_required(VERSION 3.18)

project(SourceAudio VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(sourceaudio SHARED
    src/audio.cpp
    src/api.cpp
)

target_include_directories(sourceaudio PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

find_package(Threads REQUIRED)

target_link_libraries(sourceaudio PRIVATE
    Threads::Threads
    ${CMAKE_DL_LIBS}
)

if(UNIX AND NOT APPLE)
    target_link_libraries(sourceaudio PRIVATE m)
endif()

if(WIN32)
    target_link_libraries(sourceaudio PRIVATE winmm ole32)
endif()
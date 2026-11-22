
#include <pybind11/pybind11.h>

#include "sourceaudio/audio.hpp"

namespace py = pybind11;

PYBIND11_MODULE(sourceaudio, m) {
    m.doc() = "SourceAudio native audio engine";

    py::class_<SourceAudio::Audio>(m, "Audio")
        .def(py::init<>())

        .def("load_music",
             &SourceAudio::Audio::loadMusic)

        .def("play_music",
             &SourceAudio::Audio::playMusic,
             py::arg("loop") = false)

        .def("stop_music",
             &SourceAudio::Audio::stopMusic)

        .def("set_music_volume",
             &SourceAudio::Audio::setMusicVolume)

        .def("set_sound_volume",
             &SourceAudio::Audio::setSoundVolume)

        .def("play_sound",
             &SourceAudio::Audio::playSound);
}

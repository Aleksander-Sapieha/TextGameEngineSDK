
import ctypes
import os


# Load shared library
_library_path = os.path.join(
    os.path.dirname(__file__),
    "libsourceaudio.so"
)

_audio = ctypes.CDLL(_library_path)


# Function definitions
_audio.sa_create.argtypes = []
_audio.sa_create.restype = ctypes.c_void_p

_audio.sa_destroy.argtypes = [
    ctypes.c_void_p
]
_audio.sa_destroy.restype = None

_audio.sa_load_music.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p
]
_audio.sa_load_music.restype = ctypes.c_int

_audio.sa_play_music.argtypes = [
    ctypes.c_void_p,
    ctypes.c_int
]
_audio.sa_play_music.restype = None

_audio.sa_stop_music.argtypes = [
    ctypes.c_void_p
]
_audio.sa_stop_music.restype = None

_audio.sa_set_music_volume.argtypes = [
    ctypes.c_void_p,
    ctypes.c_float
]
_audio.sa_set_music_volume.restype = None

_audio.sa_set_sound_volume.argtypes = [
    ctypes.c_void_p,
    ctypes.c_float
]
_audio.sa_set_sound_volume.restype = None

_audio.sa_play_sound.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p
]
_audio.sa_play_sound.restype = ctypes.c_int


class Audio:
    def __init__(self):
        self._handle = _audio.sa_create()

        if not self._handle:
            raise RuntimeError("Failed to create audio instance")

    def loadMusic(self, path):
        return bool(
            _audio.sa_load_music(
                self._handle,
                os.fsencode(path)
            )
        )

    def playMusic(self, loop=False):
        _audio.sa_play_music(
            self._handle,
            int(loop)
        )

    def stopMusic(self):
        _audio.sa_stop_music(self._handle)

    def setMusicVolume(self, volume):
        _audio.sa_set_music_volume(
            self._handle,
            float(volume)
        )

    def setSoundVolume(self, volume):
        _audio.sa_set_sound_volume(
            self._handle,
            float(volume)
        )

    def playSound(self, path):
        return bool(
            _audio.sa_play_sound(
                self._handle,
                os.fsencode(path)
            )
        )

    def close(self):
        if self._handle:
            _audio.sa_destroy(self._handle)
            self._handle = None

    def __del__(self):
        self.close()

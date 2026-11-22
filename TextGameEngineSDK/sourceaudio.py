
import ctypes
from pathlib import Path


_library = Path(__file__).parent / "libsourceaudio.so"

_lib = ctypes.CDLL(str(_library))

_lib.sa_create.restype = ctypes.c_void_p

_lib.sa_destroy.argtypes = [ctypes.c_void_p]

_lib.sa_load_music.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p
]
_lib.sa_load_music.restype = ctypes.c_int

_lib.sa_play_music.argtypes = [
    ctypes.c_void_p,
    ctypes.c_int
]

_lib.sa_stop_music.argtypes = [ctypes.c_void_p]

_lib.sa_set_music_volume.argtypes = [
    ctypes.c_void_p,
    ctypes.c_float
]

_lib.sa_set_sound_volume.argtypes = [
    ctypes.c_void_p,
    ctypes.c_float
]

_lib.sa_play_sound.argtypes = [
    ctypes.c_void_p,
    ctypes.c_char_p
]
_lib.sa_play_sound.restype = ctypes.c_int


class Audio:
    def __init__(self):
        self._handle = _lib.sa_create()

        if not self._handle:
            raise RuntimeError("Could not initialize SourceAudio")

    def load_music(self, path):
        return bool(_lib.sa_load_music(
            self._handle,
            str(path).encode()
        ))

    def play_music(self, loop=False):
        _lib.sa_play_music(self._handle, int(loop))

    def stop_music(self):
        _lib.sa_stop_music(self._handle)

    def set_music_volume(self, volume):
        _lib.sa_set_music_volume(self._handle, volume)

    def set_sound_volume(self, volume):
        _lib.sa_set_sound_volume(self._handle, volume)

    def play_sound(self, path):
        return bool(_lib.sa_play_sound(
            self._handle,
            str(path).encode()
        ))

    def close(self):
        if self._handle:
            _lib.sa_destroy(self._handle)
            self._handle = None

    def __del__(self):
        self.close()

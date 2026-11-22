import ctypes
from pathlib import Path

# Load the compiled C library
_lib = ctypes.CDLL(
    str(Path(__file__).with_name("bfppp.so"))
)

# Configure the C function
_lib.run.argtypes = [ctypes.c_char_p]
_lib.run.restype = ctypes.c_int


def run(path):
    """Execute a Brainfuck++ program from a file."""
    return _lib.run(str(path).encode("utf-8"))

if __name__ == "__main__":
    run("test.bfppp")
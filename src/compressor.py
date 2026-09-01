import ctypes
import platform
import struct
from pathlib import Path

def _find_lib() -> Path:
    """
    Locates the compiled lz77 shared library relative to this file's
    own location (not the process's cwd), and picks the right
    extension for the current platform.
    """
    lib_dir = Path(__file__).resolve().parent / "bin"
    system = platform.system()

    if system == "Linux":
        name = "lz77.so"
    elif system == "Darwin":
        name = "lz77.so"
    elif system == "Windows":
        name = "lz77.dll"
    else:
        raise RuntimeError(f"Unsupported platform for lz77 compression: {system}")

    lib_path = lib_dir / name
    if not lib_path.exists():
        raise FileNotFoundError( f"Could not find compression library at {lib_path}. ""Was pix2gba installed correctly?")
    return lib_path


lib = ctypes.CDLL(str(_find_lib()))

lib.GBA_LZ77CompressBound.argtypes = [ctypes.c_size_t]
lib.GBA_LZ77CompressBound.restype = ctypes.c_size_t

lib.GBA_LZ77Compress.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t
]
lib.GBA_LZ77Compress.restype = ctypes.c_ssize_t


def gba_lz77_compress(data: bytes) -> bytes:
    """
    The compression function that invokes a compiled binary to compress the data
    :param data: Uncompressed byte stream of the unit
    :return: Compressed byte stream of the unit
    """
    # Normalize to an immutable bytes object for from_buffer_copy
    data = bytes(data)

    in_len = len(data)
    in_buf = (ctypes.c_ubyte * in_len).from_buffer_copy(data)

    # Use the *bound* function (not the compressor) to size the output buffer
    out_cap = lib.GBA_LZ77CompressBound(in_len)
    out_py = bytearray(out_cap)
    out_buf = (ctypes.c_ubyte * out_cap).from_buffer(out_py)

    n = lib.GBA_LZ77Compress(in_buf, in_len, out_buf, out_cap)
    if n < 0:
        raise RuntimeError(f"GBA_LZ77Compress failed: {n}")
    return bytes(out_py[:n])


def gba_lz77_compress_list(data: list) -> bytes:
    """
    Compresses a list of u32 values (either hex strings like "0x1234ABCD"
    or plain ints/numpy ints) using GBA LZ77 compression.
    :param data: List of u32 words, as hex strings or integers
    :return: Compressed byte stream
    """
    if len(data) == 0:
        return b""

    if isinstance(data[0], str):
        int_data = [int(s, 16) for s in data]
    else:
        # Normalizes numpy ints (and any other int-like type) to plain int
        int_data = [int(s) for s in data]

    try:
        byte_array = struct.pack(f"<{len(int_data)}I", *int_data)
    except struct.error as e:
        raise ValueError(f"Invalid u32 data for compression: {e}") from e

    return gba_lz77_compress(byte_array)
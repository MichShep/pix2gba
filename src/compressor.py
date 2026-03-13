import ctypes
import struct

lib = ctypes.CDLL("./bin/lz77.so")

lib.GBA_LZ77CompressBound.argtypes = [ctypes.c_size_t]
lib.GBA_LZ77CompressBound.restype  = ctypes.c_size_t

lib.GBA_LZ77Compress.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t
]
lib.GBA_LZ77Compress.restype = ctypes.c_ssize_t


def gba_lz77_compress(data: bytes) -> bytes:
    """
    The compression function that invokes a cpp bin to compress the data
    :param data: Uncompressed byte stream of the unit
    :return: Compressed byte stream of the unit
    """
    # Ensure we have an immutable bytes object for from_buffer_copy
    if isinstance(data, bytearray):
        data = bytes(data)
    elif not isinstance(data, (bytes, bytearray)):
        data = bytes(data)

    in_len = len(data)
    in_buf = (ctypes.c_ubyte * in_len).from_buffer_copy(data)

    # Use the *bound* function (not the compressor) to size the output buffer
    out_cap = lib.GBA_LZ77CompressBound(in_len)
    out_py  = bytearray(out_cap)
    out_buf = (ctypes.c_ubyte * out_cap).from_buffer(out_py)

    # Call the correct function name
    n = lib.GBA_LZ77Compress(in_buf, in_len, out_buf, out_cap)
    if n < 0:
        raise RuntimeError(f"GBA_LZ77Compress failed: {n}")
    return bytes(out_py[:n])

def gba_lz77_compress_list(data: list) -> bytes:
    int_data = data.copy()

    if type(data[0]) is not int:
        int_data = [int(s, 16) for s in int_data]

    byte_array = struct.pack("<%dI" % len(int_data), *int_data)

    return gba_lz77_compress(byte_array)

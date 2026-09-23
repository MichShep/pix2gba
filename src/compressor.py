import struct
from typing import Union

# GBA BIOS LZ77 limits
LZ77_MIN_MATCH = 3
LZ77_MAX_MATCH = 18
LZ77_WINDOW = 0x1000
# Minimum distance back to a match (LZ77UnCompVram needs at least 2 because VRAM is written 16 bits at a time)
LZ77_MIN_DISTANCE = 8


def _find_match(data: bytes, offset: int, length: int) -> int:
    """
    Finds the nearest earlier copy of data[offset:offset + length] inside the LZ77 window.
    The copy may overlap the current position, which the BIOS decoder supports.
    :param data: Uncompressed byte stream
    :param offset: Position of the bytes to match
    :param length: Number of bytes that must match
    :return: Start index of the match, or -1 if there is none
    """
    if offset < LZ77_MIN_DISTANCE or offset + length > len(data):
        return -1

    window_start = max(0, offset - LZ77_WINDOW)
    window_end = offset - LZ77_MIN_DISTANCE + length
    return data.rfind(data[offset:offset + length], window_start, window_end)


def gba_lz77_compress(data: bytes) -> bytes:
    """
    Compresses a byte stream into the GBA BIOS LZ77 format (LZ77UnCompVram / LZ77UnCompWram).
    :param data: Uncompressed byte stream of the unit
    :return: Compressed byte stream of the unit, padded to a multiple of 4 bytes
    """
    data = bytes(data)
    data_len = len(data)

    # Header: compression type 0x10 with the uncompressed size in the upper 24 bits
    out = bytearray(struct.pack("<I", (data_len << 8) | 0x10))

    offset = 0
    while offset < data_len:
        # Each block is a flag byte followed by up to 8 literals/tokens (MSB first, 1 = token)
        flag_position = len(out)
        out.append(0)
        flags = 0

        for bit in range(8):
            if offset >= data_len:
                break

            # Take the longest match; each length uses its nearest occurrence
            token_size = 0
            token_start = -1
            for length in range(LZ77_MIN_MATCH, LZ77_MAX_MATCH + 1):
                start = _find_match(data, offset, length)
                if start < 0:
                    break
                token_size = length
                token_start = start

            if token_size:
                distance = offset - token_start - 1
                out.append(((token_size - LZ77_MIN_MATCH) << 4) | (distance >> 8))
                out.append(distance & 0xFF)
                flags |= 0x80 >> bit
                offset += token_size
            else:
                out.append(data[offset])
                offset += 1

        out[flag_position] = flags

    # Pad so the total length is 4-byte aligned
    out += bytes(-len(out) % 4)
    return bytes(out)


def gba_lz77_compress_list(data: list[Union[str, int]]) -> bytes:
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

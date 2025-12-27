#include <cstdint>
#include <cstddef>
#include <cstdint>
#include <cstddef>
#include <cstdlib>   // malloc, free
#include <cstring>   // memcpy

// Negative return codes (ctypes-friendly)
static constexpr ptrdiff_t LZ77_E_BADARGS = -1;
static constexpr ptrdiff_t LZ77_E_DSTFULL = -3;

/* ====== ORIGINAL LOGIC (unchanged except signature types) ====== */

static int findTokenWithLength(uint8_t* buffer, size_t offset, size_t inputLength, int length)
{
    if (offset + (size_t)length > inputLength)
        return 0;

    // NOTE: this intentionally matches your original code's behavior,
    // including its "start at offset-8" and backward scan order.
    for (uint8_t* ptr = buffer + offset - 8; ptr >= buffer; ptr--)
    {
        int delta = (int)(ptr - buffer) - (int)offset;

        int encodedDelta = -delta - 1;
        if (encodedDelta > 0xFFF)
            return 0;

        bool match = true;
        for (int i = 0; i < length && match; ++i)
        {
            if (ptr[i] != buffer[offset + (size_t)i])
                match = false;
        }
        if (match)
            return delta;
    }

    return 0;
}

/* ====== ONLY NEW CODE: in-memory writer helpers ====== */

static inline bool put_u8(uint8_t* out, size_t out_cap, size_t& o, uint8_t v)
{
    if (o >= out_cap) return false;
    out[o++] = v;
    return true;
}

static inline bool put_u32_le(uint8_t* out, size_t out_cap, size_t& o, uint32_t v)
{
    return put_u8(out, out_cap, o, (uint8_t)(v & 0xFF)) &&
           put_u8(out, out_cap, o, (uint8_t)((v >> 8) & 0xFF)) &&
           put_u8(out, out_cap, o, (uint8_t)((v >> 16) & 0xFF)) &&
           put_u8(out, out_cap, o, (uint8_t)((v >> 24) & 0xFF));
}

/* ====== EXPORTED API ====== */

extern "C" {

// Same allocation idea as your tool: inputLength*2 + header + padding
size_t GBA_LZ77CompressBound(size_t inputLength)
{
    return 4 + (inputLength * 2) + 3;
}

/*
 * Exactly your compressor, except:
 * - input is passed as pointer/length (no file I/O)
 * - output is written to out buffer (no file I/O)
 * - returns total bytes written (INCLUDING the 4-byte header and padding)
 *
 * Output format is BIOS-compatible:
 *   u32 little-endian: (inputLength << 8) | 0x10
 *   then LZ77 blocks exactly like your tool writes
 */
ptrdiff_t GBA_LZ77Compress(const uint8_t* in, size_t inputLength,
                           uint8_t* out, size_t out_cap)
{
    if ((!in && inputLength) || (!out && out_cap)) return LZ77_E_BADARGS;

    // Your original uses a writable srcBuffer. We must preserve that to avoid changing anything.
    // We'll copy input into a temporary local buffer if needed.
    // To minimize changes, we create a mutable copy.
    // NOTE: This uses stack for small inputs; for large, consider a caller-provided scratch buffer.
    uint8_t* srcBuffer = (uint8_t*)malloc(inputLength);
    if (!srcBuffer && inputLength) return LZ77_E_BADARGS;
    if (inputLength) memcpy(srcBuffer, in, inputLength);

    // Output writing
    size_t bytesWritten = 0;

    // Header identical to: io::writeU32(fhOut, (inputLength << 8) | 0x10);
    uint32_t header = ((uint32_t)inputLength << 8) | 0x10u;
    if (!put_u32_le(out, out_cap, bytesWritten, header)) {
        free(srcBuffer);
        return LZ77_E_DSTFULL;
    }

    size_t inputBytesProcessed = 0;
    size_t lastFlagPosition = 0;
    int numFlagBits = 0;
    uint8_t flags = 0;

    while (inputBytesProcessed < inputLength)
    {
        if (numFlagBits == 0)
        {
            // Your original wrote placeholder 0x37 then overwrote it.
            // Placeholder value does not matter; we keep it identical.
            lastFlagPosition = bytesWritten;
            if (!put_u8(out, out_cap, bytesWritten, 0x37)) {
                free(srcBuffer);
                return LZ77_E_DSTFULL;
            }
        }

        if (findTokenWithLength(srcBuffer, inputBytesProcessed, inputLength, 3))
        {
            int tokenSize = 0;
            int tokenDelta = 0;
            for (int attemptTokenSize = 3; attemptTokenSize <= 18; ++attemptTokenSize)
            {
                int attemptTokenDelta = findTokenWithLength(srcBuffer, inputBytesProcessed, inputLength, attemptTokenSize);
                if (attemptTokenDelta != 0) {
                    tokenSize = attemptTokenSize;
                    tokenDelta = attemptTokenDelta;
                } else {
                    break;
                }
            }

            int flippedTokenDelta = -tokenDelta - 1;

            uint8_t b1 = (uint8_t)((((tokenSize - 3) & 0xf) << 4) | ((flippedTokenDelta & 0xf00) >> 8));
            uint8_t b2 = (uint8_t)(flippedTokenDelta & 0xff);

            if (!put_u8(out, out_cap, bytesWritten, b1) ||
                !put_u8(out, out_cap, bytesWritten, b2)) {
                free(srcBuffer);
                return LZ77_E_DSTFULL;
            }

            inputBytesProcessed += (size_t)tokenSize;
            flags |= (uint8_t)(0x80 >> numFlagBits);
        }
        else
        {
            if (!put_u8(out, out_cap, bytesWritten, srcBuffer[inputBytesProcessed])) {
                free(srcBuffer);
                return LZ77_E_DSTFULL;
            }
            inputBytesProcessed++;
        }

        numFlagBits++;
        if (numFlagBits == 8 || inputBytesProcessed >= inputLength) {
            numFlagBits = 0;
            out[lastFlagPosition] = flags;
            flags = 0;
        }
    }

    // Your original pads BYTES WRITTEN (payload) to 4 before writing.
    // Here bytesWritten includes the header too; to keep identical payload padding behavior,
    // pad so that TOTAL LENGTH is 4-aligned as well.
    while ((bytesWritten % 4) != 0) {
        if (!put_u8(out, out_cap, bytesWritten, 0x00)) {
            free(srcBuffer);
            return LZ77_E_DSTFULL;
        }
    }

    free(srcBuffer);
    return (ptrdiff_t)bytesWritten;
}

} // extern "C"

// Sprite3 on Sprite3 Palette; Compressed with LZ77
#pragma once

//======================================================================
//	Sprite3, 64pxl by 32pxl @ 4bpp
//	+ Number of Tiles : 32
//	+ Metatile Shape  : 4w by 4h
//	+ Dimensions in MT: 2w by 1h
//	+ Compressed number of bytes   : 396
//	+ Decompressed number of bytes : 1024
//	+ Blank Color     : 0x5d53
//	2026-01-22 18:57:20.156680
//======================================================================

/**
 * @brief The number of bytes Sprite3 occupies. 
 * 
 */
#define Sprite3Len 1024

/**
 * @brief The number of bytes in the compression stream for Sprite3. 
 * 
 */
#define Sprite3CompressedLen 396

/**
 * @brief The byte stream to decompress Sprite3 to tile data. 
 * 
 */
extern const unsigned char Sprite3Compression[396];

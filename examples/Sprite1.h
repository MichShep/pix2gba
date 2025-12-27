// Sprite1 on Sprite1_pal Palette Compressed with LZ77
#pragma once

//======================================================================
//	Sprite1, 64pxl by 32pxl @ 4bpp
//	+ Number of Tiles : 32
//	+ Metatile Shape  : 4w by 4h
//	+ Dimensions in MT: 2w by 1h
//	+ Compressed number of bytes   : 344
//	+ Decompressed number of bytes : 1024
//	+ Blank Color     : 0x5d53
//	2026-01-11 11:42:06.275180
//======================================================================

/**
 * @brief The number of bytes Sprite1 occupies. 
 * 
 */
#define Sprite1Len 1024

/**
 * @brief The number of bytes in the compression stream for Sprite1. 
 * 
 */
#define Sprite1CompressedLen 344

/**
 * @brief The byte stream to decompress Sprite1 to tile data. 
 * 
 */
extern const unsigned char Sprite1Compression[344];

/**
 * @brief The number of bytes the Palette for Sprite1 occupies. 
 * 
 */
#define Sprite1PalLen 32

/**
 * @brief The array of rgb5 (short) numbers that create Sprite1's Palette. 
 */
extern const unsigned short Sprite1Pal[16];

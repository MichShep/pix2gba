// Sprite8 on Sprite8 Palette; Compressed with LZ77
#pragma once

//======================================================================
//	Sprite8, 64pxl by 32pxl @ 4bpp
//	+ Number of Tiles : 32
//	+ Metatile Shape  : 4w by 4h
//	+ Dimensions in MT: 2w by 1h
//	+ Compressed number of bytes   : 344
//	+ Decompressed number of bytes : 1024
//	+ Blank Color     : 0x5d53
//	2026-03-12 15:57:29.599029
//======================================================================

/**
 * @brief The number of bytes Sprite8 occupies. 
 * 
 */
#define Sprite8Len 1024

/**
 * @brief The number of bytes in the compression stream for Sprite8. 
 * 
 */
#define Sprite8CompressedLen 344

/**
 * @brief The byte stream to decompress Sprite8 to tile data. 
 * 
 */
extern const unsigned char Sprite8Compression[344];

/**
 * @brief The number of bytes the Palette for Sprite8 occupies. 
 * 
 */
#define Sprite8PalLen 18

/**
 * @brief The array of rgb5 (short) numbers that create Sprite8's Palette. 
 */
extern const unsigned short Sprite8Pal[9];

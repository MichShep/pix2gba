// Sprite8; Compressed
#pragma once

//======================================================================
//	Sprite8, 64pxl by 32pxl @ 4bpp
//	+ Number of Tiles : 32
//	+ Metatile Shape  : 4w by 4h
//	+ Dimensions in MT: 2w by 1h
//	+ Number of Bytes : 1024 -> 344 (compressed)
//	+ Number of U32   : 256
//	+ Blank Color     : 0x5d53
//======================================================================

/**
 * @brief The number of tiles to make Sprite8. 
 * 
 */
#define Sprite8_TILE_COUNT 32

/**
 * @brief The number of bytes Sprite8 occupies. 
 * 
 */
#define Sprite8_TILE_BYTES 1024

/**
 * @brief The number of bytes in the compression stream for Sprite8. 
 * 
 */
#define Sprite8_COMPRESSION_LEN 344

/**
 * @brief The byte stream to decompress Sprite8 to tile data. 
 * 
 */
extern const unsigned char Sprite8_COMPRESSION[344];

/**
 * @brief The number of bytes the Palette for Sprite8 occupies. 
 * 
 */
#define Sprite8_PAL_LEN 18

/**
 * @brief The array of rgb5 (short) numbers that create Sprite8's Palette. 
 */
extern const unsigned short Sprite8_PAL[9];

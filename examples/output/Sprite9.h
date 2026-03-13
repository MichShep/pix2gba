// Sprite9; Deduped; Compressed
#pragma once

//======================================================================
//	Sprite9, 240pxl by 160pxl @ 4bpp
//	+ Number of Tiles : 600 -> 110 (deduped)
//	+ Metatile Shape  : 1w by 1h
//	+ Dimensions in MT: 30w by 20h
//	+ Number of Bytes : 3520 -> 1024 (compressed)
//	+ Number of U32   : 880
//	+ Blank Color     : 0x5d53
//======================================================================

/**
 * @brief The number of tiles to make Sprite9. 
 * 
 */
#define Sprite9_TILE_COUNT 600

/**
 * @brief The number of bytes Sprite9 occupies. 
 * 
 */
#define Sprite9_TILE_BYTES 3520

/**
 * @brief The number of bytes in the compression stream for Sprite9. 
 * 
 */
#define Sprite9_COMPRESSION_LEN 1024

/**
 * @brief The byte stream to decompress Sprite9 to tile data. 
 * 
 */
extern const unsigned char Sprite9_COMPRESSION_LEN[1024];

/**
 * @brief The array of Tile indices to create Sprite9 from other Tiles after deduping. 
 * 
 */
extern const unsigned short Sprite9_TILE_MAPPING[600];

/**
 * @brief The number of bytes the Palette for Sprite9 occupies. 
 * 
 */
#define Sprite9_PAL_LEN 26

/**
 * @brief The array of rgb5 (short) numbers that create Sprite9's Palette. 
 */
extern const unsigned short Sprite9_PAL[13];

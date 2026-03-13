// Sprite5; Deduped
#pragma once

//======================================================================
//	Sprite5, 96pxl by 16pxl @ 4bpp
//	+ Number of Tiles : 24 -> 13 (deduped)
//	+ Metatile Shape  : 4w by 2h
//	+ Dimensions in MT: 3w by 1h
//	+ Number of Bytes : 416
//	+ Number of U32   : 104
//	+ Blank Color     : 0x5d53
//======================================================================

/**
 * @brief The number of tiles to make Sprite5. 
 * 
 */
#define Sprite5_TILE_COUNT 24

/**
 * @brief The number of bytes Sprite5 occupies. 
 * 
 */
#define Sprite5_TILE_BYTES 416

/**
 * @brief The array of Palette indices (4 packed into one uint) to create Sprite5 in Tiles. 
 * 
 */
extern const unsigned int Sprite5_TILES[104];

/**
 * @brief The array of Tile indices to create Sprite5 from other Tiles after deduping. 
 * 
 */
extern const unsigned short Sprite5_TILE_MAPPING[24];

/**
 * @brief The number of bytes the Palette for Sprite5 occupies. 
 * 
 */
#define Sprite5_PAL_LEN 8

/**
 * @brief The array of rgb5 (short) numbers that create Sprite5's Palette. 
 */
extern const unsigned short Sprite5_PAL[4];

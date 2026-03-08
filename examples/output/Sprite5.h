// Sprite5 on Sprite5 Palette; Deduped
#pragma once

//======================================================================
//	Sprite5, 96pxl by 16pxl @ 4bpp
//	+ Number of Tiles : 24
//	+ Metatile Shape  : 4w by 2h
//	+ Dimensions in MT: 3w by 1h
//	+ Number of Bytes : 768
//	+ Number of U32   : 192
//	+ Blank Color     : 0x5d53
//	2026-03-08 04:18:41.208535
//======================================================================

/**
 * @brief The number of tiles to make Sprite5. 
 * 
 */
#define Sprite5TileAmount 24

/**
 * @brief The number of bytes Sprite5 occupies. 
 * 
 */
#define Sprite5TilesLen 768

/**
 * @brief The array of Palette indices (4 packed into one uint) to create Sprite5 in Tiles. 
 * 
 */
extern const unsigned int Sprite5Tiles[192];

/**
 * @brief The array of Tile indices to create Sprite5 from other Tiles after deduping. 
 * 
 */
extern const unsigned int Sprite5TileMapping[24];

/**
 * @brief The number of bytes the Palette for Sprite5 occupies. 
 * 
 */
#define Sprite5PalLen 8

/**
 * @brief The array of rgb5 (short) numbers that create Sprite5's Palette. 
 */
extern const unsigned short Sprite5Pal[4];

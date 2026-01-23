// Sprite1 on Sprite1_pal Palette; Deduped
#pragma once

//======================================================================
//	Sprite1, 96pxl by 16pxl @ 4bpp
//	+ Number of Tiles : 24
//	+ Metatile Shape  : 4w by 2h
//	+ Dimensions in MT: 3w by 1h
//	+ Number of Bytes : 768
//	+ Number of U32   : 192
//	+ Blank Color     : 0x5d53
//	2026-01-22 18:57:20.150737
//======================================================================

/**
 * @brief The number of tiles to make Sprite1. 
 * 
 */
#define Sprite1TileAmount 24

/**
 * @brief The number of bytes Sprite1 occupies. 
 * 
 */
#define Sprite1TilesLen 768

/**
 * @brief The array of Palette indices (4 packed into one uint) to create Sprite1 in Tiles. 
 * 
 */
extern const unsigned int Sprite1Tiles[192];

/**
 * @brief The array of Tile indices to create Sprite1 from other Tiles after deduping. 
 * 
 */
extern const unsigned int Sprite1TileMapping[24];

/**
 * @brief The number of bytes the Palette for Sprite1 occupies. 
 * 
 */
#define Sprite1PalLen 32

/**
 * @brief The array of rgb5 (short) numbers that create Sprite1's Palette. 
 */
extern const unsigned short Sprite1Pal[16];

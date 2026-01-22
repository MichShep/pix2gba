// Sprite3 on Sprite3 Palette; Deduped
#pragma once

//======================================================================
//	Sprite3, 64pxl by 32pxl @ 4bpp
//	+ Number of Tiles : 32
//	+ Metatile Shape  : 4w by 4h
//	+ Dimensions in MT: 2w by 1h
//	+ Number of Bytes : 1024
//	+ Number of U32   : 256
//	+ Blank Color     : 0x5d53
//	2026-01-22 17:36:13.786759
//======================================================================

/**
 * @brief The number of tiles to make Sprite3. 
 * 
 */
#define Sprite3TileAmount 32

/**
 * @brief The number of bytes Sprite3 occupies. 
 * 
 */
#define Sprite3TilesLen 1024

/**
 * @brief The array of Palette indices (4 packed into one uint) to create Sprite3 in Tiles. 
 * 
 */
extern const unsigned int Sprite3Tiles[256];

/**
 * @brief The array of Tile indices to create Sprite3 from other Tiles after deduping. 
 * 
 */
extern const unsigned int Sprite3TileMapping[32];

/**
 * @brief The number of bytes the Palette for Sprite3 occupies. 
 * 
 */
#define Sprite3PalLen 24

/**
 * @brief The array of rgb5 (short) numbers that create Sprite3's Palette. 
 */
extern const unsigned short Sprite3Pal[12];

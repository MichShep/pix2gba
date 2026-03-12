// Sprite6 on Sprite6_palette Palette
#pragma once

//======================================================================
//	Sprite6, 64pxl by 32pxl @ 4bpp
//	+ Number of Tiles : 32
//	+ Metatile Shape  : 4w by 4h
//	+ Dimensions in MT: 2w by 1h
//	+ Number of Bytes : 1024
//	+ Number of U32   : 256
//	+ Blank Color     : 0x5d53
//	2026-03-08 04:18:41.320737
//======================================================================

/**
 * @brief The number of tiles to make Sprite6. 
 * 
 */
#define Sprite6TileAmount 32

/**
 * @brief The number of bytes Sprite6 occupies. 
 * 
 */
#define Sprite6TilesLen 1024

/**
 * @brief The array of Palette indices (4 packed into one uint) to create Sprite6 in Tiles. 
 * 
 */
extern const unsigned int Sprite6Tiles[256];

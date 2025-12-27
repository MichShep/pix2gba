// Sprite3 on Sprite3 Palette
#pragma once

//======================================================================
//	Sprite3, 64pxl by 32pxl @ 4bpp
//	+ Number of Tiles : 32
//	+ Metatile Shape  : 4w by 4h
//	+ Dimensions in MT: 2w by 1h
//	+ Number of Bytes : 1024
//	+ Number of U32   : 256
//	+ Blank Color     : 0x5d53
//	2026-01-11 11:42:06.277520
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

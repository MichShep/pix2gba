// Sprite4; on palette Palette2.png
#pragma once

//======================================================================
//	Sprite4, 64pxl by 32pxl @ 4bpp
//	+ Number of Tiles : 32
//	+ Metatile Shape  : 4w by 4h
//	+ Dimensions in MT: 2w by 1h
//	+ Number of Bytes : 1024
//	+ Number of U32   : 256
//	+ Blank Color     : 0x5d53
//======================================================================

/**
 * @brief The number of tiles to make Sprite4. 
 * 
 */
#define Sprite4_TILE_COUNT 32

/**
 * @brief The number of bytes Sprite4 occupies. 
 * 
 */
#define Sprite4_TILE_BYTES 1024

/**
 * @brief The array of Palette indices (4 packed into one uint) to create Sprite4 in Tiles. 
 * 
 */
extern const unsigned int Sprite4_TILES[256];

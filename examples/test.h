// test on test Palette
#pragma once

//======================================================================
//	test, 200pxl by 200pxl @ 4bpp
//	+ Number of Tiles : 625
//	+ Metatile Shape  : 1w by 1h
//	+ Dimensions in MT: 25w by 25h
//	+ Number of Bytes : 20000
//	+ Number of U32   : 5000
//	+ Blank Color     : 0x5d53
//	2025-12-12 00:37:17.893529
//======================================================================

/**
 * @brief The number of tiles to make test. 
 * 
 */
#define testTileAmount 625

/**
 * @brief The number of bytes test occupies. 
 * 
 */
#define testTilesLen 20000

/**
 * @brief The array of Palette indices (4 packed into one uint) to create test in Tiles. 
 * 
 */
extern const unsigned int testTiles[5000];

/**
 * @brief The number of bytes the Palette for test occupies. 
 * 
 */
#define testPalLen 32

/**
 * @brief The array of rgb5 (short) numbers that create test's Palette. 
 */
extern const unsigned short testPal[16];

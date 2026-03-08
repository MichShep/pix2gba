// InventoryBackground on InventoryBackground Palette; Deduped
#pragma once

//======================================================================
//	InventoryBackground, 240pxl by 160pxl @ 4bpp
//	+ Number of Tiles : 600
//	+ Metatile Shape  : 1w by 1h
//	+ Dimensions in MT: 30w by 20h
//	+ Number of Bytes : 19200
//	+ Number of U32   : 4800
//	+ Blank Color     : 0x5d53
//	2026-03-08 04:18:41.313700
//======================================================================

/**
 * @brief The number of tiles to make InventoryBackground. 
 * 
 */
#define InventoryBackgroundTileAmount 600

/**
 * @brief The number of bytes InventoryBackground occupies. 
 * 
 */
#define InventoryBackgroundTilesLen 19200

/**
 * @brief The array of Palette indices (4 packed into one uint) to create InventoryBackground in Tiles. 
 * 
 */
extern const unsigned int InventoryBackgroundTiles[4800];

/**
 * @brief The array of Tile indices to create InventoryBackground from other Tiles after deduping. 
 * 
 */
extern const unsigned int InventoryBackgroundTileMapping[600];

/**
 * @brief The number of bytes the Palette for InventoryBackground occupies. 
 * 
 */
#define InventoryBackgroundPalLen 26

/**
 * @brief The array of rgb5 (short) numbers that create InventoryBackground's Palette. 
 */
extern const unsigned short InventoryBackgroundPal[13];

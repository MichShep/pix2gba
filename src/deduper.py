def _hash_list(l: list):
    result = 17
    for i in range(len(l)):
        result = result * 31 + l[i]
    return result


def _compare_lists(l1: list, l2: list) -> bool:
    """
    Checks if two lists contain identical values
    """
    if len(l1) != len(l2):
        return False

    for i in range(len(l1)):
        if l1[i] != l2[i]:
            return False

    return True


def dedupe_tiles(hex_list: list, bpp: int) -> dict:

    # 1. Convert hex strings to ints
    int_list = [int(h, 16) for h in hex_list]

    # 2. Split stream into tiles
    tile_size = 2 * bpp
    tile_list = []

    for i in range(0, len(int_list), tile_size):
        tile_list.append(int_list[i:i + tile_size])

    # 3. Hash all tiles
    hash_list = [_hash_list(tile) for tile in tile_list]

    # 4. Deduplicate using hash buckets
    lookup_table = {}   # hash -> list of tile indices
    unique_tile_ids = []  # stores the original tile index of each unique tile
    tile_mapping = []   # maps each tile to its unique tile index

    for i in range(len(tile_list)):
        entry = hash_list[i]

        if entry not in lookup_table:
            lookup_table[entry] = [i]
            unique_tile_ids.append(i)
            tile_mapping.append(len(unique_tile_ids) - 1)

        else:
            found_match = False

            for index in lookup_table[entry]:
                if _compare_lists(tile_list[i], tile_list[index]):
                    found_match = True
                    unique_index = unique_tile_ids.index(index)
                    tile_mapping.append(unique_index)
                    break

            if not found_match:
                lookup_table[entry].append(i)
                unique_tile_ids.append(i)
                tile_mapping.append(len(unique_tile_ids) - 1)


    # 5. Build final tile list
    final_list = []

    for tile_id in unique_tile_ids:
        final_list.extend(tile_list[tile_id])

    final_list = ["0x{:08x}".format(i) for i in final_list]

    output_dict = {
        "final_list": final_list,
        "tile_mapping": tile_mapping,
        "unique_tile_count": len(unique_tile_ids)
    }

    return output_dict

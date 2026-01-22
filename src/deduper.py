
def _hash_list(l: list):
    result = 17
    for i in range(len(l)):
        result = result * 31 + l[i]

    return result

def _compare_lists(l1: list, l2: list)-> bool:
    """
    Checks if two lists are the same value wise
    :param l1: List 1
    :param l2: List 2
    :return: True if the same, False is different
    """
    for i in range(len(l1)):
        if l1[i] != l2[i]:
            return False

    return True

def dedupe_tiles(hex_list: list, bpp: int)-> tuple[list[hex], list[int]]:
    print(" \t Deduping...")
    # 1. Split of stream of hex to tile
    int_list = [int(h, 16) for h in hex_list]

    tile_list = []
    hex_tile_list = []
    temp_tile = []
    for i in range(len(int_list)):
        if i % (2*bpp) == 0 and i != 0:
            tile_list.append(temp_tile)
            temp_tile = []

        temp_tile.append(int_list[i])
    tile_list.append(temp_tile)

    # 2. Hash all tiles into single value
    hash_list = [_hash_list(l) for l in tile_list]

    # 3. Compare the values and eliminate duplicates and create tile mapping
    tile_mapping = []
    lookup_table = {}
    for i in range(len(hash_list)):
        entry = hash_list[i]
        # If not in the lut then is a unique entry
        if entry not in lookup_table:
            lookup_table[entry] = [i]
            tile_mapping.append(i)
        # If there is a collision, compare with all in that bucket for uniqueness
        else:
            found_match = False
            for index in lookup_table[entry]:
                # If the current list matches one in the bucket then isn't unique
                if _compare_lists(tile_list[i], tile_list[index]):
                    found_match = True
                    tile_mapping.append(index)
                    break

            # If here then the list is unique to all others in the hash
            if not found_match:
                lookup_table[entry].append(i)
                tile_mapping.append(i)


    print(f" \t\t Deduped from {len(tile_list)} to {len(lookup_table.values())} tiles!")

    # 4. Go through each kept tile and add data to final array
    final_list = []
    for entry in lookup_table.values():
        for tile_id in entry:
            final_list.extend(tile_list[tile_id])

    final_list = [hex(i) for i in final_list]

    return final_list, tile_mapping
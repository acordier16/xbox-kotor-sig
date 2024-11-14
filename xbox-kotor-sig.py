import hmac
import hashlib
import os
import argparse

def read_file_bytes(file_path: str, start: int = 0, end: int = None):
    with open(file_path, 'rb') as file:
        file.seek(start)
        if end is None: # Read the rest of the file
            return file.read()
        else: # Read the specified portion of the file
            length = end - start
            return file.read(length)

def read_file_hex(file_path: str, start: int = 0, end: int = None):
    return read_file_bytes(file_path, start, end).hex()

def hash_with_key(data: bytes, key: bytes):
    hmac_obj = hmac.new(key, digestmod=hashlib.sha1)
    hmac_obj.update(data)
    return hmac_obj.hexdigest()

def bytes_to_int(byte_sequence: bytes, byte_order: str = 'little'):
    return int.from_bytes(byte_sequence, byte_order)

def __main__(core_path: str):

    auth_key = bytes([0x07, 0xDF, 0x71, 0xE6, 0xB1, 0xFB, 0x1C, 0x82, 0x78, 0x26, 0x68, 0x3C, 0x2A, 0x48, 0x42, 0xD3]) # V1 KOTOR
    # auth_key = bytes([0x67,0x77,0x01,0x4b,0xb4,0xad,0xe4,0x21,0x8b,0x3d,0x98,0x67,0xa8,0xba,0x76,0x3c]) # V2 (KOTOR 2?)

    # Signing: Screen.tga, PARTYTABLE.res, GLOBALVARS.res, savenfo.res
    screen = read_file_bytes(os.path.join(core_path, "Screen.tga"))
    partytable = read_file_bytes(os.path.join(core_path, "PARTYTABLE.res"))
    globalvars = read_file_bytes(os.path.join(core_path, "GLOBALVARS.res"))
    savenfo = read_file_bytes(os.path.join(core_path, "savenfo.res"))

    screen_sig = hash_with_key(screen, auth_key)
    partytable_sig = hash_with_key(partytable, auth_key)
    globalvars_sig = hash_with_key(globalvars, auth_key)
    savenfo_sig = hash_with_key(savenfo, auth_key)

    # Signing: SAVEGAME.sav

    # Information from :
    # https://github.com/nadrino/kotor-savegame-editor/blob/main/old/kse_337.pl#L2477
    # First SAVEGAME.sav 44 bytes = 11 variables of 4 bytes
    # - sig (0 -> 4)
    # - version (4 -> 8)
    # - localized_string_count (8 -> 12)
    # - localized_string_size (12 -> 16)
    # - entry_count (16 -> 20)
    # - offset_to_localized_string (20 -> 24)
    # - offset_to_key_list (24 -> 28)
    # - offset_to_resource_list (28 -> 32)
    # - build_year (32 -> 36)
    # - build_day (36 -> 40)
    # - description_str_ref (40 -> 44)

    entry_count = bytes_to_int(read_file_bytes(os.path.join(core_path, "SAVEGAME.sav"), start=16, end=16+4))
    offset_to_resource_list = bytes_to_int(read_file_bytes(os.path.join(core_path, "SAVEGAME.sav"), start=28, end=28+4))
    header_vars_size = offset_to_resource_list + (8 * entry_count) - 160

    # Split SAVEGAME.sav into 3 sections:
    # 0 -> 160 bytes = HEADER
    # 160 -> X = HEADER_VARS
    # X -> END = DATA

    savegame_header = read_file_bytes(os.path.join(core_path, "SAVEGAME.sav"), start=0, end=160)
    savegame_header_vars = read_file_bytes(os.path.join(core_path, "SAVEGAME.sav"), start=160, end=160+header_vars_size)
    savegame_data = read_file_bytes(os.path.join(core_path, "SAVEGAME.sav"), start=160+header_vars_size, end=None)

    savegame_header_vars_sig = hash_with_key(savegame_header_vars, auth_key)
    savegame_data_sig = hash_with_key(savegame_data, auth_key)

    # Compute total SAVEGAME.sav filesize
    file_size = os.path.getsize(os.path.join(core_path, "SAVEGAME.sav"))
    # Convert filesize to bytes
    file_size_bytes = file_size.to_bytes(4, 'little')
    # Concatenate header of SAVEGAME.sav with the filesize
    savegame_header_with_size = savegame_header + file_size_bytes
    # Hash
    savegame_header_sig = hash_with_key(savegame_header_with_size, auth_key)

    signatures = {
        "Screen.sig": screen_sig,
        "SAVE_PARTY.sig": partytable_sig,
        "SAVE_VARS.sig": globalvars_sig,
        "SAVE_INFO.sig": savenfo_sig,
        "SAVE_HEADER.sig": savegame_header_sig,
        "SAVE_HEADERVAR.sig": savegame_header_vars_sig,
        "SAVE_DATA.sig": savegame_data_sig
    }

    # Print signatures
    print("Computed sig files:")
    for sig_filename, sig in signatures.items():
        print(f"- {sig_filename} ({sig})")

    # Ask user to save the signatures to disk
    save_choice = input("\nDo you want to save the sig files to disk in the save folder?\nWARNING: this will overwrite existing sig files if any. (Y/N): ").strip().lower()
    if save_choice == 'y':
        for filename, signature in signatures.items():
            file_path = os.path.join(core_path, filename)
            with open(file_path, 'wb') as sig_file:
                sig_file.write(bytes.fromhex(signature))
            print(f"Saved {filename} in {core_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and sign KOTOR save files in a specified core_path directory.")
    parser.add_argument("core_path", type=str, help="The path to the folder containing the KOTOR save files")
    args = parser.parse_args()

    __main__(args.core_path)

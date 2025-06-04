import wcs # This assumes the compiled Rust module is in the Python path

def test_bincode():
    # Sample WCS parameters dictionary
    wcs_dict_initial = {
        "NAXIS": 2,
        "NAXIS1": 1024,
        "NAXIS2": 512,
        "CTYPE1": "RA---TAN",
        "CTYPE2": "DEC--TAN",
        "CRVAL1": 150.0,
        "CRVAL2": 2.0,
        "CRPIX1": 512.5,
        "CRPIX2": 256.5,
        "CDELT1": -0.001,
        "CDELT2": 0.001,
        "RADESYS": "ICRS",
        # Add a few more optional parameters to ensure they are handled
        "LONPOLE": 180.0,
        "LATPOLE": 0.0,
        "EQUINOX": 2000.0,
    }

    print("Initial WCS Dictionary:")
    # Print sorted dict for consistent output if needed for manual comparison
    for k, v in sorted(wcs_dict_initial.items()):
        print(f"  {k}: {v}")
    print("-" * 30)

    # 1. Create WCSParams from Python dictionary
    try:
        params_original = wcs.WCSParams(wcs_dict_initial)
        print("Successfully created WCSParams from dict (params_original).")
    except Exception as e:
        print(f"Error creating WCSParams from dict: {e}")
        return

    # 2. Serialize to Python bytes
    try:
        py_bytes = params_original.to_bytes()
        print(f"Successfully serialized to bytes. Byte length: {len(py_bytes)}")
        # print(f"Bytes (first 50): {py_bytes[:50]}") # Optional: print some bytes
    except Exception as e:
        print(f"Error serializing WCSParams to bytes: {e}")
        return
    print("-" * 30)

    # 3. Deserialize from Python bytes
    try:
        params_deserialized = wcs.WCSParams.from_bytes(py_bytes)
        print("Successfully deserialized WCSParams from bytes (params_deserialized).")
    except Exception as e:
        print(f"Error deserializing WCSParams from bytes: {e}")
        return
    print("-" * 30)

    # 4. Convert back to dictionaries and compare
    try:
        dict_original = params_original.to_dict()
        dict_deserialized = params_deserialized.to_dict()
        print("Converted both instances back to dictionaries.")
    except Exception as e:
        print(f"Error converting WCSParams back to dict: {e}")
        return

    # Normalize dictionaries for comparison (e.g. handle None vs missing keys if necessary, though to_dict should be consistent)
    # For this test, we expect them to be identical including key presence.
    
    print("\nOriginal Dictionary (from params_original.to_dict()):")
    for k, v in sorted(dict_original.items()):
        print(f"  {k}: {v}")
        
    print("\nDeserialized Dictionary (from params_deserialized.to_dict()):")
    for k, v in sorted(dict_deserialized.items()):
        print(f"  {k}: {v}")

    if dict_original == dict_deserialized:
        print("\nSUCCESS: Original and deserialized dictionaries are identical.")
    else:
        print("\nFAILURE: Dictionaries do not match.")
        # Find differences
        all_keys = set(dict_original.keys()) | set(dict_deserialized.keys())
        for k in sorted(list(all_keys)):
            v1 = dict_original.get(k)
            v2 = dict_deserialized.get(k)
            if v1 != v2:
                print(f"  Mismatch for key '{k}': original='{v1}', deserialized='{v2}'")


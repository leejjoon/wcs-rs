import timeit
from wcs import WCSParams # PyWCSParams is exposed as WCSParams in Python

# Sample WCS data (same as in test_bincode_wcs_params.py)
initial_wcs_dict = {
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
    "LONPOLE": 180.0,
    "LATPOLE": 0.0,
    "EQUINOX": 2000.0,
    "RADESYS": "ICRS",
}

# Number of repetitions for timeit
REPEATS = 10000

print(f"Benchmarking WCSParams serialization/deserialization ({REPEATS} repeats each)...")

# --- Setup for benchmarks ---
# Create an initial instance for serialization tests
params_instance = WCSParams(initial_wcs_dict)
# Serialize to bytes once for deserialization test
serialized_bytes = params_instance.to_bytes()
# Serialize to dict once for from_dict (constructor) test setup
# (though the constructor itself is what we're testing for 'from_dict')

# --- Benchmark: Construction from dictionary ---
setup_code_from_dict = '''
from wcs import WCSParams
initial_wcs_dict = {
    "NAXIS": 2, "NAXIS1": 1024, "NAXIS2": 512, "CTYPE1": "RA---TAN",
    "CTYPE2": "DEC--TAN", "CRVAL1": 150.0, "CRVAL2": 2.0, "CRPIX1": 512.5,
    "CRPIX2": 256.5, "CDELT1": -0.001, "CDELT2": 0.001, "LONPOLE": 180.0,
    "LATPOLE": 0.0, "EQUINOX": 2000.0, "RADESYS": "ICRS"
}
'''
stmt_from_dict = "WCSParams(initial_wcs_dict)"
time_from_dict = timeit.timeit(stmt_from_dict, setup=setup_code_from_dict, number=REPEATS)
print(f"1. From Dict (Constructor): {time_from_dict:.6f} seconds")

# --- Benchmark: Serialization to dictionary ---
setup_code_to_dict = '''
from wcs import WCSParams
initial_wcs_dict = {
    "NAXIS": 2, "NAXIS1": 1024, "NAXIS2": 512, "CTYPE1": "RA---TAN",
    "CTYPE2": "DEC--TAN", "CRVAL1": 150.0, "CRVAL2": 2.0, "CRPIX1": 512.5,
    "CRPIX2": 256.5, "CDELT1": -0.001, "CDELT2": 0.001, "LONPOLE": 180.0,
    "LATPOLE": 0.0, "EQUINOX": 2000.0, "RADESYS": "ICRS"
}
params_instance = WCSParams(initial_wcs_dict)
'''
stmt_to_dict = "params_instance.to_dict()"
time_to_dict = timeit.timeit(stmt_to_dict, setup=setup_code_to_dict, number=REPEATS)
print(f"2. To Dict:                 {time_to_dict:.6f} seconds")

# --- Benchmark: Serialization to bytes ---
setup_code_to_bytes = setup_code_to_dict # Same setup as to_dict
stmt_to_bytes = "params_instance.to_bytes()"
time_to_bytes = timeit.timeit(stmt_to_bytes, setup=setup_code_to_bytes, number=REPEATS)
print(f"3. To Bytes (bincode):      {time_to_bytes:.6f} seconds")

# --- Benchmark: Deserialization from bytes ---
setup_code_from_bytes = '''
from wcs import WCSParams
initial_wcs_dict = {
    "NAXIS": 2, "NAXIS1": 1024, "NAXIS2": 512, "CTYPE1": "RA---TAN",
    "CTYPE2": "DEC--TAN", "CRVAL1": 150.0, "CRVAL2": 2.0, "CRPIX1": 512.5,
    "CRPIX2": 256.5, "CDELT1": -0.001, "CDELT2": 0.001, "LONPOLE": 180.0,
    "LATPOLE": 0.0, "EQUINOX": 2000.0, "RADESYS": "ICRS"
}
params_instance = WCSParams(initial_wcs_dict)
serialized_bytes = params_instance.to_bytes()
'''
stmt_from_bytes = "WCSParams.from_bytes(serialized_bytes)"
time_from_bytes = timeit.timeit(stmt_from_bytes, setup=setup_code_from_bytes, number=REPEATS)
print(f"4. From Bytes (bincode):    {time_from_bytes:.6f} seconds")

print("\n--- Comparison ---")
if time_to_bytes < time_to_dict:
    print(f"To Bytes is {time_to_dict / time_to_bytes:.2f}x faster than To Dict for serialization.")
else:
    print(f"To Dict is {time_to_bytes / time_to_dict:.2f}x faster than To Bytes for serialization.")

# Comparing from_bytes with constructor (from_dict)
if time_from_bytes < time_from_dict:
    print(f"From Bytes is {time_from_dict / time_from_bytes:.2f}x faster than From Dict for deserialization.")
else:
    print(f"From Dict is {time_from_bytes / time_from_dict:.2f}x faster than From Bytes for deserialization.")

# Round trip comparison
round_trip_dict_time = time_from_dict + time_to_dict
round_trip_bytes_time = time_to_bytes + time_from_bytes # Assuming construction time is separate

# More accurate round trip: create -> to_bytes -> from_bytes vs create -> to_dict -> from_dict(create)
# For bytes round trip: time_to_bytes + time_from_bytes
# For dict round trip: time_to_dict + time_from_dict (re-construction)

print(f"\nRound trip (Serialization + Deserialization):")
print(f"  Dict -> WCSParams -> Dict:  {time_to_dict + time_from_dict:.6f} seconds (using constructor time for 'from dict')")
print(f"  Dict -> WCSParams -> Bytes -> WCSParams: {time_to_bytes + time_from_bytes:.6f} seconds (bincode)")

if (time_to_bytes + time_from_bytes) < (time_to_dict + time_from_dict):
    factor = (time_to_dict + time_from_dict) / (time_to_bytes + time_from_bytes)
    print(f"Bincode round trip is {factor:.2f}x faster than dictionary round trip.")
else:
    factor = (time_to_bytes + time_from_bytes) / (time_to_dict + time_from_dict)
    print(f"Dictionary round trip is {factor:.2f}x faster than bincode round trip.")

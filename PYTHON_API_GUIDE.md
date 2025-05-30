## Python API Guide for WCS-rs

This guide explains how to use the Python wrapper for the `wcs-rs` library.

### 1. Building and Installation (for local development)

To use the Python module, you first need to build it from the Rust source code using Maturin.

1.  **Install Maturin and Pytest**:
    If you don't have them, install Maturin (for building) and pytest (for testing):
    ```bash
    pip install maturin pytest
    ```
2.  **Build and install the development version**:
    Navigate to the root directory of the `wcs-rs` crate and run:
    ```bash
    maturin develop
    ```
    This command builds the Rust code into a Python module and installs it in your current Python virtual environment.

    *(Note: If the `maturin develop` command fails due to environment issues, manual compilation might be needed, or a pre-built wheel if available.)*

### 2. Importing the Library

Once built and installed, you can import the necessary classes in your Python script:

```python
from wcs import WCSParams, WCS
```

### 3. Creating `WCSParams`

The `WCSParams` object holds the World Coordinate System parameters, typically derived from a FITS header. You create it from a Python dictionary.

*   **`WCSParams(params_dict: dict) -> WCSParams`**
    *   `params_dict`: A Python dictionary where keys are WCS parameter names (e.g., "NAXIS", "CTYPE1", "CRVAL1", "CD1_1") and values are their corresponding values (integers, floats, or strings as appropriate).

**Example:**

```python
params_data = {
    "NAXIS": 2,
    "CTYPE1": "RA---TAN",
    "CTYPE2": "DEC--TAN",
    "CRVAL1": 185.445488837,
    "CRVAL2": 4.47896032431,
    "CRPIX1": 588.995094299,
    "CRPIX2": 308.307905197,
    "CUNIT1": "deg",
    "CUNIT2": "deg",
    "CD1_1": -0.000223666022989,
    "CD1_2": -0.000296578064584,
    "CD2_1": -0.000296427555509,
    "CD2_2": 0.000223774308964,
    "NAXIS1": 1080,
    "NAXIS2": 705,
    # Add other necessary WCS keywords like EQUINOX, LONPOLE, LATPOLE if needed
    "EQUINOX": 2000.0,
    "LONPOLE": 180.0,
    # "LATPOLE": 0.0, # LATPOLE is optional in Rust WCSParams if not present
}

try:
    wcs_params = WCSParams(params_data)
except ValueError as e:
    print(f"Error creating WCSParams: {e}")
    # Handle error appropriately
```
If essential parameters are missing or incorrect in the dictionary (e.g., a missing `CTYPE1`), the `WCSParams` constructor will raise a `ValueError`.

### 4. Creating `WCS`

The `WCS` object performs the coordinate transformations. It's initialized with a `WCSParams` object.

*   **`WCS(params: WCSParams) -> WCS`**
    *   `params`: An instance of `WCSParams`.

**Example:**

```python
try:
    wcs_object = WCS(wcs_params)
except ValueError as e:
    print(f"Error creating WCS object: {e}")
    # Handle error appropriately
```
If the parameters in `WCSParams` are insufficient or inconsistent for initializing the WCS transformations (e.g., `NAXIS1` missing when `NAXIS` is 2), the `WCS` constructor will raise a `ValueError`.

### 5. Coordinate Projection

Projecting from world coordinates (longitude, latitude) to pixel coordinates (X, Y).

*   **`wcs_object.proj(lon: float, lat: float) -> Optional[Tuple[float, float]]`**
    *   `lon`: Longitude in **degrees**.
    *   `lat`: Latitude in **degrees**.
    *   Returns a tuple `(x, y)` representing pixel coordinates, or `None` if the projection fails (e.g., point is outside the valid projection domain).

**Example:**

```python
lon_deg = 185.445488837
lat_deg = 4.47896032431

pixel_coords = wcs_object.proj(lon_deg, lat_deg)
if pixel_coords:
    x, y = pixel_coords
    print(f"Projected pixel coordinates: X={x}, Y={y}")
else:
    print("Projection failed or point is outside domain.")
```

### 6. Coordinate Unprojection

Unprojecting from pixel coordinates (X, Y) to world coordinates (longitude, latitude).

*   **`wcs_object.unproj(x: float, y: float) -> Optional[Tuple[float, float]]`**
    *   `x`: X pixel coordinate.
    *   `y`: Y pixel coordinate.
    *   Returns a tuple `(lon, lat)` representing world coordinates in **degrees**, or `None` if the unprojection fails.

**Example:**

```python
x_pix = 588.995094299
y_pix = 308.307905197

world_coords = wcs_object.unproj(x_pix, y_pix)
if world_coords:
    lon, lat = world_coords
    print(f"Unprojected world coordinates: Lon={lon} deg, Lat={lat} deg")
else:
    print("Unprojection failed.")
```

### 7. Complete Example

```python
from wcs import WCSParams, WCS

# 1. Define WCS parameters
params_data = {
    "NAXIS": 2, "CTYPE1": "RA---TAN", "CTYPE2": "DEC--TAN",
    "CRVAL1": 185.445488837, "CRVAL2": 4.47896032431,
    "CRPIX1": 588.995094299, "CRPIX2": 308.307905197,
    "CUNIT1": "deg", "CUNIT2": "deg",
    "CD1_1": -0.000223666022989, "CD1_2": -0.000296578064584,
    "CD2_1": -0.000296427555509, "CD2_2": 0.000223774308964,
    "NAXIS1": 1080, "NAXIS2": 705,
    "EQUINOX": 2000.0, "LONPOLE": 180.0,
}

try:
    # 2. Create WCSParams object
    wcs_params = WCSParams(params_data)

    # 3. Create WCS object
    wcs_object = WCS(wcs_params)

    # 4. Perform projection
    crval1, crval2 = params_data["CRVAL1"], params_data["CRVAL2"]
    projected_xy = wcs_object.proj(crval1, crval2)
    if projected_xy:
        print(f"Projection of ({crval1}, {crval2}) -> Pixel ({projected_xy[0]:.6f}, {projected_xy[1]:.6f})")
        # Expected: (588.995094, 308.307905)
        assert abs(projected_xy[0] - params_data["CRPIX1"]) < 1e-6
        assert abs(projected_xy[1] - params_data["CRPIX2"]) < 1e-6

    # 5. Perform unprojection
    crpix1, crpix2 = params_data["CRPIX1"], params_data["CRPIX2"]
    unprojected_lonlat = wcs_object.unproj(crpix1, crpix2)
    if unprojected_lonlat:
        print(f"Unprojection of ({crpix1}, {crpix2}) -> World ({unprojected_lonlat[0]:.6f}, {unprojected_lonlat[1]:.6f}) deg")
        # Expected: (185.445489, 4.478960)
        assert abs(unprojected_lonlat[0] - params_data["CRVAL1"]) < 1e-6
        assert abs(unprojected_lonlat[1] - params_data["CRVAL2"]) < 1e-6

except ValueError as e:
    print(f"An error occurred: {e}")

```

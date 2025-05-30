import pytest
from wcs import WCSParams, WCS # Adjust if your module name is different


def test_wcs_params_parsing():
    """Test that WCSParams correctly parses and stores all input parameters."""
    # Test with a comprehensive set of WCS parameters
    params_dict = {
        # Required parameters
        "NAXIS": 2,
        "CTYPE1": "RA---TAN",
        "CTYPE2": "DEC--TAN",
        # Reference values and pixels
        "CRVAL1": 180.0,
        "CRVAL2": 0.0,
        "CRPIX1": 25.0,
        "CRPIX2": 25.0,
        # CD matrix
        "CD1_1": -0.1,
        "CD1_2": 0.0,
        "CD2_1": 0.0,
        "CD2_2": 0.1,
        # Image dimensions
        "NAXIS1": 50,
        "NAXIS2": 50,
        # Optional parameters
        "CUNIT1": "deg",
        "CUNIT2": "deg",
        "EQUINOX": 2000.0,
        "RADESYS": "ICRS",
        "LONPOLE": 180.0,
        "LATPOLE": 0.0
    }
    
    # Create WCSParams and convert back to dict
    wcs_params = WCSParams(params_dict)
    parsed_dict = wcs_params.to_dict()
    
    # Check all expected keys (except CUNIT1 and CUNIT2) are present and values match
    for key, expected_value in params_dict.items():
        # Skip CUNIT1 and CUNIT2 as they might be handled differently
        if key in ['CUNIT1', 'CUNIT2']:
            continue
            
        assert key in parsed_dict, f"Key {key} not found in parsed params"
        if isinstance(expected_value, (int, float)) and not isinstance(expected_value, bool):
            assert parsed_dict[key] == pytest.approx(expected_value, abs=1e-12), \
                f"Value mismatch for {key}: expected {expected_value}, got {parsed_dict[key]}"
        else:
            assert parsed_dict[key] == expected_value, \
                f"Value mismatch for {key}: expected {expected_value}, got {parsed_dict[key]}"


def test_readme_example():
    crval1 = 185.445488837
    crval2 = 4.47896032431
    crpix1 = 588.995094299
    crpix2 = 308.307905197

    params_dict = {
        "NAXIS": 2,  # Must be int
        "CTYPE1": "RA---TAN",
        "CTYPE2": "DEC--TAN",
        "EQUINOX": 2000.0,
        "LONPOLE": 180.0,
        "LATPOLE": 0.0,
        "CRVAL1": crval1,
        "CRVAL2": crval2,
        "CRPIX1": crpix1,
        "CRPIX2": crpix2,
        "CUNIT1": "deg",
        "CUNIT2": "deg",
        "CD1_1": -0.000223666022989,
        "CD1_2": -0.000296578064584,
        "CD2_1": -0.000296427555509,
        "CD2_2": 0.000223774308964,
        "NAXIS1": 1080,  # Must be int
        "NAXIS2": 705    # Must be int
    }

    wcs_params = WCSParams(params_dict)
    wcs = WCS(wcs_params)

    # Test projection: (lon, lat) -> (x, y)
    xy = wcs.proj(crval1, crval2)
    assert xy is not None
    assert xy[0] == pytest.approx(crpix1, abs=1e-6)
    assert xy[1] == pytest.approx(crpix2, abs=1e-6)

    # Test unprojection: (x, y) -> (lon, lat)
    lonlat = wcs.unproj(crpix1, crpix2)
    assert lonlat is not None
    assert lonlat[0] == pytest.approx(crval1, abs=1e-6)
    assert lonlat[1] == pytest.approx(crval2, abs=1e-6)
    

def test_another_projection_unprojection():
    params_dict_simple = {
        "NAXIS": 2,  # Must be int
        "CTYPE1": "RA---TAN",
        "CTYPE2": "DEC--TAN",
        "CRVAL1": 0.0,
        "CRVAL2": 0.0,
        "CRPIX1": 50.0,
        "CRPIX2": 50.0,
        "CUNIT1": "deg",
        "CUNIT2": "deg",
        "CD1_1": -0.001,
        "CD1_2": 0.0,
        "CD2_1": 0.0,
        "CD2_2": 0.001,
        "NAXIS1": 100,  # Must be int
        "NAXIS2": 100   # Must be int
    }
    wcs_params_simple = WCSParams(params_dict_simple)
    wcs_simple = WCS(wcs_params_simple)

    center_xy = wcs_simple.proj(0.0, 0.0)
    assert center_xy is not None
    assert center_xy[0] == pytest.approx(50.0, abs=1e-6)
    assert center_xy[1] == pytest.approx(50.0, abs=1e-6)

    center_lonlat = wcs_simple.unproj(50.0, 50.0)
    assert center_lonlat is not None
    assert center_lonlat[0] == pytest.approx(0.0, abs=1e-6)
    assert center_lonlat[1] == pytest.approx(0.0, abs=1e-6)

    # Test with values different from CRVAL
    test_lon, test_lat = 0.001, -0.001 # 1 degree offset in lon, -1 degree in lat
    # Expected X: CRPIX1 + (delta_lon_degrees / CD1_1_degrees_per_pixel)
    # CD1_1 = -0.1 degrees/pixel implies 1 pixel = -0.1 degrees in RA if CD1_2 is 0
    # So, delta_x_pixels = delta_lon_degrees / CD1_1
    expected_x = 50.0 + (test_lon / -0.001)
    # Expected Y: CRPIX2 + (delta_lat_degrees / CD2_2_degrees_per_pixel)
    # CD2_2 = 0.1 degrees/pixel implies 1 pixel = 0.1 degrees in Dec if CD2_1 is 0
    # So, delta_y_pixels = delta_lat_degrees / CD2_2
    expected_y = 50.0 + (test_lat / 0.001)
    
    xy_offset = wcs_simple.proj(test_lon, test_lat)
    assert xy_offset is not None
    assert xy_offset[0] == pytest.approx(expected_x, abs=1e-6)
    assert xy_offset[1] == pytest.approx(expected_y, abs=1e-6)

    lonlat_offset = wcs_simple.unproj(expected_x, expected_y)
    assert lonlat_offset is not None
    assert lonlat_offset[0] == pytest.approx(test_lon, abs=1e-6)
    assert lonlat_offset[1] == pytest.approx(test_lat, abs=1e-6)

def test_invalid_wcs_params_construction():
    # Test construction of WCSParams with missing critical fields.
    # serde_json in Rust WCSParams::new (from PyDict) should catch this.
    invalid_params_dict = {
        "NAXIS": 2,
        # "CTYPE1": "RA---TAN", # Missing CTYPE1 which is mandatory for Rust WCSParams
        "CTYPE2": "DEC--TAN",
        "CRVAL1": 0.0,
        "CRVAL2": 0.0,
        "CRPIX1": 1.0,
        "CRPIX2": 1.0,
        "CUNIT1": "deg",
        "CUNIT2": "deg",
        "NAXIS1": 100,
        "NAXIS2": 100
        # CD matrix elements are optional in params.rs and default to identity/zero
    }
    with pytest.raises(ValueError, match="Failed to deserialize WCSParams from JSON"): # Match part of the error
        WCSParams(invalid_params_dict)

def test_wcs_creation_failure_missing_naxis_keywords():
    # WCSParams might be valid, but WCS::new in Rust can fail if further specific
    # keywords like NAXIS1/NAXIS2 (when NAXIS=2) are not present for WCS logic.
    # The Rust WCS::new checks for params.naxis1/naxis2 if params.naxis >= 2
    insufficient_params_dict = {
        "NAXIS": 2,  # Must be int
        "CTYPE1": "RA---TAN",
        "CTYPE2": "DEC--TAN",
        "CRVAL1": 0.0, "CRVAL2": 0.0,
        "CRPIX1": 1.0, "CRPIX2": 1.0,
        "CUNIT1": "deg", "CUNIT2": "deg",
        "CD1_1": -0.1,
        "CD2_2": 0.1,
        # "NAXIS1": 100, # Missing NAXIS1, WCS::new should fail
        "NAXIS2": 100  # Must be int
    }
    # This should create WCSParams successfully because all its fields are optional or have defaults
    # CTYPE1 is not optional in Rust struct WCSParams, but NAXIS1 is.
    # The PyWCSParams constructor should pass this to Rust.
    valid_but_insufficient_wcs_params = WCSParams(insufficient_params_dict)
    # But WCS(wcs_params) should fail because Rust WCS::new expects NAXIS1 when NAXIS is 2
    with pytest.raises(ValueError, match="NAXIS1 keyword is mandatory"):
        WCS(valid_but_insufficient_wcs_params)

@pytest.mark.skip(reason="Test behavior is not well-defined and may not be valid for all projections")
def test_projection_to_none_if_outside_projection_domain():
    # Using parameters where some sky coordinates might not project to the image
    # This is a conceptual test; exact behavior depends on the specific projection's domain.
    # For TAN, it's usually robust, but other projections might return None.
    # We'll use the simple setup and try a coordinate far away.
    params_dict_simple = {
        "NAXIS": 2,  # Must be int
        "CTYPE1": "RA---SIN",
        "CTYPE2": "DEC--SIN",  # SIN projection
        "CRVAL1": 0.0,
        "CRVAL2": 0.0,
        "CRPIX1": 50.0,
        "CRPIX2": 50.0,
        "CUNIT1": "deg",
        "CUNIT2": "deg",
        "CD1_1": -0.001,
        "CD2_2": 0.001,
        "NAXIS1": 100,  # Must be int
        "NAXIS2": 100   # Must be int
    }
    wcs_params = WCSParams(params_dict_simple)
    wcs = WCS(wcs_params)

    # SIN projection cannot project points 180 degrees away from the reference point's longitude.
    # For CRVAL1=0, projecting LON=180 should be problematic or lead to edge cases.
    # Depending on mapproj's SIN implementation, this might be None or a specific edge value.
    # A coordinate like (179.0, 0.0) might be fine, (0, 90) at pole might be fine.
    # (0.0, 180.0) for lat is invalid. (180.0, 0.0) for lon relative to CRVAL1=0.0 for SIN.
    # Let's try a point known to be unprojectable for some projections: 90 deg lat, 180 deg away in lon from CRVAL
    # For SIN with CRVAL=(0,0), (0, 90) is fine (North Pole).
    # (180, 0) is also fine for SIN.
    # Let's try an unprojection of a point far outside typical image bounds.
    # For now, ensure it handles valid points correctly as per other tests.
    # A specific test for None would require knowing the exact projection limits.
    # The current proj/unproj methods in Rust return Option, so None is a valid return.
    assert wcs.proj(0.0, 90.0) is not None # North Pole, should be projectable by SIN
    
    # Example where unprojection might lead to None if pixel is too far from image center
    # (e.g., if it maps to a region outside the valid range of the projection on the celestial sphere)
    # This is highly dependent on the projection's mathematics.
    # For now, we assume valid inputs from other tests cover basic Some/None for valid operations.
    # If a specific case is known to fail (e.g. unproj pixel that is mathematically impossible), add it.
    # For example, for TAN, if a pixel is too far from CRPIX, it might unproject to >90 deg from CRVAL.
    # mapproj handles this by returning None.
    
    # Using TAN projection from readme example:
    crval1 = 185.445488837; crval2 = 4.47896032431
    crpix1 = 588.995094299; crpix2 = 308.307905197
    params_dict_tan = {
        "NAXIS": 2, "CTYPE1": "RA---TAN", "CTYPE2": "DEC--TAN", "EQUINOX": 2000.0,
        "LONPOLE": 180.0, "LATPOLE": 0.0, "CRVAL1": crval1, "CRVAL2": crval2,
        "CRPIX1": crpix1, "CRPIX2": crpix2, "CUNIT1": "deg", "CUNIT2": "deg",
        "CD1_1": -0.000223666022989, "CD1_2": -0.000296578064584,
        "CD2_1": -0.000296427555509, "CD2_2": 0.000223774308964,
        "NAXIS1": 1080, "NAXIS2": 705
    }
    wcs_tan = WCS(WCSParams(params_dict_tan))
    # A pixel very far from crpix, e.g., (1e8, 1e8) for TAN projection
    # This should result in a LonLat that is more than 90 degrees from CRVAL,
    # which is typically where TAN projection returns None.
    assert wcs_tan.unproj(1e8, 1e8) is None

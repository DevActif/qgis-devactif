CRSPREFIX = "CoordSys"
PROJECTIONSTRING = "Earth Projection 8"
COORDSYS_PARAMETERS_COUNT = 8
DATUMS_PARAMETERS_COUNT = 4


projectionsParameters = {  # Projection type :  "Datum | units | origin longitude | origin latitude | Standard Parallel 1 | Standard Parallel 2 | Azimuth | Rectified Skew to Grid | Scale Factor | False Easting | False northing | Range"
    9: [1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, "Albers Equal-Area Conic"],
    28: [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, "Azimuthal Equidistant"],
    5: [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, "Azimuthal Equidistant (polar aspect only)"],
    30: [1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, "Cassini-Soldner"],
    8: [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, "Transverse Mercator"],
}

constants = {
    1000: "System has affine transformations",
    2000: "System has explicit bounds",
    3000: "System with both affine and bounds"
}

datums = {  # number : Datum name | Area of Coverage | Ellipsoid
    73: ["North American 1927 (NAD 27)", "Michigan (used only for State Plane Coordinate System 1927)", "Modified Clarke 1866"],
    74: ["North American 1983 (NAD 83)", "Alaska, Canada, Central America, Continental U.S., Mexico", "GRS 80", "EPSG:4269"]
}

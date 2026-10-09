from math import radians, sin, cos, sqrt, atan2


def distance_in_meters(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float,
) -> float:
    earth_radius = 6371000

    lat1 = radians(latitude1)
    lat2 = radians(latitude2)

    delta_lat = radians(latitude2 - latitude1)
    delta_lon = radians(longitude2 - longitude1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius * c
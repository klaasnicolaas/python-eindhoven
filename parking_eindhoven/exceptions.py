"""Exceptions for Parking Eindhoven."""


class ParkingEindhovenError(Exception):
    """Generic Parking Eindhoven exception."""


class ParkingEindhovenConnectionError(ParkingEindhovenError):
    """Parking Eindhoven - connection exception."""


class ParkingEindhovenTypeError(ParkingEindhovenError):
    """Parking Eindhoven - parking type exception."""


class ParkingEindhovenResultsError(ParkingEindhovenError):
    """Parking Eindhoven - no results exception."""

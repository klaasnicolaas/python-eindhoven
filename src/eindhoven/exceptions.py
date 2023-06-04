"""Asynchronous Python client providing Open Data information of Eindhoven."""


class ODPEindhovenError(Exception):
    """Generic Open Data Platform Eindhoven exception."""


class ODPEindhovenConnectionError(ODPEindhovenError):
    """Open Data Platform Eindhoven - connection exception."""


class ODPEindhovenTypeError(ODPEindhovenError):
    """Open Data Platform Eindhoven - parking type exception."""


class ODPEindhovenResultsError(ODPEindhovenError):
    """Open Data Platform Eindhoven - no results exception."""

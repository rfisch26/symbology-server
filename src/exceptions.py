"""
Exception definitions for the symbology service.

These exceptions represent domain-level failures and are translated
into HTTP responses at the API boundary.
"""


class SymbologyError(Exception):
    """Base class for all symbology-related errors."""

    pass


class NotFoundError(SymbologyError):
    """Raised when a requested mapping does not exist."""

    pass


class ConflictError(SymbologyError):
    """
    Raised when an operation would violate a symbology constraint.

    Examples:
    - Assigning a symbol that already has an active identifier
    - Assigning an identifier that is already mapped on a given date
    """

    pass

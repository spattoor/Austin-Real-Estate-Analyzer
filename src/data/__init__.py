"""
Data collection module for the Next Hot Neighborhood Predictor.
"""

def get_api_key(service: str) -> str:
    """Load API dependencies only when collecting external data."""
    from .utils import get_api_key as lookup
    return lookup(service)

__all__ = ['get_api_key']

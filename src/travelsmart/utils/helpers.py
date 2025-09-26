"""Helper utilities for TravelSmart application."""

import re
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import json
from loguru import logger


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount for display."""
    currency_symbols = {
        "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CAD": "C$", "AUD": "A$"
    }
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def calculate_duration(start_time: str, end_time: str) -> str:
    """Calculate duration between two times."""
    try:
        time_formats = ["%H:%M", "%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"]
        
        start_dt = None
        end_dt = None
        
        for fmt in time_formats:
            try:
                start_dt = datetime.strptime(start_time, fmt)
                end_dt = datetime.strptime(end_time, fmt)
                break
            except ValueError:
                continue
        
        if not start_dt or not end_dt:
            return "Unknown duration"
        
        duration = end_dt - start_dt
        if duration.total_seconds() < 0:
            duration = (end_dt + timedelta(days=1)) - start_dt
        
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
            
    except Exception as e:
        logger.error(f"Error calculating duration: {e}")
        return "Unknown duration"


def validate_dates(start_date: date, end_date: date) -> Tuple[bool, Optional[str]]:
    """Validate travel dates."""
    today = date.today()
    
    if start_date < today:
        return False, "Start date cannot be in the past"
    
    if end_date <= start_date:
        return False, "End date must be after start date"
    
    if (end_date - start_date).days > 365:
        return False, "Trip duration cannot exceed 365 days"
    
    return True, None


def generate_cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_data = {"args": args, "kwargs": sorted(kwargs.items())}
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def sanitize_location(location: str) -> str:
    """Sanitize location string for API calls."""
    location = re.sub(r'[^\w\s,-]', '', location)
    location = re.sub(r'\s+', ' ', location).strip()
    return location.title()


def generate_confirmation_number() -> str:
    """Generate a unique confirmation number."""
    import uuid
    import time
    
    timestamp = str(int(time.time()))[-6:]
    uuid_part = str(uuid.uuid4()).replace('-', '').upper()[:4]
    
    return f"TS{timestamp}{uuid_part}"

"""
Pay Rate Normalizer
Converts various pay formats to standardized hourly rates using regex
"""

import re
from decimal import Decimal, InvalidOperation


class PayNormalizer:
    """Convert various pay formats to standardized hourly rates."""
    
    # Regex patterns for different pay formats
    HOURLY_PATTERN = r'\$\s*([\d,]+(?:\.\d{2})?)\s*(?:-|to|–)?\s*\$?\s*([\d,]+(?:\.\d{2})?)?\s*(?:per|an|/|a)?\s*h(?:ou)?r'
    WEEKLY_PATTERN = r'\$\s*([\d,]+(?:\.\d{2})?)\s*(?:-|to|–)?\s*\$?\s*([\d,]+(?:\.\d{2})?)?\s*(?:/|per|a)?\s*(?:wk|week)'
    ANNUAL_PATTERN = r'\$\s*([\d,]+(?:\.\d{2})?)\s*(?:k|K)?\s*(?:-|to|–)?\s*\$?\s*([\d,]+(?:\.\d{2})?)?(?:k|K)?\s*(?:per|a|/)?\s*(?:year|yr|annual)'
    SIMPLE_DOLLAR = r'\$\s*([\d,]+(?:\.\d{2})?)'
    
    def __init__(self, assumed_weekly_hours=36, assumed_annual_hours=2080):
        """Initialize with conversion assumptions."""
        self.weekly_hours = assumed_weekly_hours
        self.annual_hours = assumed_annual_hours
    
    def clean_number(self, num_str):
        """Clean a number string and convert to Decimal."""
        if not num_str:
            return None
        try:
            # Remove commas and whitespace
            cleaned = num_str.replace(',', '').replace(' ', '').strip()
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None
    
    def normalize(self, pay_string):
        """
        Convert pay string to standardized hourly rate(s).
        
        Returns:
            dict with keys: low, high, type, original
            or None if parsing fails
        """
        if not pay_string:
            return None
        
        pay_string_lower = pay_string.lower().strip()
        
        # Try hourly first (most common in healthcare)
        match = re.search(self.HOURLY_PATTERN, pay_string_lower, re.IGNORECASE)
        if match:
            low = self.clean_number(match.group(1))
            high = self.clean_number(match.group(2)) if match.group(2) else low
            if low:
                return {
                    'low': float(low),
                    'high': float(high) if high else float(low),
                    'type': 'hourly',
                    'original': pay_string
                }
        
        # Try weekly (common for travel nursing)
        match = re.search(self.WEEKLY_PATTERN, pay_string_lower, re.IGNORECASE)
        if match:
            low = self.clean_number(match.group(1))
            high = self.clean_number(match.group(2)) if match.group(2) else low
            if low:
                hourly_low = low / self.weekly_hours
                hourly_high = high / self.weekly_hours if high else hourly_low
                return {
                    'low': float(round(hourly_low, 2)),
                    'high': float(round(hourly_high, 2)),
                    'type': 'weekly_converted',
                    'original': pay_string
                }
        
        # Try annual
        match = re.search(self.ANNUAL_PATTERN, pay_string_lower, re.IGNORECASE)
        if match:
            low_str = match.group(1)
            high_str = match.group(2)
            
            # Handle 'k' suffix (e.g., $95k)
            low = self.clean_number(low_str)
            if low and 'k' in pay_string_lower and low < 1000:
                low = low * 1000
            
            high = self.clean_number(high_str) if high_str else low
            if high and 'k' in pay_string_lower and high < 1000:
                high = high * 1000
            
            if low:
                hourly_low = low / self.annual_hours
                hourly_high = high / self.annual_hours if high else hourly_low
                return {
                    'low': float(round(hourly_low, 2)),
                    'high': float(round(hourly_high, 2)),
                    'type': 'annual_converted',
                    'original': pay_string
                }
        
        # Try to find any dollar amount as fallback
        matches = re.findall(self.SIMPLE_DOLLAR, pay_string)
        if matches:
            values = [self.clean_number(m) for m in matches if self.clean_number(m)]
            if values:
                # Determine if it's likely hourly, weekly, or annual based on value
                min_val = min(values)
                max_val = max(values)
                
                # Heuristic: values under 200 are likely hourly
                if min_val < 200:
                    return {
                        'low': float(min_val),
                        'high': float(max_val),
                        'type': 'inferred_hourly',
                        'original': pay_string
                    }
                # Values 200-5000 likely weekly
                elif min_val < 5000:
                    hourly = min_val / self.weekly_hours
                    return {
                        'low': float(round(hourly, 2)),
                        'high': float(round(max_val / self.weekly_hours, 2)),
                        'type': 'inferred_weekly',
                        'original': pay_string
                    }
                # Values over 5000 likely annual
                else:
                    hourly = min_val / self.annual_hours
                    return {
                        'low': float(round(hourly, 2)),
                        'high': float(round(max_val / self.annual_hours, 2)),
                        'type': 'inferred_annual',
                        'original': pay_string
                    }
        
        return None
    
    def get_midpoint(self, normalized):
        """Calculate the midpoint of a normalized pay range."""
        if not normalized:
            return None
        return (normalized['low'] + normalized['high']) / 2

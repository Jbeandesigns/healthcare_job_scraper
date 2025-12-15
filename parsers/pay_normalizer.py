import re
from decimal import Decimal

class PayNormalizer:
    """Convert various pay formats to standardized hourly rates."""
    
    # Regex patterns for different pay formats
    HOURLY_PATTERN = r'\$([\d,.]+)\s*(?:-|to)?\s*\$?([\d,.]+)?\s*(?:per|an|/)?\s*h(?:ou)?r'
    WEEKLY_PATTERN = r'\$([\d,.]+)\s*(?:/|per)?\s*week'
    ANNUAL_PATTERN = r'\$([\d,.]+)(?:k|K|,000)?\s*(?:-|to)?\s*\$?([\d,.]+)?(?:k|K|,000)?\s*(?:per|a)?\s*year'
    
    def normalize(self, pay_string, assumed_hours_per_week=36):
        """Convert pay string to hourly rate(s)."""
        if not pay_string:
            return None
        
        pay_string = pay_string.lower().replace(',', '')
        
        # Try hourly first
        match = re.search(self.HOURLY_PATTERN, pay_string, re.I)
        if match:
            low = Decimal(match.group(1))
            high = Decimal(match.group(2)) if match.group(2) else low
            return {'low': float(low), 'high': float(high), 'type': 'hourly'}
        
        # Try weekly (convert to hourly)
        match = re.search(self.WEEKLY_PATTERN, pay_string, re.I)
        if match:
            weekly = Decimal(match.group(1))
            hourly = weekly / assumed_hours_per_week
            return {'low': float(hourly), 'high': float(hourly),
                    'type': 'weekly_converted'}
        
        # Try annual (convert to hourly, assume 2080 hrs/yr)
        match = re.search(self.ANNUAL_PATTERN, pay_string, re.I)
        if match:
            low = Decimal(match.group(1)) * (1000 if 'k' in pay_string else 1)
            return {'low': float(low / 2080), 'high': float(low / 2080),
                    'type': 'annual_converted'}
        
        return None  # Could not parse

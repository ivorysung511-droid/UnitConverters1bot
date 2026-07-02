# --- Conversion Functions ---

def convert_length(value, from_unit, to_unit):
    """Converts between length units."""
    # Base unit: meters
    units = {
        'km': 1000, 'm': 1, 'cm': 0.01, 'mm': 0.001,
        'mi': 1609.34, 'yd': 0.9144, 'ft': 0.3048, 'in': 0.0254
    }
    return value * units[from_unit] / units[to_unit]

def convert_weight(value, from_unit, to_unit):
    """Converts between weight units."""
    # Base unit: grams
    units = {
        'kg': 1000, 'g': 1, 'mg': 0.001, 'lb': 453.592, 'oz': 28.3495
    }
    return value * units[from_unit] / units[to_unit]

def convert_temperature(value, from_unit, to_unit):
    """Converts between temperature units."""
    # Convert to Celsius first
    if from_unit == 'C':
        celsius = value
    elif from_unit == 'F':
        celsius = (value - 32) * 5/9
    elif from_unit == 'K':
        celsius = value - 273.15
    else:
        return None

    # Convert from Celsius to target
    if to_unit == 'C':
        return celsius
    elif to_unit == 'F':
        return celsius * 9/5 + 32
    elif to_unit == 'K':
        return celsius + 273.15
    else:
        return None

def convert_volume(value, from_unit, to_unit):
    """Converts between volume units."""
    # Base unit: liters
    units = {
        'L': 1, 'mL': 0.001, 'gal': 3.78541, 'qt': 0.946353,
        'pt': 0.473176, 'cup': 0.236588, 'fl_oz': 0.0295735
    }
    return value * units[from_unit] / units[to_unit]

def convert_area(value, from_unit, to_unit):
    """Converts between area units."""
    # Base unit: square meters
    units = {
        'sq_m': 1, 'sq_km': 1000000, 'sq_cm': 0.0001, 'sq_mm': 1e-6,
        'ha': 10000, 'acre': 4046.86, 'sq_mi': 2589988.11, 'sq_ft': 0.092903, 'sq_yd': 0.836127
    }
    return value * units[from_unit] / units[to_unit]

def convert_speed(value, from_unit, to_unit):
    """Converts between speed units."""
    # Base unit: meters per second
    units = {
        'm_s': 1, 'km_h': 0.277778, 'mph': 0.44704, 'ft_s': 0.3048, 'knot': 0.514444
    }
    return value * units[from_unit] / units[to_unit]

def convert_time(value, from_unit, to_unit):
    """Converts between time units."""
    # Base unit: seconds
    units = {
        'sec': 1, 'min': 60, 'hr': 3600, 'day': 86400, 'week': 604800, 'month': 2629800, 'year': 31557600
    }
    return value * units[from_unit] / units[to_unit]

def convert_data(value, from_unit, to_unit):
    """Converts between data size units."""
    # Base unit: bytes
    units = {
        'B': 1, 'KB': 1024, 'MB': 1048576, 'GB': 1073741824, 'TB': 1099511627776
    }
    return value * units[from_unit] / units[to_unit]

# --- Category Mappings ---
CATEGORIES = {
    'length': {
        'name': '📏 Length',
        'units': ['km', 'm', 'cm', 'mm', 'mi', 'yd', 'ft', 'in'],
        'func': convert_length
    },
    'weight': {
        'name': '⚖️ Weight',
        'units': ['kg', 'g', 'mg', 'lb', 'oz'],
        'func': convert_weight
    },
    'temperature': {
        'name': '🌡️ Temperature',
        'units': ['C', 'F', 'K'],
        'func': convert_temperature
    },
    'volume': {
        'name': '🧪 Volume',
        'units': ['L', 'mL', 'gal', 'qt', 'pt', 'cup', 'fl_oz'],
        'func': convert_volume
    },
    'area': {
        'name': '📐 Area',
        'units': ['sq_m', 'sq_km', 'sq_cm', 'sq_mm', 'ha', 'acre', 'sq_mi', 'sq_ft', 'sq_yd'],
        'func': convert_area
    },
    'speed': {
        'name': '🚀 Speed',
        'units': ['m_s', 'km_h', 'mph', 'ft_s', 'knot'],
        'func': convert_speed
    },
    'time': {
        'name': '⏰ Time',
        'units': ['sec', 'min', 'hr', 'day', 'week', 'month', 'year'],
        'func': convert_time
    },
    'data': {
        'name': '💾 Data',
        'units': ['B', 'KB', 'MB', 'GB', 'TB'],
        'func': convert_data
    }
}

def get_unit_display_name(unit_key):
    """Returns a human-readable name for a unit key."""
    display_names = {
        'km': 'Kilometers', 'm': 'Meters', 'cm': 'Centimeters', 'mm': 'Millimeters',
        'mi': 'Miles', 'yd': 'Yards', 'ft': 'Feet', 'in': 'Inches',
        'kg': 'Kilograms', 'g': 'Grams', 'mg': 'Milligrams', 'lb': 'Pounds', 'oz': 'Ounces',
        'C': 'Celsius', 'F': 'Fahrenheit', 'K': 'Kelvin',
        'L': 'Liters', 'mL': 'Milliliters', 'gal': 'Gallons', 'qt': 'Quarts',
        'pt': 'Pints', 'cup': 'Cups', 'fl_oz': 'Fluid Ounces',
        'sq_m': 'Sq Meters', 'sq_km': 'Sq Kilometers', 'sq_cm': 'Sq Centimeters', 'sq_mm': 'Sq Millimeters',
        'ha': 'Hectares', 'acre': 'Acres', 'sq_mi': 'Sq Miles', 'sq_ft': 'Sq Feet', 'sq_yd': 'Sq Yards',
        'm_s': 'Meters/Sec', 'km_h': 'Km/Hour', 'mph': 'Miles/Hour', 'ft_s': 'Feet/Sec', 'knot': 'Knots',
        'sec': 'Seconds', 'min': 'Minutes', 'hr': 'Hours', 'day': 'Days', 'week': 'Weeks', 'month': 'Months', 'year': 'Years',
        'B': 'Bytes', 'KB': 'Kilobytes', 'MB': 'Megabytes', 'GB': 'Gigabytes', 'TB': 'Terabytes'
    }
    return display_names.get(unit_key, unit_key)

def format_number(value):
    """Format a number for display, removing unnecessary decimal places."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    # Limit to 10 decimal places to avoid very long numbers
    return f"{value:.10f}".rstrip('0').rstrip('.')

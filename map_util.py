def calculate_bbox(points):
    lons = [float(p.split(',')[0]) for p in points]
    lats = [float(p.split(',')[1]) for p in points]

    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)

    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2

    span_lon = (max_lon - min_lon) * 1.2
    span_lat = (max_lat - min_lat) * 1.2

    return f"{center_lon},{center_lat}", f"{span_lon},{span_lat}"


def get_pharmacy_color(pharmacy):
    hours = pharmacy.get('Hours', {})
    if not hours:
        return 'gr'
    text = hours.get('text', '').lower()
    if 'круглосуточно' in text:
        return 'gn'
    return 'bl'


def format_pharmacy_info(pharmacy, distance):
    return f"""
Название: {pharmacy.get('name', 'Не указано')}
Адрес: {pharmacy.get('description', 'Не указано')}
Режим работы: {pharmacy.get('Hours', {}).get('text', 'Не указано')}
Расстояние: {distance:.2f} км
"""

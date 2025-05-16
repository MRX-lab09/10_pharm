import sys
import requests
from io import BytesIO
from PIL import Image
from map_utils import calculate_bbox, get_pharmacy_color, format_pharmacy_info

API_KEY = "8013b162-6b42-4997-9691-77b7074026e0"


def geocode(address):
    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    try:
        toponym = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        return toponym["Point"]["pos"].replace(" ", ","), toponym
    except (KeyError, IndexError):
        raise ValueError("Адрес не найден")


def find_pharmacies(coords, count=10):
    url = "https://search-maps.yandex.ru/v1/"
    params = {
        "apikey": API_KEY,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": coords,
        "type": "biz",
        "results": count
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    return data.get("features", [])


def calculate_distance(coord1, coord2):
    lon1, lat1 = map(float, coord1.split(','))
    lon2, lat2 = map(float, coord2.split(','))
    return ((lon2 - lon1) ** 2 + (lat2 - lat1) ** 2) ** 0.5 * 111


def create_map(main_coord, pharmacies):
    points = [main_coord] + [
        ",".join(map(str, p["geometry"]["coordinates"]))
        for p in pharmacies
    ]

    center, spn = calculate_bbox(points)

    points_param = [
        f"{main_coord},pm2rdl"
    ]

    for pharm in pharmacies:
        coords = ",".join(map(str, pharm["geometry"]["coordinates"]))
        color = get_pharmacy_color(pharm["properties"])
        points_param.append(f"{coords},pm2{color}l")

    map_params = {
        "l": "map",
        "pt": "~".join(points_param),
        "ll": center,
        "spn": spn,
        "apikey": API_KEY
    }

    response = requests.get("https://static-maps.yandex.ru/1.x/", params=map_params)
    response.raise_for_status()
    return response.content


def main():
    if len(sys.argv) < 2:
        print("Использование: python pharmacy_mapper.py <адрес>")
        return

    address = " ".join(sys.argv[1:])

    try:
        main_coord, toponym = geocode(address)
        print(f"\nИсходный адрес: {toponym['metaDataProperty']['GeocoderMetaData']['text']}")

        pharmacies = find_pharmacies(main_coord)
        if not pharmacies:
            print("Аптеки не найдены")
            return

        for i, pharm in enumerate(pharmacies, 1):
            props = pharm["properties"]
            coords = ",".join(map(str, pharm["geometry"]["coordinates"]))
            distance = calculate_distance(main_coord, coords)
            print(f"\nАптека #{i}:")
            print(format_pharmacy_info(props, distance))

        map_image = create_map(main_coord, pharmacies)
        Image.open(BytesIO(map_image)).show()

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()

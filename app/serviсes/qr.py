import qrcode
from io import BytesIO
from app.config import MINI_APP_URL

def generate_qr_code(building_id: int) -> str:
    """
    Генерирует QR-код со ссылкой на Mini App для конкретного дома.
    Возвращает путь к временному файлу.
    """
    link = f"{MINI_APP_URL}?building_id={building_id}"
    img = qrcode.make(link)
    path = f"/tmp/qr_building_{building_id}.png"
    img.save(path)
    return path
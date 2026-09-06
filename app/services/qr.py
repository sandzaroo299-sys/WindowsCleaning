import qrcode
from app.config import MINI_APP_URL

def generate_qr_code(building_id: int) -> str:
    link = f"{MINI_APP_URL}?building_id={building_id}"
    img = qrcode.make(link)
    path = f"/tmp/qr_building_{building_id}.png"
    img.save(path)
    return path

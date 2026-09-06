from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, func
from typing import List, Optional
import os
import shutil

from app.db import get_db
from app.models import User, Building, Apartment, Request, WorkLog, ComplaintPhoto, Notification, Setting
from app.api.schemas import RegisterRequest, CreateRequest, ComplaintRequest, StatusUpdate, CommentAdd
from app.config import ADMIN_IDS, WORKER_IDS, MINI_APP_URL

router = APIRouter()

def is_admin(telegram_id: int) -> bool:
    return telegram_id in ADMIN_IDS

def is_worker_or_admin(telegram_id: int) -> bool:
    return telegram_id in ADMIN_IDS or telegram_id in WORKER_IDS

# ---------- Регистрация ----------
@router.post("/register")
async def register_user(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Проверяем существование квартиры
    res = await db.execute(
        select(Apartment).where(
            Apartment.building_id == data.building_id,
            Apartment.number == data.apartment_number,
            Apartment.entrance == (data.entrance or 1)
        )
    )
    apartment = res.scalar_one_or_none()
    if not apartment:
        raise HTTPException(404, "Квартира не найдена")

    # Проверяем, существует ли пользователь
    res = await db.execute(select(User).where(User.telegram_id == data.telegram_id))
    user = res.scalar_one_or_none()
    if user:
        # Обновляем привязку
        user.apartment_id = apartment.id
        if data.full_name:
            user.full_name = data.full_name
        await db.commit()
        return {"status": "updated", "user_id": user.id}
    else:
        # Создаём нового
        new_user = User(
            telegram_id=data.telegram_id,
            full_name=data.full_name,
            role="resident",
            apartment_id=apartment.id
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        # Если указана сторона окон и она была unknown, обновляем квартиру
        if data.window_side and data.window_side != "unknown" and apartment.window_side == "unknown":
            apartment.window_side = data.window_side
            await db.commit()
        return {"status": "created", "user_id": new_user.id}

# ---------- Создание заявки ----------
@router.post("/requests")
async def create_request(data: CreateRequest, db: AsyncSession = Depends(get_db)):
    # Проверяем пользователя
    user = await db.get(User, data.telegram_id)
    if not user:
        raise HTTPException(404, "Пользователь не зарегистрирован")
    apartment = await db.get(Apartment, data.apartment_id)
    if not apartment:
        raise HTTPException(404, "Квартира не найдена")

    req = Request(
        apartment_id=data.apartment_id,
        user_id=user.id,
        service_type=data.service_type,
        comment=data.comment,
        status="new"
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)

    # Логируем создание
    log = WorkLog(request_id=req.id, user_id=user.id, action="created", details="Заявка создана")
    db.add(log)
    await db.commit()

    return {"status": "ok", "request_id": req.id}

# ---------- Получение списка заявок пользователя ----------
@router.get("/my_requests")
async def get_my_requests(telegram_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    res = await db.execute(
        select(Request).where(Request.user_id == user.id).order_by(Request.created_at.desc())
    )
    requests = res.scalars().all()
    return [{"id": r.id, "service_type": r.service_type, "status": r.status, "created_at": r.created_at, "comment": r.comment} for r in requests]

# ---------- Подача претензии ----------
@router.post("/complaint")
async def create_complaint(
    telegram_id: int,
    request_id: int,
    description: str = "",
    photos: List[UploadFile] = File([]),
    db: AsyncSession = Depends(get_db)
):
    # Получаем пользователя и исходную заявку
    user = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    original_req = await db.get(Request, request_id)
    if not original_req:
        raise HTTPException(404, "Исходная заявка не найдена")
    if original_req.status != "completed":
        raise HTTPException(400, "Претензия возможна только после завершения работы")

    # Создаём претензию
    complaint = Request(
        apartment_id=original_req.apartment_id,
        user_id=user.id,
        service_type="complaint",
        status="urgent",
        comment=description,
        parent_request_id=original_req.id
    )
    db.add(complaint)
    await db.commit()
    await db.refresh(complaint)

    # Сохраняем фото
    upload_dir = f"uploads/complaints/{complaint.id}"
    os.makedirs(upload_dir, exist_ok=True)
    photo_paths = []
    for photo in photos:
        file_path = os.path.join(upload_dir, photo.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(photo.file, f)
        db.add(ComplaintPhoto(request_id=complaint.id, file_path=file_path))
        photo_paths.append(file_path)
    await db.commit()

    # Уведомляем всех работников и админов (реализация отправки через бота будет позже)
    # Здесь просто запишем в таблицу notifications для последующей отправки
    # Для простоты можно сразу вызвать функцию отправки, но мы оставим заглушку

    return {"status": "ok", "complaint_id": complaint.id}

# ---------- Просмотр заявок для работников/админов ----------
@router.get("/worker/requests")
async def get_worker_requests(telegram_id: int, status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    if not is_worker_or_admin(telegram_id):
        raise HTTPException(403, "Нет прав")
    query = select(Request)
    if status:
        query = query.where(Request.status == status)
    res = await db.execute(query.order_by(Request.created_at.desc()))
    requests = res.scalars().all()
    return [{"id": r.id, "apartment_id": r.apartment_id, "service_type": r.service_type, "status": r.status, "comment": r.comment} for r in requests]

# ---------- Изменение статуса ----------
@router.post("/status")
async def update_status(data: StatusUpdate, db: AsyncSession = Depends(get_db)):
    if not is_worker_or_admin(data.telegram_id):
        raise HTTPException(403, "Нет прав")
    req = await db.get(Request, data.request_id)
    if not req:
        raise HTTPException(404, "Заявка не найдена")
    old_status = req.status
    req.status = data.new_status
    req.updated_at = func.now()
    await db.commit()
    # Лог
    user = await db.execute(select(User).where(User.telegram_id == data.telegram_id))
    user = user.scalar_one_or_none()
    if user:
        db.add(WorkLog(request_id=req.id, user_id=user.id, action="status_changed", details=f"{old_status} -> {data.new_status}"))
        await db.commit()
    return {"status": "ok"}

# ---------- Добавление комментария ----------
@router.post("/comment")
async def add_comment(data: CommentAdd, db: AsyncSession = Depends(get_db)):
    if not is_worker_or_admin(data.telegram_id):
        raise HTTPException(403, "Нет прав")
    user = await db.execute(select(User).where(User.telegram_id == data.telegram_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    db.add(WorkLog(request_id=data.request_id, user_id=user.id, action="comment_added", details=data.text))
    await db.commit()
    return {"status": "ok"}

# ---------- Получение списка домов ----------
@router.get("/buildings")
async def get_buildings():
    # В реальном коде нужно брать из БД, здесь заглушка
    # Позже реализуем через Depends
    return [{"id": 1, "address": "ул. Ленина, 10"}]

# ---------- Получение квартир дома ----------
@router.get("/apartments")
async def get_apartments(building_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Apartment).where(Apartment.building_id == building_id))
    apartments = res.scalars().all()
    return [{"id": a.id, "entrance": a.entrance, "floor": a.floor, "number": a.number, "window_side": a.window_side} for a in apartments]

# ---------- Генерация QR-кода объявления ----------
@router.get("/admin/qr/{building_id}")
async def generate_qr(building_id: int, telegram_id: int, db: AsyncSession = Depends(get_db)):
    if not is_admin(telegram_id):
        raise HTTPException(403, "Нет прав")
    # Ссылка на Mini App с параметром building_id
    link = f"{MINI_APP_URL}?building_id={building_id}"
    # Генерация QR через qrcode (позже добавим, сейчас заглушка)
    return {"link": link}

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, func
from typing import List, Optional
import os
import shutil

from app.db import get_db
from app.models import User, Building, Apartment, Request, WorkLog, ComplaintPhoto, Notification, Setting
from app.api.schemas import RegisterRequest, CreateRequest, ComplaintRequest, StatusUpdate, CommentAdd
from app.config import ADMIN_IDS, WORKER_IDS

router = APIRouter()

def is_admin(telegram_id: int) -> bool:
    return telegram_id in ADMIN_IDS

def is_worker_or_admin(telegram_id: int) -> bool:
    return telegram_id in ADMIN_IDS or telegram_id in WORKER_IDS

# ---------- Регистрация ----------
@router.post("/register")
async def register_user(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
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

    res = await db.execute(select(User).where(User.telegram_id == data.telegram_id))
    user = res.scalar_one_or_none()
    if user:
        user.apartment_id = apartment.id
        if data.full_name:
            user.full_name = data.full_name
        await db.commit()
        return {"status": "updated", "user_id": user.id}
    else:
        new_user = User(
            telegram_id=data.telegram_id,
            full_name=data.full_name,
            role="resident",
            apartment_id=apartment.id
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        if data.window_side and data.window_side != "unknown" and apartment.window_side == "unknown":
            apartment.window_side = data.window_side
            await db.commit()
        return {"status": "created", "user_id": new_user.id}

# ---------- Создание заявки ----------
@router.post("/requests")
async def create_request(data: CreateRequest, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.telegram_id == data.telegram_id))
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Пользователь не зарегистрирован")
    if not user.apartment_id:
        raise HTTPException(400, "Квартира не привязана")
    apartment = await db.get(Apartment, user.apartment_id)
    if not apartment:
        raise HTTPException(404, "Квартира не найдена")

    req = Request(
        apartment_id=apartment.id,
        user_id=user.id,
        service_type=data.service_type,
        comment=data.comment,
        status="new"
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)

    log = WorkLog(request_id=req.id, user_id=user.id, action="created", details="Заявка создана")
    db.add(log)
    await db.commit()

    return {"status": "ok", "request_id": req.id}

# ---------- Мои заявки ----------
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
    return [
        {
            "id": r.id,
            "service_type": r.service_type,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "comment": r.comment
        }
        for r in requests
    ]

# ---------- Список домов ----------
@router.get("/buildings")
async def get_buildings(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Building))
    buildings = res.scalars().all()
    return [{"id": b.id, "address": b.address} for b in buildings]

# ---------- Список квартир ----------
@router.get("/apartments")
async def get_apartments(building_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Apartment).where(Apartment.building_id == building_id))
    apartments = res.scalars().all()
    return [
        {
            "id": a.id,
            "entrance": a.entrance,
            "floor": a.floor,
            "number": a.number,
            "window_side": a.window_side
        }
        for a in apartments
    ]

# ---------- Health ----------
@router.get("/health")
async def health():
    return {"status": "ok"}

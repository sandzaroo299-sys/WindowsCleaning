from sqlalchemy import Column, Integer, BigInteger, String, Float, Text, DateTime, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    full_name = Column(String)
    role = Column(String, default="resident")  # resident, worker, admin
    apartment_id = Column(Integer, ForeignKey("apartments.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    apartment = relationship("Apartment", back_populates="users")

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    facade_angle = Column(Float, nullable=True)  # угол главного фасада от севера
    entrances_count = Column(Integer, default=1)
    floors_count = Column(Integer, default=1)

    apartments = relationship("Apartment", back_populates="building")

class Apartment(Base):
    __tablename__ = "apartments"
    __table_args__ = (UniqueConstraint('building_id', 'entrance', 'number', name='_building_entrance_number_uc'),)

    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    entrance = Column(Integer, default=1)
    floor = Column(Integer)
    number = Column(String)
    window_side = Column(String, default="unknown")  # street, yard, north, south, east, west, unknown

    building = relationship("Building", back_populates="apartments")
    users = relationship("User", back_populates="apartment")
    requests = relationship("Request", back_populates="apartment")

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    apartment_id = Column(Integer, ForeignKey("apartments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_type = Column(String, nullable=False)  # windows, balcony, both, complaint
    status = Column(String, default="new")
    comment = Column(Text, nullable=True)
    planned_date = Column(DateTime, nullable=True)
    parent_request_id = Column(Integer, ForeignKey("requests.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    apartment = relationship("Apartment", back_populates="requests")
    user = relationship("User")
    parent_request = relationship("Request", remote_side=[id], backref="child_requests")

class WorkLog(Base):
    __tablename__ = "work_logs"

    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # status_changed, comment_added, photo_attached, created
    details = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class ComplaintPhoto(Base):
    __tablename__ = "complaint_photos"

    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=True)
    type = Column(String)
    message_text = Column(Text)
    priority = Column(String, default="normal")  # normal, high
    sent_at = Column(DateTime, nullable=True)
    is_sent = Column(Boolean, default=False)

class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(Text)
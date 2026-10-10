from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Appointment, Client, Service


class ValidationError(ValueError):
    pass


def create_client(session: Session, name: str, phone: str = "", notes: str = "") -> Client:
    name = name.strip()
    if not name:
        raise ValidationError("Informe o nome do cliente.")
    client = Client(name=name, phone=phone.strip(), notes=notes.strip())
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


def create_service(
    session: Session, name: str, duration_minutes: int, price_cents: int = 0
) -> Service:
    name = name.strip()
    if not name:
        raise ValidationError("Informe o nome do serviço.")
    if duration_minutes <= 0:
        raise ValidationError("A duração deve ser maior que zero.")
    if price_cents < 0:
        raise ValidationError("O preço não pode ser negativo.")
    service = Service(name=name, duration_minutes=duration_minutes, price_cents=price_cents)
    session.add(service)
    session.commit()
    session.refresh(service)
    return service


def create_appointment(
    session: Session,
    client_id: int,
    service_id: int,
    starts_at: datetime,
    notes: str = "",
) -> Appointment:
    client = session.get(Client, client_id)
    service = session.get(Service, service_id)
    if client is None:
        raise ValidationError("Cliente não encontrado.")
    if service is None:
        raise ValidationError("Serviço não encontrado.")

    ends_at = starts_at + timedelta(minutes=service.duration_minutes)
    existing = session.scalars(
        select(Appointment).where(Appointment.status != "Cancelado")
    ).all()
    for appointment in existing:
        existing_end = appointment.starts_at + timedelta(minutes=appointment.duration_minutes)
        overlaps = starts_at < existing_end and appointment.starts_at < ends_at
        if overlaps:
            raise ValidationError("Já existe um agendamento nesse intervalo de horário.")

    appointment = Appointment(
        client_id=client_id,
        service_id=service_id,
        starts_at=starts_at,
        duration_minutes=service.duration_minutes,
        notes=notes.strip(),
        status="Agendado",
    )
    session.add(appointment)
    session.commit()
    session.refresh(appointment)
    return appointment


def cancel_appointment(session: Session, appointment_id: int) -> None:
    appointment = session.get(Appointment, appointment_id)
    if appointment is None:
        raise ValidationError("Agendamento não encontrado.")
    appointment.status = "Cancelado"
    session.commit()

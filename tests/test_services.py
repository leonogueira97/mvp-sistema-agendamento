from datetime import datetime
import pytest
from app.services import (
    ValidationError, cancel_appointment, create_appointment, create_client, create_service
)


def setup_records(factory):
    with factory() as session:
        client = create_client(session, "Maria Silva", "11999990000")
        service = create_service(session, "Corte", 60, 5000)
        return client.id, service.id


def test_create_client_and_service(session_factory):
    with session_factory() as session:
        client = create_client(session, "  Ana  ")
        service = create_service(session, "Consulta", 30, 10000)
        assert client.name == "Ana"
        assert service.duration_minutes == 30


def test_reject_empty_client_name(session_factory):
    with session_factory() as session:
        with pytest.raises(ValidationError):
            create_client(session, "  ")


def test_prevent_overlapping_appointments(session_factory):
    client_id, service_id = setup_records(session_factory)
    with session_factory() as session:
        create_appointment(session, client_id, service_id, datetime(2026, 10, 12, 10, 0))
        with pytest.raises(ValidationError, match="conflito|intervalo"):
            create_appointment(session, client_id, service_id, datetime(2026, 10, 12, 10, 30))


def test_cancelled_appointment_does_not_block_time(session_factory):
    client_id, service_id = setup_records(session_factory)
    with session_factory() as session:
        appointment = create_appointment(session, client_id, service_id, datetime(2026, 10, 12, 10, 0))
        cancel_appointment(session, appointment.id)
        new_appointment = create_appointment(session, client_id, service_id, datetime(2026, 10, 12, 10, 0))
        assert new_appointment.status == "Agendado"

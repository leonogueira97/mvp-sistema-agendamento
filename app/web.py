from datetime import datetime
from flask import Flask, redirect, render_template_string, request, url_for
from sqlalchemy import select
from .database import Base, make_engine, make_session_factory
from .models import Appointment, Client, Service
from .services import ValidationError, cancel_appointment, create_appointment, create_client, create_service


PAGE = """
<!doctype html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MVP — Sistema de Agendamento</title>
  <style>
    :root { font-family: Arial, sans-serif; color: #1f2937; background: #f3f5f8; }
    body { max-width: 1100px; margin: 0 auto; padding: 24px; }
    h1 { margin-bottom: 6px; } .sub { color: #64748b; margin-top: 0; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(260px,1fr)); gap: 16px; }
    section { background: white; border-radius: 12px; padding: 18px; box-shadow: 0 2px 8px #0000000b; margin: 16px 0; }
    input, select, textarea, button { box-sizing: border-box; width: 100%; padding: 10px; margin: 5px 0 10px; border: 1px solid #cbd5e1; border-radius: 7px; font: inherit; }
    button { background: #1d4ed8; color: white; border: 0; cursor: pointer; font-weight: 600; }
    button.secondary { background: #475569; } .error { background: #fee2e2; padding: 10px; border-radius: 8px; color: #991b1b; }
    .success { background: #dcfce7; padding: 10px; border-radius: 8px; color: #166534; }
    table { border-collapse: collapse; width: 100%; } th, td { text-align: left; border-bottom: 1px solid #e2e8f0; padding: 9px 6px; }
    .status { font-size: .9em; } form.inline { display: inline; } form.inline button { width: auto; padding: 6px 9px; margin: 0; }
    @media(max-width:600px) { body { padding: 12px; } table { font-size: .9em; } }
  </style>
</head>
<body>
  <h1>📅 Sistema de Agendamento</h1>
  <p class="sub">MVP para organização de clientes, serviços e horários.</p>
  {% if message %}<p class="{{ 'error' if is_error else 'success' }}">{{ message }}</p>{% endif %}
  <div class="grid">
    <section>
      <h2>Novo cliente</h2>
      <form method="post" action="{{ url_for('clients') }}">
        <label>Nome *</label><input name="name" required maxlength="120">
        <label>Telefone</label><input name="phone" maxlength="40">
        <label>Observações</label><textarea name="notes" rows="2"></textarea>
        <button type="submit">Cadastrar cliente</button>
      </form>
    </section>
    <section>
      <h2>Novo serviço</h2>
      <form method="post" action="{{ url_for('services') }}">
        <label>Nome *</label><input name="name" required maxlength="120">
        <label>Duração (minutos) *</label><input name="duration" type="number" min="1" value="60" required>
        <label>Preço (R$)</label><input name="price" type="number" min="0" step="0.01" value="0.00" required>
        <button type="submit">Cadastrar serviço</button>
      </form>
    </section>
    <section>
      <h2>Novo agendamento</h2>
      {% if clients and services %}
      <form method="post" action="{{ url_for('appointments') }}">
        <label>Cliente *</label><select name="client_id" required>{% for c in clients %}<option value="{{ c.id }}">{{ c.name }}</option>{% endfor %}</select>
        <label>Serviço *</label><select name="service_id" required>{% for s in services %}<option value="{{ s.id }}">{{ s.name }} — {{ s.duration_minutes }} min</option>{% endfor %}</select>
        <label>Data e hora *</label><input type="datetime-local" name="starts_at" required>
        <label>Observações</label><textarea name="notes" rows="2"></textarea>
        <button type="submit">Criar agendamento</button>
      </form>
      {% else %}<p>Cadastre pelo menos um cliente e um serviço antes de agendar.</p>{% endif %}
    </section>
  </div>
  <section>
    <h2>Agendamentos</h2>
    {% if appointments %}
    <table><thead><tr><th>Data/hora</th><th>Cliente</th><th>Serviço</th><th>Status</th><th>Ação</th></tr></thead><tbody>
    {% for a in appointments %}
      <tr><td>{{ a.starts_at.strftime('%d/%m/%Y %H:%M') }}</td><td>{{ a.client.name }}</td><td>{{ a.service.name }}</td><td class="status">{{ a.status }}</td><td>
      {% if a.status != 'Cancelado' %}<form class="inline" method="post" action="{{ url_for('cancel', appointment_id=a.id) }}"><button class="secondary" type="submit">Cancelar</button></form>{% else %}—{% endif %}
      </td></tr>
    {% endfor %}
    </tbody></table>
    {% else %}<p>Nenhum agendamento cadastrado.</p>{% endif %}
  </section>
  <section>
    <h2>Clientes cadastrados</h2>
    {% if clients %}<ul>{% for c in clients %}<li>{{ c.name }}{% if c.phone %} — {{ c.phone }}{% endif %}</li>{% endfor %}</ul>{% else %}<p>Nenhum cliente cadastrado.</p>{% endif %}
  </section>
  <section>
    <h2>Serviços cadastrados</h2>
    {% if services %}<ul>{% for s in services %}<li>{{ s.name }} — {{ s.duration_minutes }} min — R$ {{ '%.2f'|format(s.price_cents / 100) }}</li>{% endfor %}</ul>{% else %}<p>Nenhum serviço cadastrado.</p>{% endif %}
  </section>
</body>
</html>
"""


def create_app(database_url: str = "sqlite:///agendamentos.db", testing: bool = False):
    app = Flask(__name__)
    engine = make_engine(database_url)
    Base.metadata.create_all(engine)
    Session = make_session_factory(engine)
    app.config["TESTING"] = testing

    def page(message=None, is_error=False):
        with Session() as session:
            clients = session.scalars(select(Client).order_by(Client.name)).all()
            services = session.scalars(select(Service).order_by(Service.name)).all()
            appointments = session.scalars(select(Appointment).order_by(Appointment.starts_at.desc())).all()
            return render_template_string(
                PAGE, clients=clients, services=services, appointments=appointments,
                message=message, is_error=is_error
            )

    @app.get("/")
    def index():
        return page()

    @app.post("/clients")
    def clients():
        try:
            with Session() as session:
                create_client(session, request.form.get("name", ""), request.form.get("phone", ""), request.form.get("notes", ""))
            return page("Cliente cadastrado com sucesso.")
        except ValidationError as exc:
            return page(str(exc), True), 400

    @app.post("/services")
    def services():
        try:
            duration = int(request.form.get("duration", "60"))
            price = round(float(request.form.get("price", "0")) * 100)
            with Session() as session:
                create_service(session, request.form.get("name", ""), duration, price)
            return page("Serviço cadastrado com sucesso.")
        except (ValidationError, ValueError) as exc:
            return page(str(exc) or "Informe valores válidos.", True), 400

    @app.post("/appointments")
    def appointments():
        try:
            starts_at = datetime.strptime(request.form.get("starts_at", ""), "%Y-%m-%dT%H:%M")
            with Session() as session:
                create_appointment(
                    session, int(request.form["client_id"]), int(request.form["service_id"]),
                    starts_at, request.form.get("notes", "")
                )
            return page("Agendamento criado com sucesso.")
        except (ValidationError, ValueError, KeyError) as exc:
            return page(str(exc) or "Confira os dados do agendamento.", True), 400

    @app.post("/appointments/<int:appointment_id>/cancel")
    def cancel(appointment_id):
        try:
            with Session() as session:
                cancel_appointment(session, appointment_id)
            return page("Agendamento cancelado.")
        except ValidationError as exc:
            return page(str(exc), True), 404

    return app

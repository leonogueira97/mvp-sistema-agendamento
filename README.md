# MVP — Sistema de Agendamento

Sistema web simples para pequenos negócios de prestação de serviços. O MVP ajuda a centralizar clientes, serviços e agendamentos, reduzindo a dependência de WhatsApp e agenda de papel.

## Funcionalidades

- Cadastro e listagem de clientes.
- Cadastro e listagem de serviços.
- Criação e listagem de agendamentos.
- Validação para impedir conflito de horários para o mesmo profissional/agenda.
- Cancelamento de agendamentos.
- Persistência local com SQLite e SQLAlchemy.
- Testes automatizados com pytest.
- Integração contínua com GitHub Actions.

## Tecnologias

- Python 3.11+
- Flask
- SQLite
- SQLAlchemy
- pytest
- Git e GitHub

## Como executar localmente

1. Instale o Python 3.11 ou superior.
2. Crie e ative um ambiente virtual:

   **Windows (PowerShell):**
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   **macOS/Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicie o sistema:
   ```bash
   python main.py
   ```

5. Abra `http://127.0.0.1:5000` no navegador.

O banco `agendamentos.db` será criado localmente na primeira execução. Esse arquivo não é enviado ao GitHub.

## Executar os testes

```bash
pytest -v
```

## Estrutura do projeto

```text
mvp-sistema-agendamento/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── services.py
│   └── web.py
├── tests/
│   ├── conftest.py
│   ├── test_services.py
│   └── test_web.py
├── .github/
│   └── workflows/
│       └── tests.yml
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## Regras e limitações do MVP

- O sistema é uma versão inicial para demonstração e validação com o responsável pelo negócio.
- Os horários são informados no formato `AAAA-MM-DD HH:MM`.
- Cada agendamento tem duração definida em minutos.
- Nesta versão, os conflitos são verificados para a agenda geral do negócio; não há cadastro de profissionais diferentes.
- Não use dados pessoais reais durante testes públicos. Antes de uso comercial, implemente autenticação, autorização, política de privacidade, backups e controles de segurança adequados.

## Fluxo sugerido para GitHub

1. Crie um repositório chamado `mvp-sistema-agendamento` com visibilidade **Public**.
2. Extraia os arquivos deste pacote para uma pasta local.
3. No terminal, dentro da pasta do projeto, execute:

   ```bash
   git init
   git add .
   git commit -m "feat: cria MVP de sistema de agendamento"
   git branch -M main
   git remote add origin https://github.com/SEU-USUARIO/mvp-sistema-agendamento.git
   git push -u origin main
   ```

4. Substitua `SEU-USUARIO` pelo seu nome de usuário do GitHub.
5. O workflow do GitHub Actions executará os testes quando houver push ou pull request.

## Validação em campo

Registre pelo menos duas rodadas reais de teste com o representante do negócio. Documente as tarefas realizadas, dificuldades observadas, feedback recebido e alterações efetivamente implementadas. Não apresente feedback fictício como se fosse real.

## Revisão técnica

Esta etapa tem como objetivo avaliar a qualidade do código do Sistema de Agendamento, considerando organização, legibilidade, segurança e facilidade de manutenção.

Serão observados os seguintes pontos:

- Organização das responsabilidades da aplicação.
- Validação dos dados de clientes e agendamentos.
- Prevenção de conflitos de horários.
- Segurança nas operações com o banco de dados.
- Oportunidades de simplificação e melhoria do código.

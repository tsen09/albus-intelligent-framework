<div align="center">
    <picture>
        <source
            media="(prefers-color-scheme: dark)"
            srcset=".github/assets/albus-banner-dark.png">
        <img
            src=".github/assets/albus-banner.png"
            alt="Albus"
            width="600">
    </picture>

### A reusable Python backend framework for building intelligent assistants.

**Build intelligent applications without reinventing the backend infrastructure.**

Albus is a modular Python backend framework designed to provide reusable, production-ready foundations for intelligent assistant applications. From API infrastructure and shared utilities to model integrations, authorization, load balancing, observability, and extensible backend services, Albus brings essential building blocks together into a unified framework—allowing developers to focus on application-specific logic and intelligence rather than infrastructure.

<br/>

**Built with**

[![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-Validation-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-1C3C3C?logo=langchain&logoColor=white)](https://www.langchain.com/langgraph)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

</div>

---

## What is Albus?

**Albus** is a reusable, modular Python backend framework designed to serve as the foundational infrastructure for building intelligent assistants and AI-powered applications.

The goal of Albus is to become the **go-to backend infrastructure repository for intelligent assistants** — a centralised foundation where common backend capabilities are developed, maintained, and reused across projects rather than repeatedly implemented in individual applications.

Built with Python, Albus provides a collection of reusable, independently integrable components that can be installed into any compatible project. From API infrastructure and database abstractions to model integrations, authentication and authorisation, load balancing, observability, and shared utilities, Albus aims to bring the essential building blocks of intelligent assistant backends together under a unified framework.

By centralising these capabilities, Albus allows developers to focus on what makes each assistant unique — its intelligence, workflows, domain knowledge, and application-specific functionality — rather than reinventing foundational infrastructure.

Albus is built around **reusability, modularity, extensibility, maintainability, and application independence**, evolving alongside the requirements of modern intelligent assistant systems.

## Features

- **FastAPI Foundation** — Reusable API infrastructure and backend components built around FastAPI.
- **Database Infrastructure** — SQLAlchemy-based database engines, connection management, session handling, and reusable database abstractions.
- **Model Encapsulators** — Unified abstractions for integrating, managing, and interacting with AI and machine learning models while isolating implementation details.
- **Authentication & Authorisation** — Reusable security, authentication, and access-control infrastructure for assistant applications.
- **Load Balancing** — Infrastructure abstractions for distributing workloads and managing scalable service and model integrations.
- **Observability** — Shared capabilities for logging, monitoring, diagnostics, and tracking application behaviour.
- **Shared Utilities** — Centralised, reusable backend utilities and common components available across consuming projects.
- **Environment Configuration** — Flexible configuration management supporting development, testing, and production environments.
- **Modular Architecture** — Independently integrable components designed to minimise coupling and maximise reuse across applications.
- **Extensible Framework** — Designed to evolve with new infrastructure capabilities, integrations, and requirements.
- **Python Native** — Built for modern Python applications with maintainable, type-friendly interfaces.

---
## Development Status

> **Albus is currently under active development.**
>
> The project is focused on establishing a reusable, modular Python backend foundation for intelligent assistants and AI-powered applications.
>
> Current development efforts are focused on building and refining core backend infrastructure, including FastAPI components, database utilities, logging, exception handling, model encapsulators, configuration management, and other shared services.
>
> The framework is being designed to be application-independent, allowing its components to be integrated, installed, and reused across multiple projects without coupling them to specific application logic or domains.
>
> **The objective is to evolve Albus into the go-to backend infrastructure framework for building scalable, maintainable, and production-ready intelligent assistants.**

---

## Design Principles

Albus is built around the following principles to establish a reliable, reusable, and extensible backend foundation for intelligent assistants:

- **Reusability** — Develop common backend capabilities once and make them available across multiple intelligent assistant projects.
- **Modularity** — Design components as cohesive, independently integrable modules with minimal dependencies on other framework components.
- **Separation of Concerns** — Keep backend infrastructure, application-specific business logic, and assistant intelligence decoupled.
- **Extensibility** — Provide flexible foundations that can evolve with new models, integrations, infrastructure capabilities, and application requirements.
- **Consistency** — Establish standardised interfaces, configurations, and backend behaviour across consuming applications.
- **Scalability** — Build infrastructure capable of supporting growing workloads, expanding integrations, and increasingly complex assistant architectures.
- **Reliability** — Prioritise robust, predictable, and maintainable infrastructure suitable for production-oriented applications.
- **Maintainability** — Centralise shared functionality, reduce duplication, and simplify improvements across the ecosystem.
- **Application Independence** — Keep Albus generic and domain-agnostic, allowing it to serve as the backend foundation for assistants across different domains and use cases.

---

## ⚙️ Setup & Usage

Follow these steps to clone, set up, and install Albus locally.

### Prerequisites

- **Git** – Required to clone the repository.
- **curl** – Required by the setup script to install [uv](https://docs.astral.sh/uv/) automatically if it is not already available.

**Note:** Python 3.13+ and `uv` do not need to be installed beforehand. Albus's setup script handles their installation automatically.

### 1. Clone the Repository

```bash
git clone https://github.com/tsen09/albus-intelligent-framework.git
cd albus-intelligent-framework
```

### 2. Set Up Albus

Run the setup command to create the Python virtual environment and install the required dependencies using `uv`.

```bash
./albus.sh setup
```

Alternatively, use the shorthand:

```bash
./albus.sh -s
```

### 3. Configure the Environment

Before developing or testing Albus, configure the environment variables.

Create a `.env` file in the project root using the provided example:

```bash
cp .env.example .env
```

Set the appropriate environment in `.env`:

```dotenv
ENV="development"
```

Albus automatically loads the corresponding TOML configuration file from `backend/config/`:

| Environment | Configuration file |
|---|---|
| Development | `backend/config/development.toml` |
| Testing | `backend/config/testing.toml` |
| Staging | `backend/config/staging.toml` |
| Production | `backend/config/production.toml` |

Update the selected TOML file with the appropriate application, database, and Python runtime settings.

### 4. Install Albus as a Package

To make Albus available for import within your local Python environment, install it in editable mode:

```bash
uv pip install -e .
```

Editable installation allows changes to the Albus source code to be reflected without reinstalling the package.

This is particularly useful when developing Albus alongside other intelligent assistant projects that consume it as a dependency.

### 5. Verify the Installation

Verify that Albus is installed in the active Python environment:

```bash
uv pip show albus
```

You can also verify that Python can locate the installed package:

```bash
uv run python -c "import albus; print('Albus installed successfully.')"
```

**Note:** The import statement assumes the package exposes `albus` as its Python import namespace.

### 6. Integrate Albus into Other Projects

Once installed, Albus can be used as a shared backend dependency across compatible Python projects.

For local development, install it directly from its repository:

```bash
uv pip install -e /path/to/albus
```

Alternatively, add Albus as a Git dependency in another project's `pyproject.toml`:

```toml
[project]
dependencies = [
    "albus @ git+https://github.com/tsen09/albus.git"
]
```

This allows consuming applications to reuse Albus's backend infrastructure without duplicating its implementation.

### 7. Uninstall Albus

To remove Albus's local Python environment and generated build/cache artifacts:

```bash
./albus.sh --remove
```

Alternatively:

```bash
./albus.sh -r
```

Albus will ask for confirmation before proceeding. Enter `y` to confirm or `n` to cancel.

To skip the confirmation prompt:

```bash
./albus.sh --remove --yes
```

**Note:** Uninstallation preserves your source code, Git history, documentation, environment configuration, and shared system dependencies. It does not uninstall Python, `uv`, or any system-wide database installations.

### CLI Reference

| Command | Description |
|---|---|
| `./albus.sh setup` | Set up the project environment |
| `./albus.sh -s` | Set up the project environment (shorthand) |
| `./albus.sh run` | Run the configured development application, if applicable |
| `./albus.sh --remove` | Uninstall Albus's local environment and generated artifacts |
| `./albus.sh -r` | Uninstall Albus (shorthand) |
| `./albus.sh --remove --yes` | Uninstall Albus without confirmation |
| `./albus.sh --version` | Display the project version |
| `./albus.sh --help` | Display available commands |

---

## Acknowledgements

Albus builds upon the work and contributions of the open-source community.

- [fastapi-langgraph-agent-production-ready-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template) by [wassim249](https://github.com/wassim249) — The original project from which Albus was forked, providing an initial foundation for development.
- [FastAPI](https://github.com/fastapi/fastapi) — An excellent Python framework for building modern, high-performance APIs.

We gratefully acknowledge the developers, maintainers, and contributors of these projects and the broader open-source ecosystem that makes Albus possible.

## Author

Albus is created and maintained by [Tanmoy Sen](https://github.com/tsen09).

This project is an exploration of reusable backend infrastructure, intelligent assistant architectures, model integrations, and the engineering foundations required to build scalable, maintainable AI-powered applications.

If you find the project interesting, consider starring the repository, sharing your feedback, or contributing ideas and improvements.

Built with a vision to establish a shared foundation for the next generation of intelligent assistants.

[GitHub: @tsen09](https://github.com/tsen09)

---

## 📄 License

Albus is distributed under the [MIT License](LICENSE).

---
<div align="center">
    <picture>
        <source
            media="(prefers-color-scheme: dark)"
            srcset=".github/assets/albus-banner-dark.png">
        <img
            src=".github/assets/albus-banner.png"
            alt="Albus"
            width="800">
    </picture>

### A reusable Python backend foundation for intelligent assistants.

**Build intelligent applications without rebuilding the backend infrastructure.**

Albus is a modular Python backend framework providing reusable infrastructure for intelligent assistant applications — from API foundations and database utilities to logging, exception handling, model integrations, and shared backend components.

</div>

---

## What is Albus?

**Albus** is a reusable backend framework designed to simplify the development of intelligent assistants and AI-powered applications.

Built with Python, Albus provides a collection of modular, reusable backend components that can be installed and imported into any compatible Python project. Rather than repeatedly implementing infrastructure for every assistant, developers can leverage Albus as a shared foundation and focus on application-specific logic, intelligence, and functionality.

Albus is designed to be **application-independent, modular, extensible, and reusable** across projects.

## ✨ Features

- **FastAPI Foundation** — Reusable backend components and API infrastructure built around FastAPI.
- **Database Utilities** — SQLAlchemy-based database engines, connection management, session helpers, and database abstractions.
- **Model Encapsulators** — Abstractions for integrating and interacting with AI models while keeping implementation details isolated.
- **Reusable Components** — Importable utilities and backend modules designed to be shared across multiple applications.
- **Environment Configuration** — Configurable application behaviour across development, testing, and production environments.
- **Modular Architecture** — Components can be integrated independently without coupling the framework to a specific assistant or application.
- **Python Native** — Built for modern Python applications with type-friendly, maintainable code.

## 🧩 Core Components

### FastAPI Backend

Provides reusable backend capabilities and foundations for building API-driven applications using FastAPI.

Designed to support application-specific API development while keeping shared backend functionality centralised.

### Database Utilities

Database helpers built around SQLAlchemy, intended to simplify database configuration, connection management, engine creation, session handling, and common database operations.

Supports a reusable database layer that can be integrated into multiple applications.

This allows applications to maintain consistent error semantics while avoiding repeated exception implementations.

### Model Encapsulators

Model encapsulators provide reusable abstractions for integrating AI and machine learning models.

They help isolate model-specific implementation details behind consistent interfaces, making it easier for consuming applications to integrate, manage, and interact with different models.

### Shared Utilities

A collection of common backend utilities that support application development while remaining independent of any particular application's business logic.

## 🎯 Design Principles

Albus is developed around the following principles:

- **Reusability** — Build once, integrate across multiple projects.
- **Modularity** — Components should remain independently usable wherever practical.
- **Separation of Concerns** — Infrastructure should remain separate from application-specific business logic.
- **Extensibility** — Components should support future integrations and enhancements.
- **Consistency** — Provide common interfaces and standardised backend behaviour across applications.
- **Maintainability** — Centralise shared functionality to reduce duplication and simplify maintenance.

## 🙏 Acknowledgements

Albus is being developed from a fork of [fastapi-langgraph-agent-production-ready-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template) by [wassim249](https://github.com/wassim249). We gratefully acknowledge the original project and its contributions as the foundation for this work.

We also thank the open-source community and the developers of the technologies and libraries that make Albus possible.

## 📄 License

Albus is distributed under the [MIT License](LICENSE).

This project is based on a fork of [fastapi-langgraph-agent-production-ready-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template), which is also licensed under the MIT License. The original license and copyright notices are retained in accordance with its terms.
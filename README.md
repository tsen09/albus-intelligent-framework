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

This project is based on a fork of [fastapi-langgraph-agent-production-ready-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template), which is also licensed under the MIT License. The original license and copyright notices are retained in accordance with its terms.

---
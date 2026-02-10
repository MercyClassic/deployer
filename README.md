# 🚀 Deployment Automation System via Telegram Bot

## The goal of the project:
- clean architecture
- Domain-Driven Design (DDD)
- interaction with remote servers via SSH
- configuration-driven deployments

---

## ✨ Key Features

- 🤖 **Telegram bot interface** for all user interactions  
- 👥 **Multi-user support** — each user can manage multiple projects  
- 📦 **Multiple deployment strategies**:
  - `shell` — run custom shell commands
  - `git` — clone repository and run entrypoint
  - `docker` — pull image and run container
- 🗂 **Versioned deployment configurations**
- 🔐 **Encrypted secrets storage** (SSH credentials, env vars, registry auth)
- 🖥 **Deploy to multiple servers via SSH**
- 📊 **Deployment status and logs (stdout / stderr)**

---

## 🧱 Architecture Overview

The project follows **Domain-Driven Design (DDD)** principles.

### Aggregates

- **Project** (Aggregate Root)
  - owns servers
  - owns configuration with versions by strategy
  - enforces invariants (one active config, strategy consistency)

- **Deployment** (Aggregate Root)
  - represents a single deployment execution
  - owns deployment logs
  - immutable by design (history)

---

## 🛠 Tech Stack

- **Python 3.13**
- **aiogram 3** + **aiogram_dialog** — Telegram bot framework
- **paramiko** — SSH connections
- **PostgresSQL** — persistent storage
- **SQLAlchemy** — ORM
- **dishka** — ioc container
- **YAML / JSON** — configuration format
- **Type hints** everywhere ✅

---

## 🤖 Telegram Bot Commands

The bot interface (just several examples):

### Main Menu
![Main Menu](docs/images/entry.png)

*Entry point with Projects and Profile options*

### Project Management
![Project List](docs/images/project_list.png)

*List of all projects with create button*

![Project Info](docs/images/project_info.png)

*Detailed project information with actions*

![Project Config](docs/images/project_config.png)

*Project configuration management*

![Server List](docs/images/server_list.png)

*Manage project servers - add, remove, view details*

### Deployment Management
![Deploy History](docs/images/deploy_history.png)

*View deployment history, run new deployments, check logs*

### User Profile
![User profile](docs/images/profile.png)

*View user profile*

### Navigation
- Use **Projects** button to access project management
- Each project has: Config, Servers, Deployments sections
- Back buttons use smart navigation between states
- All data is validated according to deployment strategy

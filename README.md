EMR-CRM (Electronic Repair Shop Management)
===========================================

A Minimum Viable Product (MVP) CRM designed to streamline operations for electronic repair shops. This application manages the full lifecycle of a repair job, from customer intake and device tracking to quotations, payments, and final service reporting.

🚀 Tech Stack
-------------

-   Backend: Python 3.11+ & Django
-   Package Manager: [UV](https://github.com/astral-sh/uv) (Fast Python package installer and resolver)
-   Database: PostgreSQL
-   Containerization: Docker & Docker Compose
-   Web Server: Nginx
-   Frontend: Tailwind CSS (Django Templates)

* * * * *

✨ Features
----------

-   User Management: Secure authentication and role-based access for staff.
-   Customer Management: CRUD interface for client details and history.
-   Device Tracking: Register devices with details (IMEI, Serial Number, Model) and track their repair status.
-   Repair Workflow: Manage the full repair lifecycle (Intake, Technical Assessment, Repair, Ready for Pickup).
-   Quotations: Generate and manage quotes for repair services.
-   Payments: Record and track customer payments.
-   Document Generation: Job orders and service reports.
-   Testing: Comprehensive test suite using Pytest.

* * * * *

📂 Project Structure
--------------------

The project follows a modular Django app structure, categorized alphabetically for clarity:

-   `a_users`: Custom user model, authentication, and permissions.
-   `b_customers`: Customer profiles and management logic.
-   `c_devices`: Device registration and tracking.
-   `d_repairs`: Core repair logic, job orders, and status management.
-   `e_quotations`: Quote generation and item management.
-   `f_payments`: Payment processing and history.
-   `z_core`: Shared utilities, logging, and common models.
-   `config`: Django project settings and URL routing.
-   `templates`: Base HTML templates, Tailwind components, and layout structures.
-   `static`: Compiled CSS/JS assets and images.

```
emr-crm/

├── a_users/              # User profiles, auth, and permissions
├── b_customers/          # Client management logic
├── c_devices/            # Hardware/Device tracking
├── d_repairs/            # Core Repair Job Orders & workflow
├── e_quotations/         # Quotation generation and PDF printing
├── f_payments/           # Transaction and billing records
├── z_core/               # Shared utilities, base models, and logging
├── config/               # Django settings and main URL routing
├── static/               # Global CSS (Tailwind), JS, and Images
├── templates/            # Global UI layout & shared components
├── tests/                # Global test suite (Pytest)
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Local development orchestration
├── makefile              # Shortcuts for frequent commands
├── pyproject.toml        # Python dependencies (uv)
└── manage.py             # Django entry point
```

🛠️ Getting Started
-------------------

### Prerequisites

-   Docker & Docker Compose installed.
-   (Optional) UV installed if running locally without Docker.

* * * * *

### 1\. Clone the Repository

Bash

```
git clone <repository-url>
cd emr-crm
```
### 2\. Environment Variables

Copy the example environment file and fill in the required values.

Bash

```
cp .env.example .env
```

### 3\. Build and Run with Docker

Use Docker Compose to build the images and start the containers.

Bash

```
docker-compose up --build -d
```

Once the containers are running, apply database migrations and create a superuser.

Bash

```
# Apply migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### 4\. Access the Application

Navigate to `http://localhost:8000` in your browser.

🧪 Testing
----------

To run the test suite locally:

Bash

```
docker-compose exec web python -m pytest
```

Or using the `makefile` convenience commands:

Bash

```
make test
```

* * * * *

📄 License
----------

This project is proprietary software intended for internal use.
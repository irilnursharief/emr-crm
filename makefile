# Variables
COMPOSE = docker compose
EXEC = $(COMPOSE) exec web
UV = uv run python manage.py

# ---- Docker Ops ----
up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

build:
	$(COMPOSE) build

logs:
	$(COMPOSE) logs -f

# ---- Django ----
migrate:
	$(EXEC) $(UV) migrate

makemigrations:
	$(EXEC) $(UV) makemigrations

shell:
	$(EXEC) $(UV) shell

superuser:
	$(EXEC) $(UV) createsuperuser

collectstatic:
	$(EXEC) $(UV) collectstatic --noinput

# ---- Tailwind ----
# Note: This assumes you have the tailwind binary in your project root or tools folder 
# and it's being synced into the container via volumes.
tailwind-watch:
	./tools/tailwindcss.exe -i static/css/input.css -o static/css/output.css --watch

tailwind-build:
	./tools/tailwindcss.exe -i static/css/input.css -o static/css/output.css --minify

# ---- Combined (Development Mode) ----
# This starts the containers, then runs the Django dev server AND tailwind watch locally.
# We run Django locally with uv for the best hot-reload experience.
dev:
	@echo "Starting Docker Database..."
	$(COMPOSE) up -d db
	@echo "Starting Django + Tailwind..."
	@start "" "C:\Program Files\Git\bin\bash.exe" -lc "uv run manage.py runserver; exec bash"
	@start "" "C:\Program Files\Git\bin\bash.exe" -lc "./tools/tailwindcss.exe -i static/css/input.css -o static/css/output.css --watch; exec bash"
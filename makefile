# ---- Django ----
run:
	uv run manage.py runserver

migrate:
	uv run manage.py migrate

makemigrations:
	uv run manage.py makemigrations

shell:
	uv run manage.py shell

superuser:
	uv run manage.py createsuperuser

# ---- Tailwind ----
tailwind:
	./tools/tailwindcss.exe -i static/css/input.css -o static/css/output.css --watch

tailwind-build:
	./tools/tailwindcss.exe -i static/css/input.css -o static/css/output.css --minify

# ---- Combined (dev mode) ----
dev:
	@echo "Starting Django + Tailwind in Git Bash terminals..."
	@start "" "C:\Program Files\Git\bin\bash.exe" -lc "uv run manage.py runserver; exec bash"
	@start "" "C:\Program Files\Git\bin\bash.exe" -lc "./tools/tailwindcss.exe -i static/css/input.css -o static/css/output.css --watch; exec bash"
build:
	docker compose up -d 
	docker exec -t cutter_bot /opt/bot/venv/bin/alembic upgrade head

rebuild:
	docker compose up --force-recreate --build -d 

upgradedb:
	docker exec -t cutter_bot /opt/bot/venv/bin/alembic upgrade head
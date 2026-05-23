# 🌤 Weather Tracker

Fetches live weather data every 60 seconds using the
[Open-Meteo API](https://open-meteo.com/) and stores it in PostgreSQL.
Built as Phase 1 of an MLOps/DevOps learning roadmap.

## Stack
- Python 3.11
- Open-Meteo API (no key needed)
- PostgreSQL 15
- Docker + Docker Compose

## Run locally

1. Clone the repo
```bash
   git clone https://github.com/Parth-234/weather-tracker.git
   cd weather-tracker
```
2. Copy the env file and edit your city
```bash
   cp .env.example .env
```
3. Start everything
```bash
   docker compose up --build
```

## Check the data
```bash
docker exec -it weather_db psql -U weather_user -d weatherdb \
  -c "SELECT * FROM weather_logs ORDER BY fetched_at DESC LIMIT 10;"
```

## Docker Hub
```bash
docker pull parthsanghi/weather-tracker:latest
```

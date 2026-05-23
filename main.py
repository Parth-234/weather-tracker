import os
import time
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Config from .env ──────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_NAME     = os.getenv("DB_NAME", "weatherdb")
DB_USER     = os.getenv("DB_USER", "weather_user")
DB_PASS     = os.getenv("DB_PASSWORD", "weather_pass")
CITY        = os.getenv("CITY_NAME", "Delhi")
LAT         = float(os.getenv("LATITUDE",  "28.6139"))
LON         = float(os.getenv("LONGITUDE", "77.2090"))
INTERVAL    = int(os.getenv("FETCH_INTERVAL", "600"))   # seconds

# ── Database ──────────────────────────────────────────────────
def connect_db():
    """Retry connecting until Postgres is ready."""
    for attempt in range(15):
        try:
            conn = psycopg2.connect(
                host=DB_HOST, dbname=DB_NAME,
                user=DB_USER, password=DB_PASS
            )
            print("Connected to database.")
            return conn
        except psycopg2.OperationalError:
            print(f"Waiting for database... ({attempt + 1}/15)")
            time.sleep(3)
    raise RuntimeError("Could not connect to database after 15 attempts.")

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS weather_logs (
                id           SERIAL PRIMARY KEY,
                city         VARCHAR(100),
                temperature  FLOAT,
                humidity     INT,
                wind_speed   FLOAT,
                weather_code INT,
                fetched_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    conn.commit()
    print("Table ready.")

def insert_weather(conn, data):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO weather_logs
                (city, temperature, humidity, wind_speed, weather_code)
            VALUES (%s, %s, %s, %s, %s)
        """, (CITY, data["temperature"], data["humidity"],
              data["wind_speed"], data["weather_code"]))
    conn.commit()

# ── Weather API ───────────────────────────────────────────────
def fetch_weather():
    """Call Open-Meteo API to get current weather data."""
    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude":  LAT,
            "longitude": LON,
            "current":   "temperature_2m,relative_humidity_2m,"
                         "wind_speed_10m,weather_code",
            "timezone":  "auto",
        },
        timeout=10,
    )
    resp.raise_for_status()
    c = resp.json()["current"]
    return {
        "temperature":  c["temperature_2m"],
        "humidity":     c["relative_humidity_2m"],
        "wind_speed":   c["wind_speed_10m"],
        "weather_code": c["weather_code"],
    }

# ── Main loop ─────────────────────────────────────────────────
def main():
    print(f"Weather Tracker starting for {CITY} ...")
    conn = connect_db()
    create_table(conn)

    while True:
        try:
            data = fetch_weather()
            insert_weather(conn, data)
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}]  "
                f"{CITY}: {data['temperature']}°C  "
                f"{data['humidity']}%  "
                f"{data['wind_speed']} km/h"
            )
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
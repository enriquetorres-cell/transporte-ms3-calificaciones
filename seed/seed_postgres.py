"""Siembra usuarios, conductores y vehiculos de MS1 (PostgreSQL).
Uso:  PG_DSN="host=10.0.2.x dbname=usuarios_db user=app_ms1 password=..." python3 seed_postgres.py
Se corre PRIMERO: los IDs que genera son la fuente de verdad para MySQL y Mongo.
"""
import io
import os
import random
from datetime import timedelta

import psycopg2
from comun import (fake, DISTRITOS, TIPOS_SERVICIO, N_USUARIOS,
                   N_CONDUCTORES, N_VEHICULOS, FECHA_INICIO)

DSN = os.environ.get("PG_DSN", "host=localhost dbname=usuarios_db user=postgres password=postgres")
cn = psycopg2.connect(DSN)
cur = cn.cursor()

print("Vaciando tablas...")
cur.execute("TRUNCATE vehiculos, conductores, usuarios RESTART IDENTITY CASCADE;")
cn.commit()

# --- usuarios: COPY es mucho mas rapido que INSERT ---
buf = io.StringIO()
for i in range(1, N_USUARIOS + 1):
    buf.write("\t".join([
        str(i), fake.first_name(), fake.last_name(),
        f"usuario{i}@ejemplo.com", fake.msisdn()[:9],
        random.choice(DISTRITOS),
        fake.date_of_birth(minimum_age=18, maximum_age=70).isoformat(),
        (FECHA_INICIO - timedelta(days=random.randint(0, 900))).isoformat(),
        "true",
    ]) + "\n")
buf.seek(0)
cur.copy_from(buf, "usuarios", columns=(
    "id", "nombre", "apellido", "email", "telefono", "distrito",
    "fecha_nacimiento", "fecha_registro", "activo"))
cn.commit()
print(f"  usuarios: {N_USUARIOS:,}")

# --- conductores ---
buf = io.StringIO()
for i in range(1, N_CONDUCTORES + 1):
    buf.write("\t".join([
        str(i), fake.first_name(), fake.last_name(),
        f"conductor{i}@ejemplo.com", fake.msisdn()[:9],
        f"Q{i:08d}", random.choice(DISTRITOS),
        (FECHA_INICIO - timedelta(days=random.randint(30, 1800))).date().isoformat(),
        "0", "true",
    ]) + "\n")
buf.seek(0)
cur.copy_from(buf, "conductores", columns=(
    "id", "nombre", "apellido", "email", "telefono", "nro_licencia",
    "distrito_base", "fecha_ingreso", "calificacion_promedio", "activo"))
cn.commit()
print(f"  conductores: {N_CONDUCTORES:,}")

# --- vehiculos: uno por conductor ---
MARCAS = {"Toyota": ["Yaris", "Corolla", "Rav4"], "Hyundai": ["Accent", "Elantra", "Tucson"],
          "Kia": ["Rio", "Cerato", "Sportage"], "Nissan": ["Versa", "Sentra", "Kicks"],
          "Chevrolet": ["Sail", "Onix", "Tracker"]}
buf = io.StringIO()
for i in range(1, N_VEHICULOS + 1):
    marca = random.choice(list(MARCAS))
    buf.write("\t".join([
        str(i), str(i), f"{random.choice('ABCDEFGHJ')}{random.randint(1,9)}{random.choice('ABCDEFGHJ')}-{random.randint(100,999)}",
        marca, random.choice(MARCAS[marca]), str(random.randint(2014, 2026)),
        random.choice(["blanco", "negro", "gris", "plata", "azul", "rojo"]),
        str(random.choice([4, 4, 4, 5, 7])),
        random.choice(TIPOS_SERVICIO),
    ]) + "\n")
buf.seek(0)
cur.copy_from(buf, "vehiculos", columns=(
    "id", "conductor_id", "placa", "marca", "modelo", "anio",
    "color", "capacidad", "tipo_servicio"))
cn.commit()
print(f"  vehiculos: {N_VEHICULOS:,}")

for t in ("usuarios", "conductores", "vehiculos"):
    cur.execute(f"SELECT setval(pg_get_serial_sequence('{t}','id'), (SELECT MAX(id) FROM {t}));")
    cur.execute(f"SELECT COUNT(*) FROM {t};")
    print(f"OK  {t}: {cur.fetchone()[0]:,}")
cn.commit()
cur.close(); cn.close()

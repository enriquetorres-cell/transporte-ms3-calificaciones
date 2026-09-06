"""Siembra tarifas, viajes y paradas de MS2 (MySQL) con >=20,000 viajes.
Uso:  MYSQL_HOST=10.0.2.x MYSQL_USER=app_ms2 MYSQL_PASS=... python3 seed_mysql.py
Se corre DESPUES de seed_postgres.py: referencia sus IDs de pasajero y conductor.
"""
import os
import random
from datetime import timedelta

import mysql.connector
from comun import (fake, DISTRITOS, METODOS_PAGO, TIPOS_SERVICIO,
                   N_VIAJES, N_CONDUCTORES, FECHA_INICIO, MINUTOS_RANGO)

LOTE = 2_000

cn = mysql.connector.connect(
    host=os.environ.get("MYSQL_HOST", "localhost"),
    user=os.environ.get("MYSQL_USER", "root"),
    password=os.environ.get("MYSQL_PASS", ""),
    database=os.environ.get("MYSQL_DB", "viajes_db"),
)
cur = cn.cursor()

print("Vaciando tablas...")
cur.execute("SET FOREIGN_KEY_CHECKS=0;")
for t in ("paradas", "viajes", "tarifas"):
    cur.execute(f"TRUNCATE TABLE {t};")
cur.execute("SET FOREIGN_KEY_CHECKS=1;")
cn.commit()

# --- tarifas ---
TARIFAS = [
    (1, "economico", 4.00, 1.10, 0.25, 1.20, "2026-01-01"),
    (2, "estandar",  5.50, 1.45, 0.32, 1.35, "2026-01-01"),
    (3, "confort",   8.00, 1.95, 0.45, 1.50, "2026-01-01"),
    (4, "xl",       11.00, 2.40, 0.55, 1.60, "2026-01-01"),
]
cur.executemany(
    """INSERT INTO tarifas (id, nombre, tarifa_base, costo_km, costo_minuto,
                            multiplicador_hora_pico, vigente_desde)
       VALUES (%s,%s,%s,%s,%s,%s,%s)""", TARIFAS)
cn.commit()
print("  tarifas: 4")

# --- viajes ---
SQL_VIAJE = """INSERT INTO viajes
  (id, pasajero_id, conductor_id, vehiculo_id, tarifa_id,
   distrito_origen, distrito_destino, direccion_origen, direccion_destino,
   distancia_km, duracion_min, monto_total, metodo_pago, estado,
   solicitado_en, iniciado_en, finalizado_en)
  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

HORAS_PICO = {7, 8, 9, 18, 19, 20}
lote, insertados = [], 0

for i in range(1, N_VIAJES + 1):
    conductor_id = random.randint(1, N_CONDUCTORES)
    tarifa = random.choices(TARIFAS, weights=[30, 45, 18, 7])[0]
    solicitado = FECHA_INICIO + timedelta(minutes=random.randint(0, MINUTOS_RANGO))
    espera = timedelta(minutes=random.randint(1, 9))
    iniciado = solicitado + espera

    km = round(random.uniform(1.2, 28.0), 2)
    duracion = max(4, int(km * random.uniform(2.2, 4.0)))
    mult = float(tarifa[5]) if iniciado.hour in HORAS_PICO else 1.0
    monto = round((float(tarifa[2]) + km * float(tarifa[3]) + duracion * float(tarifa[4])) * mult, 2)

    # Los primeros 22,000 viajes quedan finalizados: son los que MS3 califica.
    estado = "finalizado" if i <= 22_000 else random.choice(["cancelado", "finalizado"])
    finalizado = iniciado + timedelta(minutes=duracion) if estado == "finalizado" else None
    origen, destino = random.sample(DISTRITOS, 2)

    lote.append((
        i, random.randint(1, 2_000), conductor_id, conductor_id, tarifa[0],
        origen, destino, fake.street_address()[:150], fake.street_address()[:150],
        km, duracion, monto, random.choice(METODOS_PAGO), estado,
        solicitado, iniciado if estado != "cancelado" else None, finalizado,
    ))

    if len(lote) == LOTE:
        cur.executemany(SQL_VIAJE, lote)
        cn.commit()
        insertados += len(lote)
        lote = []
        print(f"  {insertados:,} viajes")

if lote:
    cur.executemany(SQL_VIAJE, lote)
    cn.commit()
    insertados += len(lote)

# --- paradas: 0 a 2 por viaje ---
SQL_PARADA = """INSERT INTO paradas (viaje_id, orden, direccion, distrito, latitud, longitud, llego_en)
                VALUES (%s,%s,%s,%s,%s,%s,%s)"""
lote, total_paradas = [], 0
for viaje_id in range(1, N_VIAJES + 1):
    for orden in range(1, random.choices([1, 2, 3], weights=[55, 33, 12])[0]):
        lote.append((
            viaje_id, orden, fake.street_address()[:150], random.choice(DISTRITOS),
            round(random.uniform(-12.20, -11.95), 6), round(random.uniform(-77.15, -76.90), 6),
            FECHA_INICIO + timedelta(minutes=random.randint(0, MINUTOS_RANGO)),
        ))
    if len(lote) >= LOTE:
        cur.executemany(SQL_PARADA, lote); cn.commit()
        total_paradas += len(lote); lote = []
if lote:
    cur.executemany(SQL_PARADA, lote); cn.commit(); total_paradas += len(lote)

for t in ("tarifas", "viajes", "paradas"):
    cur.execute(f"SELECT COUNT(*) FROM {t};")
    print(f"OK  {t}: {cur.fetchone()[0]:,}")
cur.close(); cn.close()

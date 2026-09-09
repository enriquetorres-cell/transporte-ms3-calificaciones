"""Siembra la coleccion 'calificaciones' de MS3 con >=20,000 documentos.
Uso:  MONGO_URI="mongodb://..." python3 seed_mongo.py
Correr desde una MV, no desde una laptop: la base es privada.
"""
import os
import random
from datetime import timedelta

import mysql.connector
from comentarios import comentario_para, RESPUESTAS, MOTIVO_DETALLE
from pymongo import MongoClient, ASCENDING, DESCENDING
from comun import (fake, DISTRITOS, TAGS_POSITIVOS, TAGS_NEGATIVOS,
                   N_CALIFICACIONES, N_USUARIOS, FECHA_INICIO, MINUTOS_RANGO)

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/calificaciones_db")
LOTE = 2_000

# El pasajero y el conductor de una calificacion son los del viaje que se califica.
# Se leen de MySQL en vez de sortearlos: sorteados por separado no coinciden con
# viajes.pasajero_id / viajes.conductor_id y cualquier join Mongo-MySQL sale mal.
# Por eso seed_mysql.py tiene que haber corrido antes (ver README, orden de ejecucion).
print("Leyendo los viajes ya sembrados en MySQL...")
cn_my = mysql.connector.connect(
    host=os.environ.get("MYSQL_HOST", "localhost"),
    user=os.environ.get("MYSQL_USER", "root"),
    password=os.environ.get("MYSQL_PASS", ""),
    database=os.environ.get("MYSQL_DB", "viajes_db"),
)
cur_my = cn_my.cursor()
cur_my.execute(
    "SELECT id, pasajero_id, conductor_id FROM viajes WHERE id <= %s",
    (N_CALIFICACIONES,),
)
VIAJES = {vid: (pid, cid) for vid, pid, cid in cur_my}
cur_my.close()
cn_my.close()

faltan = N_CALIFICACIONES - len(VIAJES)
if faltan > 0:
    raise SystemExit(
        f"MySQL devolvio {len(VIAJES):,} viajes con id <= {N_CALIFICACIONES:,};"
        f" faltan {faltan:,}. Corre seed_mysql.py antes que este script."
    )
print(f"  {len(VIAJES):,} viajes leidos")

cli = MongoClient(MONGO_URI)
db = cli.get_default_database()
col = db["calificaciones"]

print("Limpiando coleccion (la carga es 'por unica vez', asi el script es repetible)...")
col.drop()

docs, insertados = [], 0
for viaje_id in range(1, N_CALIFICACIONES + 1):
    rating = random.choices([1, 2, 3, 4, 5], weights=[3, 5, 12, 35, 45])[0]
    pool = TAGS_POSITIVOS if rating >= 4 else TAGS_NEGATIVOS + TAGS_POSITIVOS[:2]
    fecha = FECHA_INICIO + timedelta(minutes=random.randint(0, MINUTOS_RANGO))
    origen, destino = random.sample(DISTRITOS, 2)

    pasajero_id, conductor_id = VIAJES[viaje_id]

    doc = {
        "viaje_id": viaje_id,
        "pasajero_id": pasajero_id,
        "conductor_id": conductor_id,
        "rating": rating,
        "tags": random.sample(pool, k=random.randint(0, min(3, len(pool)))),
        "comentario": comentario_para(rating) if random.random() < 0.8 else "",
        "idioma": "es",
        "distrito_origen": origen,
        "distrito_destino": destino,
        "anonimo": random.random() < 0.12,
        "moderacion": {"estado": "publicado", "reportes": 0},
        "creado_en": fecha,
        "actualizado_en": fecha,
    }
    if rating <= 2 and random.random() < 0.4:
        doc["respuesta_conductor"] = {
            "texto": random.choice(RESPUESTAS),
            "fecha": fecha + timedelta(hours=2),
        }
    docs.append(doc)

    if len(docs) == LOTE:
        col.insert_many(docs, ordered=False)
        insertados += len(docs)
        docs = []
        print(f"  {insertados:,} documentos")

if docs:
    col.insert_many(docs, ordered=False)
    insertados += len(docs)

print("Creando indices...")
col.create_index([("viaje_id", ASCENDING)], unique=True)
col.create_index([("conductor_id", ASCENDING), ("creado_en", DESCENDING)])
col.create_index([("tags", ASCENDING)])
col.create_index([("comentario", "text")], default_language="spanish")

# Reportes de moderacion
rep = db["reportes"]
rep.drop()
muestra = list(col.aggregate([{"$match": {"rating": {"$lte": 2}}}, {"$sample": {"size": 300}}]))
if muestra:
    rep.insert_many([{
        "calificacion_id": c["_id"],
        "reportado_por": random.randint(1, N_USUARIOS),
        "motivo": random.choice(["lenguaje_ofensivo", "informacion_falsa", "spam", "otro"]),
        "detalle": MOTIVO_DETALLE,
        "estado": "pendiente",
        "creado_en": c["creado_en"],
        "actualizado_en": c["creado_en"],
    } for c in muestra])
    rep.create_index([("calificacion_id", ASCENDING), ("estado", ASCENDING)])

print(f"\nOK  calificaciones: {col.count_documents({}):,}")
print(f"OK  reportes:      {rep.count_documents({}):,}")

"""Catalogos y semilla compartidos por los tres scripts de fake data.
Contrato Cero, seccion 3: los mismos valores en las tres bases o los joins de Athena salen vacios.
"""
import random
from faker import Faker

SEMILLA = 42
fake = Faker("es_ES")
Faker.seed(SEMILLA)
random.seed(SEMILLA)

DISTRITOS = [
    "Miraflores", "San Isidro", "Surco", "Barranco", "La Molina", "Lince",
    "Jesús María", "San Borja", "Magdalena", "Pueblo Libre", "Callao",
    "San Juan de Lurigancho",
]

TIPOS_SERVICIO = ["economico", "estandar", "confort", "xl"]
METODOS_PAGO   = ["efectivo", "tarjeta", "billetera"]
ESTADOS_VIAJE  = ["solicitado", "en_curso", "finalizado", "cancelado"]

TAGS_POSITIVOS = ["puntual", "auto_limpio", "conduccion_segura", "amable",
                  "musica_agradable", "ruta_eficiente"]
TAGS_NEGATIVOS = ["tarde", "brusco"]

# Rangos de identificadores acordados
N_USUARIOS    = 20_000
N_CONDUCTORES = 600
N_VEHICULOS   = 600
N_VIAJES      = 25_000
N_CALIFICACIONES = 22_000

# Ventana temporal del dataset
from datetime import datetime
FECHA_INICIO = datetime(2026, 3, 1)
MINUTOS_RANGO = 264_960   # ~184 dias, hasta el 31 de agosto

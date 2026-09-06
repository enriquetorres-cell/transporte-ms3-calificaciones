"""Comentarios en espanol real para el fake data de MS3.
Faker.sentence() devuelve lorem ipsum en latin: no sirve para la demo
ni para probar el indice de texto de MongoDB.
"""
import random

APERTURA_BUENA = [
    "Excelente servicio", "Muy buen viaje", "Todo perfecto", "Sin quejas",
    "Viaje muy comodo", "Buena experiencia", "Recomendado", "Muy conforme",
]
DETALLE_BUENO = [
    "el conductor llego puntual", "el auto estaba impecable",
    "el aire acondicionado funcionaba bien", "manejo con mucho cuidado",
    "tomo una ruta rapida y evito el trafico", "muy amable durante todo el trayecto",
    "la musica era agradable", "me ayudo con las maletas",
    "conversacion agradable sin ser invasivo", "llego antes de la hora acordada",
    "el auto olia a limpio", "conoce bien la zona",
]
APERTURA_REGULAR = [
    "Viaje normal", "Cumplio", "Nada que resaltar", "Aceptable", "Regular",
]
DETALLE_REGULAR = [
    "aunque demoro un poco en llegar", "pero habia mucho trafico",
    "el auto podria estar mas limpio", "la ruta no fue la mas corta",
    "sin aire acondicionado pero se aguanta", "no hubo conversacion",
]
APERTURA_MALA = [
    "Mala experiencia", "No lo recomiendo", "Muy decepcionado",
    "Pesimo servicio", "No volveria a viajar con el",
]
DETALLE_MALO = [
    "llego veinte minutos tarde", "manejo muy brusco en las curvas",
    "el auto estaba sucio y olia mal", "puso musica a todo volumen",
    "tomo una ruta larga sin avisar", "estuvo hablando por telefono todo el viaje",
    "el aire acondicionado no funcionaba", "me dejo a dos cuadras del destino",
    "fue cortante y de mal humor",
]
CIERRE = ["", "", "", " Gracias.", " Muy recomendable.", " Espero que mejore.",
          " Ojala lo tomen en cuenta.", " Repetiria."]

RESPUESTAS = [
    "Lamento lo ocurrido, tomare en cuenta su comentario.",
    "Gracias por la observacion, voy a mejorar ese punto.",
    "Le pido disculpas por la demora, hubo un problema en la ruta.",
    "Agradezco su comentario, espero atenderlo mejor la proxima vez.",
]

MOTIVO_DETALLE = "El comentario contiene lenguaje inapropiado o no corresponde al viaje."


def comentario_para(rating):
    if rating >= 4:
        base = f"{random.choice(APERTURA_BUENA)}, {random.choice(DETALLE_BUENO)}"
        if random.random() < 0.35:
            base += f" y {random.choice(DETALLE_BUENO)}"
    elif rating == 3:
        base = f"{random.choice(APERTURA_REGULAR)}, {random.choice(DETALLE_REGULAR)}"
    else:
        base = f"{random.choice(APERTURA_MALA)}: {random.choice(DETALLE_MALO)}"
        if random.random() < 0.4:
            base += f", ademas {random.choice(DETALLE_MALO)}"
    return (base + random.choice(CIERRE)).strip()[:500]

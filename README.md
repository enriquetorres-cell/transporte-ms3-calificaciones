# MS3 · Calificaciones y Comentarios

Microservicio NoSQL de la plataforma de transporte urbano.
**CS2032 Cloud Computing** — Proyecto Parcial, ciclo 2026-2 · Parte **P3**.

> **Despliegue completo del proyecto en AWS (paso a paso):** ver la
> [guía principal](https://github.com/Limepal/MS1-Usuarios-y-Conductores#readme).
> En producción este servicio lo construye y levanta `desplegar-prod.sh` en mv-prod-a y mv-prod-b.

| | |
|---|---|
| Lenguaje | Node.js 20 · Express 4 |
| Base de datos | MongoDB 7 |
| Puerto | `8003` |
| Prefijo | `/ms3` |
| Swagger UI | `/ms3/docs` (OpenAPI en `/ms3/openapi.json`, fuente `docs/openapi.yaml`) |
| Health check | `/ms3/health` |

## Levantar en local (un solo comando)

```bash
cp .env.example .env
docker compose up --build
```

Luego abre <http://localhost:8003/ms3/docs>.

El `docker-compose.yml` de este repo levanta **Mongo + MS3 juntos** para desarrollo.
En AWS, Mongo vive en la MV de bases de datos y este compose solo declara el servicio `ms3`.

## Sin Docker

```bash
npm install
export MONGO_URI="mongodb://localhost:27017/calificaciones_db"
npm run dev
```

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/ms3/health` | Health check del balanceador |
| GET | `/ms3/calificaciones` | Listar con filtros `viaje_id`, `conductor_id`, `pasajero_id`, `min_rating`, `tag`, `q` (texto), `page`, `limit` |
| GET | `/ms3/calificaciones/:id` | Detalle |
| POST | `/ms3/calificaciones` | Crear · 409 si el viaje ya fue calificado |
| PATCH | `/ms3/calificaciones/:id` | Editar comentario, rating, tags o responder como conductor |
| DELETE | `/ms3/calificaciones/:id` | Eliminar |
| GET | `/ms3/conductores/:id/resumen` | Promedio, distribución de estrellas y top de tags (agregación `$facet`). Lo consumen **MS1** (reglas) y **MS4** |
| GET | `/ms3/reportes` | Cola de moderación |
| POST | `/ms3/reportes` | Reportar una calificación |

### Prueba rápida

```bash
curl -X POST http://localhost:8003/ms3/calificaciones \
  -H 'content-type: application/json' \
  -d '{"viaje_id":18420,"pasajero_id":552,"conductor_id":81,"rating":4,
       "tags":["puntual","auto_limpio"],"comentario":"Llegó antes de la hora",
       "distrito_origen":"Miraflores","distrito_destino":"San Isidro"}'

curl "http://localhost:8003/ms3/calificaciones?conductor_id=81&min_rating=4"
curl "http://localhost:8003/ms3/calificaciones?q=hora"          # índice de texto
curl "http://localhost:8003/ms3/conductores/81/resumen"
```

## Estructura de datos

Las estructuras JSON de las dos colecciones, con tipos, ejemplos e índices, están en
[`docs/esquemas.json`](docs/esquemas.json). Es el equivalente al diagrama E/R que el
enunciado pide para las bases SQL.

## Fake data

Los scripts que siembran las **tres** bases del proyecto (≥20,000 registros en cada una)
están en [`seed/`](seed/) con su propio README. Orden: PostgreSQL → MySQL → MongoDB.

## Variables de entorno

| Variable | Ejemplo | Para qué |
|---|---|---|
| `PORT` | `8003` | Puerto de escucha |
| `PREFIX` | `/ms3` | Prefijo de todas las rutas |
| `MONGO_URI` | `mongodb://app_ms3:***@10.0.2.x:27017/calificaciones_db?authSource=calificaciones_db` | Conexión a la MV de bases (`app_ms3` se crea en `calificaciones_db`) |
| `MS2_URL` | `http://alb-interno/ms2` | Para validar el viaje contra MS2 |
| `VALIDAR_VIAJE` | `false` | Apaga la validación cruzada si MS2 no está arriba |

## Despliegue en AWS

1. En mv-prod-a y mv-prod-b, `desplegar-prod.sh` (repo de MS1) clona este repo, construye la imagen
   `transporte-ms3:1.2` y la levanta con `docker compose` en el puerto 8003.
2. El ALB interno enruta `/ms3/*` al target group `tg-ms3` (health check `GET /ms3/health`).
3. El API Gateway (HTTP API + VPC Link) lo expone en `https://<api-id>.execute-api.us-east-1.amazonaws.com/ms3/*`.

Pasos completos: [guía principal](https://github.com/Limepal/MS1-Usuarios-y-Conductores#readme).

## Notas de implementación

- **CORS no se configura aquí.** Va una sola vez en el API Gateway; dos capas se pelean.
- El índice `unique` sobre `viaje_id` implementa la regla "un viaje se califica una sola vez" y devuelve `409`.
- `VALIDAR_VIAJE=true` hace que `POST /calificaciones` consulte a MS2; si MS2 no responde en 5 s, no bloquea la creación.
- Todas las fechas se guardan y devuelven en UTC.

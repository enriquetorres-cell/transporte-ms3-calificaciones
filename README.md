# MS3 · Calificaciones y Comentarios

Microservicio NoSQL de la plataforma de transporte urbano.
**CS2032 Cloud Computing** — Proyecto Parcial, ciclo 2026-2 · Parte **P3**.

| | |
|---|---|
| Lenguaje | Node.js 20 · Express 4 |
| Base de datos | MongoDB 7 |
| Puerto | `8003` |
| Prefijo | `/ms3` |
| Swagger UI | `/ms3/docs` |
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
| GET | `/ms3/calificaciones` | Listar con filtros `conductor_id`, `pasajero_id`, `min_rating`, `tag`, `q`, `page`, `limit` |
| GET | `/ms3/calificaciones/:id` | Detalle |
| POST | `/ms3/calificaciones` | Crear · 409 si el viaje ya fue calificado |
| PATCH | `/ms3/calificaciones/:id` | Editar comentario, rating, tags o responder como conductor |
| DELETE | `/ms3/calificaciones/:id` | Eliminar |
| GET | `/ms3/conductores/:id/resumen` | Promedio, distribución de estrellas y top de tags (agregación) |
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
| `MONGO_URI` | `mongodb://app_ms3:***@10.0.2.50:27017/calificaciones_db?authSource=admin` | Conexión a la MV de bases |
| `MS2_URL` | `http://alb-interno/ms2` | Para validar el viaje contra MS2 |
| `VALIDAR_VIAJE` | `false` | Apaga la validación cruzada si MS2 no está arriba |

## Despliegue

1. `docker build -t <usuario>/transporte-ms3:1.0 . && docker push <usuario>/transporte-ms3:1.0`
2. En cada MV de producción, el compose del equipo hace `pull` de esa imagen.
3. El balanceador interno enruta `/ms3/*` al target group del puerto 8003.
4. AWS API Gateway (HTTP API + VPC Link) expone `https://…execute-api…/ms3/*`.

## Notas de implementación

- **CORS no se configura aquí.** Va una sola vez en el API Gateway; dos capas se pelean.
- El índice `unique` sobre `viaje_id` implementa la regla "un viaje se califica una sola vez" y devuelve `409`.
- `VALIDAR_VIAJE=true` hace que `POST /calificaciones` consulte a MS2; si MS2 no responde en 5 s, no bloquea la creación.
- Todas las fechas se guardan y devuelven en UTC.

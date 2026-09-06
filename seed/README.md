# Scripts de fake data

Cargan >=20,000 registros en una tabla de cada una de las tres bases del proyecto.

## Orden obligatorio

    python3 seed_postgres.py   # 1ro: usuarios, conductores, vehiculos (fuente de verdad de los IDs)
    python3 seed_mysql.py      # 2do: 25,000 viajes que referencian esos IDs
    python3 seed_mongo.py      # 3ro: 22,000 calificaciones, una por viaje finalizado

Los tres comparten `comun.py`: misma semilla (42), mismos distritos, mismos rangos de ID.
Cambiar cualquiera de esos valores en un solo script rompe la coherencia entre bases.

## Preparacion

    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt

## Variables de entorno

    export PG_DSN="host=10.0.2.X dbname=usuarios_db user=app_ms1 password=***"
    export MYSQL_HOST=10.0.2.X MYSQL_USER=app_ms2 MYSQL_PASS=*** MYSQL_DB=viajes_db
    export MONGO_URI="mongodb://app_ms3:***@10.0.2.X:27017/calificaciones_db?authSource=admin"

## Importante

Correr desde una MV de produccion, nunca desde una laptop: las bases son privadas
y no aceptan conexiones desde fuera de la VPC.

## Evidencia para el informe

    psql  -c "SELECT COUNT(*) FROM usuarios;"          -> 20000
    mysql -e "SELECT COUNT(*) FROM viajes;"            -> 25000
    mongosh --eval "db.calificaciones.countDocuments()" -> 22000

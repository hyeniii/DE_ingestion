Table of Contents:
1. [Running Postgres and PgAdmin through Docker](#Running-Postgres-and-PgAdmin-through-Docker)
2. [Ingesting Data](#Ingesting-Data)

# Running Postgres and PgAdmin through Docker

### 0. Environment Dependencies
python = 3.9.16
Packages:
- pgcli
- psycopg2-binary
- sqlalchemy

** installed postgresql through `brew install postgresql`

### 1. Postgres Docker

Download docker image using `docker pull postgres:13`
Run postgres through docker using following command

```bash
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:13
```
- open a new terminal and connect to postgres using pgcli
`pgcli -h localhost -p 5432 -u root -d ny_taxi`

### 2. PgAdmin Docker 

Download docker image using `docker pull dpage/pgadmin4`

```bash
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8080:80 \
  dpage/pgadmin4
```
**PROBLEM** 
Can't connect to postgres since pgadmin and postgres are in different containers
Connect two containers using network

### 3. Postgres and PgAdmin together

Create network using `docker network create pg-network`

Run Postgres
```bash
docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="ny_taxi" \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
  --network=pg-network \
  --name pg-database \
  -p 5432:5432 \
  postgres:13
```

Run PgAdmin
```bash
docker run -it \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  --network=pg-network \
  --name=pgadmin-2 \
  -p 8080:80 \
  dpage/pgadmin4
```
- create a server with database name `pg-database` to connect to postgres DB.

# Ingesting Data

```bash
URL="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"

python ingest_data.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --tb=yellow_taxi_data \
  --url=${URL}
```
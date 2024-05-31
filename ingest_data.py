import os, sys
import argparse

from time import time
import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import create_engine


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    tb = params.tb
    url = params.url

    # get filename from url
    file_name = url.rsplit('/', 1)[-1]
    print(f"Downloading {file_name}...")

    # Download data using curl
    os.system(f"curl -L {url.strip()} -o {file_name}")
    print('\n')

    # create SQL engine
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    # read file based on extension
    # df needed to create column schema
    try:
        if file_name.endswith(".parquet"):
            file = pq.ParquetFile(file_name)
            df = next(file.iter_batches(batch_size=2)).to_pandas()
            df_iter = file.iter_batches(batch_size=100000)

        elif file_name.endswith('.csv') or file_name.endswith('.csv.gz'):
            compression = 'gzip' if file_name.endswith('.csv.gz') else None
            df = pd.read_csv(file_name, nrows=10, compression=compression)
            df_iter = pd.read_csv(file_name, iterator=True, chunksize=100000, compression=compression)

        else:
            raise ValueError("Only .csv, .csv.gz, .parquet files allowed")
    except Exception as e:
        print(f"Error: {e} ")
        sys.exit(1)
    
    # Create DB in postgres
    df.head(0).to_sql(name=tb, con=engine, if_exists='replace')

    # Populate table
    t_start = time()
    count = 0
    for batch in df_iter:
        count += 1

        if '.parquet' in file_name:
            df = batch.to_pandas()
        else:
            df = batch
        print(f'inserting batch {count}...')

        b_start = time()
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.to_sql(name=tb, con=engine, if_exists='append')
        b_end = time()
        print(f'inserted! time taken {b_end-b_start:10.3f} seconds.\n')

    t_end = time()
    print(f'Completed! Total time taken was {t_end-t_start:10.3f} seconds for {count} batches.') 

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Ingest CSV data to postgres")
    # user, password, host, port, database name, table name, url of csv
    parser.add_argument('--user', help='username for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='database name for postgres')
    parser.add_argument('--tb', help='name of table to ingest data to')
    parser.add_argument('--url', help='url of the csv data')

    args = parser.parse_args()
    main(args)
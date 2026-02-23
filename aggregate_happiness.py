
import boto3

import pandas as pd

from io import BytesIO

  

# --- Konfigurasi ---

S3_ENDPOINT = 'http://minio:9000'

S3_ACCESS_KEY = 'admin'

S3_SECRET_KEY = 'admin123'

SILVER_BUCKET = 'silver'

GOLD_BUCKET = 'gold'

INPUT_FILE_KEY = 'happiness_clean.parquet'

OUTPUT_FILE_KEY = 'happiness_summary_by_country.parquet'

  

# --- Koneksi ke MinIO ---

s3 = boto3.client(

's3',

endpoint_url=S3_ENDPOINT,

aws_access_key_id=S3_ACCESS_KEY,

aws_secret_access_key=S3_SECRET_KEY

)

  

def main():

"""Fungsi utama untuk agregasi data dari Silver ke Gold."""

print(f"Membaca file '{INPUT_FILE_KEY}' dari bucket '{SILVER_BUCKET}'...")

# 1. Membaca data dari Silver

response = s3.get_object(Bucket=SILVER_BUCKET, Key=INPUT_FILE_KEY)

df = pd.read_parquet(BytesIO(response['Body'].read()))

print("Data bersih berhasil dibaca. Melakukan agregasi...")

# 2. Agregasi Data

df_gold = (

df.groupby('entity')

.agg(

avg_happiness_score=('self-reported_life_satisfaction', 'mean'),

total_records=('year', 'count')

)

.reset_index()

.sort_values(by='avg_happiness_score', ascending=False)

)

df_gold['generated_at'] = pd.Timestamp.now()

print("Agregasi selesai. Data agregat:")

print(df_gold.head())

# 3. Simpan data agregat ke Gold

output_buffer = BytesIO()

df_gold.to_parquet(output_buffer, index=False)

s3.put_object(

Bucket=GOLD_BUCKET,

Key=OUTPUT_FILE_KEY,

Body=output_buffer.getvalue()

)

print(f"\nBerhasil! File '{OUTPUT_FILE_KEY}' telah disimpan di bucket '{GOLD_BUCKET}'.")

  

if __name__ == "__main__":

main()

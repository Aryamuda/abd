import boto3
import pandas as pd
from io import BytesIO

# --- Konfigurasi ---
S3_ENDPOINT = 'http://minio:9000'
S3_ACCESS_KEY = 'admin'
S3_SECRET_KEY = 'admin123'
BRONZE_BUCKET = 'bronze'
SILVER_BUCKET = 'silver'
INPUT_FILE_KEY = 'happiness-cantril-ladder.csv'
OUTPUT_FILE_KEY = 'happiness_clean.parquet'

# --- Koneksi ke MinIO ---
s3 = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY
)

def main():
    """Fungsi utama untuk transformasi data dari Bronze ke Silver."""
    print(f"Membaca file '{INPUT_FILE_KEY}' dari bucket '{BRONZE_BUCKET}'...")
    
    # 1. Membaca data dari Bronze
    response = s3.get_object(Bucket=BRONZE_BUCKET, Key=INPUT_FILE_KEY)
    df = pd.read_csv(BytesIO(response['Body'].read()))
    
    print("Data mentah berhasil dibaca. Melakukan transformasi...")
    
    # 2. Transformasi Data
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
    df_clean = df.dropna()
    df_clean['processed_at'] = pd.Timestamp.now()
    
    print("Transformasi selesai. Data bersih:")
    print(df_clean.head())
    
    # 3. Simpan data bersih ke Silver dalam format Parquet
    output_buffer = BytesIO()
    df_clean.to_parquet(output_buffer, index=False)
    
    s3.put_object(
        Bucket=SILVER_BUCKET,
        Key=OUTPUT_FILE_KEY,
        Body=output_buffer.getvalue()
    )
    
    print(f"\nBerhasil! File '{OUTPUT_FILE_KEY}' telah disimpan di bucket '{SILVER_BUCKET}'.")

if __name__ == "__main__":
    main()

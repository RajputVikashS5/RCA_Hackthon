# Cloudflare R2 Dataset Storage

## Architecture

The local Jira archive is uploaded with a multipart-capable boto3 transfer to Cloudflare R2. The ingestion pipeline downloads only the selected R2 object to a temporary seekable file, streams BSON batches through the existing Jira reader and transformer, generates the existing 384-dimensional SentenceTransformer embeddings, and writes processed incidents to PostgreSQL + pgvector.

R2 is the raw dataset. PostgreSQL is the processed incident and embedding store.

## R2 setup

1. Create an R2 bucket.
2. Create a restricted S3 API token for that bucket.
3. Add the endpoint, access key, secret, bucket, and region to `backend/.env`.
4. Never commit credentials or expose them to the frontend.

## Environment variables

`R2_ENDPOINT_URL`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_REGION`, `R2_OBJECT_KEY`, and `R2_MANIFEST_KEY` are supported. Uploads use 64 MiB multipart thresholds/chunks by default.

## Upload and checksum verification

Use a small file first:

```powershell
python ingestion/upload_dataset.py --file test-r2.txt --key test/test-r2.txt
```

Then upload the archive:

```powershell
python ingestion/upload_dataset.py --file "E:\path\to\jira-dataset.zip" --key raw/jira-dataset.zip
```

The CLI hashes in 8 MiB chunks, uploads a manifest, verifies object existence, and prints the object key, size, and checksum. `ingestion/dataset_manifest.py` also provides `calculate_sha256(path)` and manifest validation.

## Dataset structure

Use `raw/jira-dataset.zip` or the exact BSON object key supplied by `R2_OBJECT_KEY`. The Jira reader selects only explicit Jira issue archives; unrelated model ZIPs are not selected.

## Ingestion

```powershell
python ingestion/pipeline.py --source r2 --max-records 1000
```

After validating the sample and PostgreSQL counts:

```powershell
$env:INGEST_MAX_RECORDS = "0"
python ingestion/pipeline.py --source r2
```

`0` means unlimited, but processing remains batch-based. Temporary R2 downloads are removed even when ingestion fails.

## Status and troubleshooting

`GET /api/dataset/status` performs metadata/head checks only. `GET /api/dataset` reads the optional manifest and lists metadata; neither endpoint downloads the raw archive. Missing credentials, inaccessible buckets, missing objects, invalid BSON, and upload failures are reported without returning secrets.

## Security notes

Keep R2 credentials in the backend environment only. Do not create a browser upload endpoint for the multi-gigabyte archive. Do not store the raw archive or embeddings in PostgreSQL, and do not store embeddings in R2.

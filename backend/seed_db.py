import os
from app.services.incident_ingestion import IncidentIngestionService
from app.models.schemas import IncidentRecord
import json
import tempfile
from pathlib import Path

incidents = [
    {
        "incident_id": "INC-001",
        "title": "Database Connection Pool Exhaustion",
        "description": "The production user-service is throwing 500 Internal Server errors. Monitoring shows that the PostgreSQL database connection pool is completely exhausted, and all new incoming API requests are timing out while waiting for a connection.",
        "component": "Database",
        "severity": "High",
        "environment": "Production",
        "incident_type": "Outage",
        "root_cause": "A recent deployment introduced a slow query in the user-authentication path, causing database connections to remain open for 30+ seconds instead of releasing immediately. This cascaded into pool exhaustion.",
        "resolution": "Rolled back the deployment to the previous stable version. Added an index to the authentication table to prevent the slow query from occurring again in the future.",
        "status": "Resolved"
    },
    {
        "incident_id": "INC-002",
        "title": "Memory Leak / OOMKilled in Payment Service",
        "description": "Alerts fired for the payment-processing pod constantly crashing and restarting in Kubernetes. Checking the pod events shows OOMKilled (Out of Memory) errors. The memory usage spikes drastically whenever the nightly batch job is submitted.",
        "component": "Payment Service",
        "severity": "Critical",
        "environment": "Production",
        "incident_type": "Performance Degradation",
        "root_cause": "The batch processing job was reading the entire payments table into memory at once instead of streaming the rows. This caused the container to exceed its 2GB memory limit.",
        "resolution": "Modified the batch job to use a paginated/streaming database cursor and increased the pod memory limit temporarily to 4GB.",
        "status": "Resolved"
    },
    {
        "incident_id": "INC-003",
        "title": "Redis Cache Timeout",
        "description": "Global API response times have degraded by 300% over the last hour. Application logs indicate frequent network read timeouts when the backend attempts to fetch user session data from the Redis cache cluster.",
        "component": "Cache Layer",
        "severity": "Medium",
        "environment": "Staging",
        "incident_type": "Performance Degradation",
        "root_cause": "A noisy neighbor process on the same VM was consuming excessive network bandwidth and CPU, starving the Redis process and causing networking latency spikes.",
        "resolution": "Migrated the Redis cluster to dedicated infrastructure and enabled network bandwidth throttling on background workers.",
        "status": "Resolved"
    }
]

def seed():
    print("Seeding local vector database with sample incidents...")
    service = IncidentIngestionService()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "sample_incidents.json"
        with open(file_path, "w") as f:
            json.dump(incidents, f)
            
        print(f"Created temporary dataset at {file_path}")
        try:
            records, stats = service.load_file(file_path)
            
            # Actually embed and insert the records
            from app.database.repository import IncidentRepository
            from app.services.embedding import SentenceTransformerEmbeddingService
            from app.database.connection import initialize_database
            
            print("Initializing database...")
            initialize_database()
            
            print("Generating embeddings...")
            embedder = SentenceTransformerEmbeddingService()
            embedder._ensure_model()
            
            embedded_records = []
            for record in records:
                record_dict = record.model_dump()
                text_to_embed = service.build_search_text(record_dict)
                embedding = embedder.model.encode(text_to_embed)
                record_dict["embedding"] = embedding.tolist()
                embedded_records.append(record_dict)
                
            print("Inserting into database...")
            repository = IncidentRepository()
            repository.upsert_batch(embedded_records)
            
            print(f"Successfully ingested {len(embedded_records)} records into vector store.")
        except Exception as e:
            print(f"Error during ingestion: {e}")

if __name__ == "__main__":
    seed()

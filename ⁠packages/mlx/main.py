import os
import asyncio
import asyncpg
from llmx.event_bus import SwarmEventBus
from detector import AnomalyScorer

class MLXPipeline:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.db_pool = None
        self.scorer = AnomalyScorer()

    async def connect_db(self):
        self.db_pool = await asyncpg.create_pool(self.db_url)
        print("[ML-x] Connected to PostgreSQL state database.")

    async def process_recon_event(self, event_data: dict):
        """Callback triggered when Scout finds a new target."""
        payload = event_data.get("data", {})
        target_url = payload.get("url")
        headers = payload.get("headers")

        if not target_url or not headers:
            return

        # 1. Execute ML scoring
        anomaly_score = self.scorer.calculate_score(headers)
        print(f"[ML-x] Scored {target_url} -> Anomaly Risk: {anomaly_score:.2f}")

        # 2. Persist to PostgreSQL if the score indicates it's worth reviewing
        if anomaly_score > 0.3:
            await self._persist_finding(target_url, anomaly_score, headers)

    async def _persist_finding(self, url: str, score: float, headers: dict):
        """Upsert the anomaly score into the database for the Next.js dashboard."""
        query = """
            INSERT INTO target_findings (id, url, anomaly_score, status, headers)
            VALUES (gen_random_uuid(), $1, $2, 'investigating', $3)
            ON CONFLICT (url) DO UPDATE 
            SET anomaly_score = EXCLUDED.anomaly_score,
                updated_at = NOW();
        """
        # Simplistic header stringification for DB storage
        headers_str = str(headers)[:500] 
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(query, url, score, headers_str)

async def main():
    # Environment variables injected via docker-compose.yml
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    db_url = os.environ.get("DB_URL", "postgresql://xterminator:dev_password@localhost:5432/bounty_state")

    pipeline = MLXPipeline(db_url)
    await pipeline.connect_db()

    bus = SwarmEventBus(redis_url=redis_url)
    await bus.connect()

    print("[*] ML-x Anomaly Scoring Pipeline online. Listening to bus...")
    
    # Subscribe to the same channel the Gemini agent listens to
    await bus.subscribe("recon_events", pipeline.process_recon_event)

if __name__ == "__main__":
    asyncio.run(main())

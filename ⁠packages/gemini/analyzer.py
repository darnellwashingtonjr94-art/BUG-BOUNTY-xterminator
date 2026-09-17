import os
import asyncio
import asyncpg
from google import genai
from llmx.event_bus import SwarmEventBus

class TargetAnalyzerAgent:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.db_pool = None
        self.client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        
        # System instruction focused on infrastructure and security analysis
        self.system_instruction = (
            "You are an infrastructure security analyst. Review the provided HTTP headers "
            "and architecture metadata. Identify the likely proxy, WAF, or CDN in use, "
            "and note any missing security headers or architectural anomalies concisely."
        )

    async def connect_db(self):
        """Initializes the PostgreSQL connection pool."""
        self.db_pool = await asyncpg.create_pool(self.db_url)
        print("[Gemini Agent] Connected to PostgreSQL state database.")

    async def analyze_and_persist(self, event_data: dict):
        """Callback triggered by the scout engine via Redis; analyzes headers and saves to DB."""
        payload = event_data.get("data", {})
        target = payload.get("url")
        headers = payload.get("headers")

        if not target or not headers:
            return

        print(f"[Gemini Agent] Analyzing target structure for: {target}")
        prompt = f"Analyze these headers for {target}:\n{headers}"

        try:
            # Asynchronous execution using the google-genai SDK
            response = await self.client.aio.models.generate_content(
                model='gemini-2.5-pro',
                contents=prompt,
                config=types_config = genai.types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.2
                )
            )
            
            insight_text = response.text.strip()
            print(f"[+] [Gemini Agent] Analysis complete for {target}")

            # Persist the AI insight directly to PostgreSQL
            await self._persist_insight(target, insight_text)

        except Exception as e:
            print(f"[-] [Gemini Agent] Error during analysis for {target}: {e}")

    async def _persist_insight(self, url: str, insight: str):
        """Updates the target record with the Gemini architectural insight."""
        query = """
            UPDATE target_findings
            SET ai_insight = $1,
                updated_at = NOW()
            WHERE url = $2;
        """
        async with self.db_pool.acquire() as conn:
            await conn.execute(query, insight, url)
        print(f"[DB] Persisted AI insight for {url}")


async def main():
    # Environment variables injected via docker-compose.yml
    redis_url = os.environ.get("REDIS_URL", "redis://redis-event-bus:6379")
    db_url = os.environ.get("DB_URL", "postgresql://xterminator:dev_password@localhost:5432/bounty_state")

    agent = TargetAnalyzerAgent(db_url)
    await agent.connect_db()

    bus = SwarmEventBus(redis_url=redis_url)
    await bus.connect()

    print("[*] Gemini Analyzer Agent online. Listening to 'recon_events'...")
    
    # Subscribe to the event bus channel
    await bus.subscribe("recon_events", agent.analyze_and_persist)

if __name__ == "__main__":
    asyncio.run(main())

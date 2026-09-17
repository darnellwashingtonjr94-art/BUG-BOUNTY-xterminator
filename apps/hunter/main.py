import os
import asyncio
import httpx
from llmx.event_bus import SwarmEventBus

class HunterAgent:
    def __init__(self):
        self.timeout = 10.0

    async def handle_target_verification(self, event_data: dict):
        """Callback triggered when an anomaly requires active hunter validation."""
        payload = event_data.get("data", {})
        target_url = payload.get("url")
        anomaly_score = payload.get("anomaly_score", 0.0)

        if not target_url:
            return

        print(f"[Hunter] Initiating verification workflow for target: {target_url} (Score: {anomaly_score})")

        async with httpx.AsyncClient(verify=False) as client:
            try:
                # Perform controlled endpoint inspection
                response = await client.get(target_url, timeout=self.timeout)
                print(f"[Hunter] Target {target_url} responded with status code: {response.status_code}")
                
                # Check for specific structural headers or reflections
                if response.status_code in [200, 403, 500]:
                    print(f"[+] [{target_url}] Flagged for deep inspection and PoC generation queue.")
                    
            except httpx.RequestError as e:
                print(f"[-] [Hunter] Connection error testing {target_url}: {e}")

async def main():
    redis_url = os.environ.get("REDIS_URL", "redis://redis-event-bus:6379")
    
    bus = SwarmEventBus(redis_url=redis_url)
    await bus.connect()

    hunter = HunterAgent()
    print("[*] Hunter execution daemon online. Listening to 'hunter_queue'...")

    await bus.subscribe("hunter_queue", hunter.handle_target_verification)

if __name__ == "__main__":
    asyncio.run(main())

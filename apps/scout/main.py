import asyncio
import httpx
from llmx.event_bus import SwarmEventBus

async def fetch_headers(target: str, client: httpx.AsyncClient) -> dict:
    """Passive recon task for surface-level fingerprinting."""
    try:
        response = await client.head(target, timeout=5.0)
        return dict(response.headers)
    except httpx.RequestError:
        return {"error": "unreachable"}

async def run_scout_campaign(targets: list[str], bus: SwarmEventBus):
    """Executes async recon and broadcasts results to the swarm."""
    async with httpx.AsyncClient() as client:
        tasks = [fetch_headers(t, client) for t in targets]
        results = await asyncio.gather(*tasks)

        for target, headers in zip(targets, results):
            if "error" not in headers:
                print(f"[Scout] Discovered live surface: {target}")
                
                # Push discovery to the swarm for ML/LLM analysis
                await bus.publish(
                    channel="recon_events",
                    event_type="NEW_TARGET_SURFACE",
                    payload={"url": target, "headers": headers}
                )

async def main():
    bus = SwarmEventBus(redis_url="redis://redis-event-bus:6379")
    await bus.connect()
    
    # In production, this loads from configs/target_scopes.json
    scope = ["https://example.com", "https://api.example.com"]
    await run_scout_campaign(scope, bus)

if __name__ == "__main__":
    asyncio.run(main())

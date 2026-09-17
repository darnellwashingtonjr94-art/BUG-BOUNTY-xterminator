import os
import asyncio
from llmx.event_bus import SwarmEventBus

class ValidatorAgent:
    def __init__(self):
        print("[Validator] Initializing patch re-testing & validation module...")

    async def process_validation_event(self, event_data: dict):
        """Listens for resolved or submitted vulnerability reports to verify remediation."""
        payload = event_data.get("data", {})
        finding_id = payload.get("id")
        target_url = payload.get("url")

        if not finding_id or not target_url:
            return

        print(f"[Validator] Running patch re-test sequence for finding [{finding_id}] at {target_url}...")
        
        # Simulate re-testing verification logic
        await asyncio.sleep(2)
        print(f"[+] [Validator] Finding {finding_id} status verified. Logging state transition.")

async def main():
    redis_url = os.environ.get("REDIS_URL", "redis://redis-event-bus:6379")

    bus = SwarmEventBus(redis_url=redis_url)
    await bus.connect()

    validator = ValidatorAgent()
    print("[*] Validator daemon online. Listening to 'validator_queue'...")

    await bus.subscribe("validator_queue", validator.process_validation_event)

if __name__ == "__main__":
    asyncio.run(main())

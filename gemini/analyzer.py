import os
import asyncio
from google import genai
from llmx.event_bus import SwarmEventBus

class TargetAnalyzerAgent:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        # Focus the model on infrastructure analysis, not exploitation
        self.system_instruction = (
            "You are an infrastructure analyst. Review the provided HTTP headers "
            "and architecture metadata. Identify the likely proxy, WAF, or CDN in use, "
            "and note any missing security headers or architectural anomalies."
        )

    async def analyze_headers(self, event_data: dict):
        """Callback triggered by the scout engine via Redis."""
        payload = event_data.get("data", {})
        target = payload.get("url")
        headers = payload.get("headers")

        if not target or not headers:
            return

        prompt = f"Analyze these headers for {target}:\n{headers}"
        
        # Async execution using google-genai SDK
        response = await self.client.aio.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.2
            )
        )
        
        print(f"[Gemini Agent] Analysis for {target}:\n{response.text}\n")
        # Next step: Publish findings back to bus for the 'reporter' app

async def main():
    bus = SwarmEventBus(redis_url="redis://redis-event-bus:6379")
    await bus.connect()
    
    agent = TargetAnalyzerAgent()
    print("[*] Gemini Analyzer Agent listening for recon_events...")
    
    # Keep service alive listening to the bus
    await bus.subscribe("recon_events", agent.analyze_headers)

if __name__ == "__main__":
    asyncio.run(main())

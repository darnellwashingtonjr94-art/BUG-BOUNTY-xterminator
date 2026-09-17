#!/usr/bin/env python3
"""
Veo 3 Operation Poller & Downloader
Polls Google GenAI long-running operations from batch generation and downloads completed MP4s.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from google import genai
from google.genai.errors import APIError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("veo-poller")


class VeoBatchPoller:
    def __init__(
        self,
        input_file: Path,
        output_dir: Path,
        poll_interval: int = 15,
        max_attempts: int = 120,
    ):
        self.input_file = input_file
        self.output_dir = output_dir
        self.poll_interval = poll_interval
        self.max_attempts = max_attempts

        # Initialize Google GenAI Async Client
        self.client = genai.Client()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_jobs(self) -> List[Dict[str, Any]]:
        """Loads job operations state from JSON file."""
        if not self.input_file.exists():
            logger.error(f"Input file not found: {self.input_file}")
            sys.exit(1)

        with open(self.input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("jobs", data if isinstance(data, list) else [])

    def save_jobs(self, jobs: List[Dict[str, Any]]) -> None:
        """Saves updated state back to disk."""
        with open(self.input_file, "w", encoding="utf-8") as f:
            json.dump({"jobs": jobs}, f, indent=2)

    async def poll_operation(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Polls a single long-running video generation operation."""
        op_name = job["operation_name"]
        job_id = job.get("job_id", op_name)

        if job.get("status") == "COMPLETED":
            logger.info(f"[{job_id}] Already downloaded previously.")
            return job

        logger.info(f"[{job_id}] Polling operation: {op_name}")
        attempts = 0

        while attempts < self.max_attempts:
            try:
                # Retrieve current operation state using async client
                operation = await self.client.aio.operations.get(name=op_name)

                if operation.done:
                    if getattr(operation, "error", None):
                        err_msg = str(operation.error)
                        logger.error(f"[{job_id}] Generation failed: {err_msg}")
                        job["status"] = "FAILED"
                        job["error"] = err_msg
                        return job

                    # Successfully completed - download MP4 files
                    logger.info(f"[{job_id}] Operation completed! Downloading video...")
                    job["status"] = "SUCCEEDED"
                    downloaded_files = await self._download_videos(job_id, operation)
                    job["downloaded_files"] = downloaded_files
                    job["status"] = "COMPLETED"
                    return job

                attempts += 1
                logger.info(
                    f"[{job_id}] In progress... (Attempt {attempts}/{self.max_attempts})"
                )

            except APIError as e:
                logger.warning(f"[{job_id}] API Error encountered: {e}. Retrying...")
            except Exception as e:
                logger.error(f"[{job_id}] Unexpected error: {e}")

            await asyncio.sleep(self.poll_interval)

        job["status"] = "TIMED_OUT"
        logger.error(f"[{job_id}] Polling timed out after {self.max_attempts} attempts.")
        return job

    async def _download_videos(
        self, job_id: str, operation: Any
    ) -> List[str]:
        """Extracts generated video file objects and writes MP4s to output directory."""
        downloaded_paths = []
        response = getattr(operation, "response", None)

        if not response or not hasattr(response, "generated_videos"):
            logger.error(f"[{job_id}] No generated_videos found in operation response.")
            return downloaded_paths

        for idx, gen_vid in enumerate(response.generated_videos):
            filename = f"{job_id}_v{idx + 1}.mp4"
            dest_path = self.output_dir / filename

            try:
                # Stream file bytes or download using standard Client files API
                if hasattr(self.client.aio.files, "download"):
                    await self.client.aio.files.download(
                        file=gen_vid.video,
                        destination=str(dest_path)
                    )
                else:
                    # Fallback to direct bytes payload
                    video_bytes = getattr(gen_vid.video, "video_bytes", None)
                    if video_bytes:
                        dest_path.write_bytes(video_bytes)

                logger.info(f"[{job_id}] Successfully saved MP4 -> {dest_path}")
                downloaded_paths.append(str(dest_path))

            except Exception as e:
                logger.error(f"[{job_id}] Failed downloading video #{idx + 1}: {e}")

        return downloaded_paths

    async def run((self) -> None:
        """Executes concurrent polling for all pending batch operations."""
        jobs = self.load_jobs()
        pending_jobs = [j for j in jobs if j.get("status") not in ("COMPLETED", "FAILED")]

        if not pending_jobs:
            logger.info("No pending jobs to poll.")
            return

        logger.info(f"Starting async polling for {len(pending_jobs)} operations...")
        
        # Run worker tasks concurrently across pending jobs
        tasks = [self.poll_operation(job) for job in pending_jobs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Update and persist batch state
        self.save_jobs(jobs)
        logger.info("Polling batch completed. State persisted to disk.")


def main():
    parser = argparse.ArgumentParser(description="Poll and Download Veo 3 Video Operations")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("batch_jobs.json"),
        help="Path to JSON file generated by run_batch.py containing operation handles",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("downloads"),
        help="Directory where downloaded MP4s will be saved",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=15,
        help="Polling interval in seconds (default: 15)",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=120,
        help="Maximum polling attempts per job before timeout (default: 120)",
    )

    args = parser.parse_args()

    if not os.getenv("GOOGLE_API_KEY"):
        logger.warning("GOOGLE_API_KEY env var not set. Ensure credentials are set.")

    poller = VeoBatchPoller(
        input_file=args.input,
        output_dir=args.output_dir,
        poll_interval=args.interval,
        max_attempts=args.max_attempts,
    )

    asyncio.run(poller.run())


if __name__ == "__main__":
    main()

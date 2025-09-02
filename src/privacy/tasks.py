import asyncio
from datetime import datetime
import json
import logging
from pathlib import Path
from uuid import UUID

from src.core.celery_app import celery_app
from src.core.database import AsyncSessionLocal
from src.privacy.services import GDPRService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def generate_user_data_export(self, user_id: UUID, export_id: str | None = None) -> str:
    """
    Generate GDPR data export for a user in the background.
    Saves the export to a JSON file for later retrieval.
    Idempotent by checking if export already exists.
    """
    try:
        if not export_id:
            export_id = f"{user_id}_{datetime.utcnow().isoformat()}"
    
        try:
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(_generate_export_async(user_id, export_id))
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            return asyncio.run(_generate_export_async(user_id, export_id))
    except Exception as exc:
        logger.error(f"Error generating export for user {user_id}: {exc}")
        # Retry with exponential backoff
        raise self.retry(countdown=60 * (2**self.request.retries), exc=exc) from exc


async def _generate_export_async(user_id: UUID, export_id: str) -> str:
    logger.info(f"Generating data export for user {user_id}, export_id: {export_id}")

    # Create exports directory if it doesn't exist
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)

    export_file = export_dir / f"{export_id}.json"

    # Idempotency check: Skip if export already exists
    if export_file.exists():
        logger.info(f"Export {export_id} already exists, skipping")
        return f"Export already exists: {export_id}"

    async with AsyncSessionLocal() as session:
        gdpr_service = GDPRService(session)
        data = await gdpr_service.export_user_data(user_id)

    # Add metadata to the export
    export_data = {
        "metadata": {
            "user_id": user_id,
            "export_id": export_id,
            "generated_at": datetime.utcnow().isoformat(),
            "version": "1.0",
        },
        "data": data,
    }

    # Save to file
    with open(export_file, "w") as f:
        json.dump(export_data, f, indent=2)

    logger.info(f"Successfully generated export for user {user_id} at {export_file}")
    return f"Export generated: {export_id}"

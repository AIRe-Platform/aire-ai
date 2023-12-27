from fastapi import UploadFile
from pathlib import Path
from tempfile import NamedTemporaryFile
import shutil

async def create_temporary_file(file: UploadFile) -> Path | None:
    """Saves uploaded file on disk. Returns file path."""
    path = None
    try:
        suffix = Path(file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            path = Path(tmp.name)
    finally:
        await file.close()
    return path

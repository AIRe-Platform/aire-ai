# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


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

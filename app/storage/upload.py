from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status


BASE_UPLOAD_DIR = Path("uploads")

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def save_file(
    file: UploadFile,
    folder: str,
) -> str:
    """
    Save uploaded file and return relative path.
    Example:
        profile_photos/abc123.jpg
    """

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type.",
        )

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10 MB.",
        )

    upload_dir = BASE_UPLOAD_DIR / folder

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = f"{uuid4().hex}{extension}"

    file_path = upload_dir / filename

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    return f"{folder}/{filename}"
import os
import uuid


def generate_uuid_filename(path: str, extension: str) -> str:
    file_name = f"{uuid.uuid4()}.{extension.lstrip('.')}"
    return os.path.join(path, file_name)

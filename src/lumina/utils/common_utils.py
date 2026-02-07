import os
import uuid


def create_folder_if_not_exists(folder_path: str):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def generate_uuid_filename(path: str, extension: str) -> str:
    file_name = f"{uuid.uuid4()}.{extension.lstrip('.')}"
    return os.path.join(path, file_name)


def remove_extension(file_name: str) -> str:
    return os.path.splitext(file_name)[0]

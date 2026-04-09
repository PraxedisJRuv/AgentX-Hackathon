from sqlmodel import Session, SQLModel, create_engine
import base64
import os

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def save_image(image_base64: str, report_id: str) -> str:
    image_data = base64.b64decode(image_base64)
    images_dir = "images"
    os.makedirs(images_dir, exist_ok=True)
    image_path = os.path.join(images_dir, f"{report_id}.jpg")
    with open(image_path, "wb") as f:
        f.write(image_data)
    return image_path


def parse_images_to_b64(images_path: str) -> str:
    if not images_path:
        return None
    image_paths = images_path.split("!")
    b64_images = []
    for path in image_paths:
        with open(path, "rb") as f:
            b64_images.append(base64.b64encode(f.read()).decode("utf-8"))
    return b64_images


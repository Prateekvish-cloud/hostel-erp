from typing import Dict

from app.core.security import get_password_hash

# fake user store just for starting; later connect to PostgreSQL
fake_users_db: Dict[str, dict] = {
    "admin": {
        "username": "admin",
        "full_name": "Hostel Admin",
        "role": "admin",
        "hashed_password": get_password_hash("admin123"),
        "disabled": False,
    },
    "student1": {
        "username": "student1",
        "full_name": "Student One",
        "role": "student",
        "hashed_password": get_password_hash("stud123"),
        "disabled": False,
    },
}

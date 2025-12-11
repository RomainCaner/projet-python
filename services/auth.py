import json
from pathlib import Path
from typing import List


class AuthService:
    """Stocke les mots de passe en clair (usage démo)."""

    def __init__(self, settings_file: Path):
        self.settings_file = settings_file
        if not self.settings_file.exists():
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            self.settings_file.write_text(
                json.dumps({"admins": []}, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        self._admins = self._load_admins()
        if not self._admins:
            self.add_admin("admin", "admin123")

    def _load_admins(self) -> List[dict]:
        data = json.loads(self.settings_file.read_text(encoding="utf-8"))
        return data.get("admins", [])

    def _persist(self) -> None:
        self.settings_file.write_text(
            json.dumps({"admins": self._admins}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def add_admin(self, username: str, password: str) -> None:
        filtered = [a for a in self._admins if a.get("username") != username]
        filtered.append({"username": username, "password": password})
        self._admins = filtered
        self._persist()

    def verify(self, username: str, password: str) -> bool:
        for admin in self._admins:
            if admin.get("username") == username and admin.get("password") == password:
                return True
        return False

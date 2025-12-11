from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from models.student import Student
from services.storage import StorageService
from services.face_store import FaceStore


class StudentService:
    """Service de gestion des étudiants (enregistrement, reconnaissance)"""

    def __init__(self, storage: StorageService, face_store: FaceStore):
        self.storage = storage
        self.face_store = face_store

    def register_student(
        self,
        student_id: str,
        first_name: str,
        last_name: str,
        balance: float,
        image_path: Path,
    ) -> Student:
        """Enregistre un nouvel étudiant avec son encoding facial"""
        encoding = self.face_store.encode_image(image_path)
        student = Student(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            balance=balance,
            image_path=str(image_path),
            face_encoding=encoding,
        )
        self.storage.upsert_student(student)
        return student

    def match_encoding(self, encoding: List[float], tolerance: float = 0.6) -> Optional[Student]:
        """Compare un encoding facial à la base d'étudiants"""
        students = self.storage.load_students()
        for student in students:
            if not student.face_encoding:
                continue
            distance = self.face_store.compute_distance(encoding, student.face_encoding)
            if distance < tolerance:
                return student
        return None

    def decrement_balance(self, student_id: str, amount: float) -> Optional[Student]:
        """Décrémente le solde d'un étudiant"""
        return self.storage.decrement_balance(student_id, amount)

    def get_all_students(self) -> List[Student]:
        """Retourne la liste de tous les étudiants"""
        return self.storage.load_students()



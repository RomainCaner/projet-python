from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from models.student import Student


class StorageService:
    def __init__(self, students_file: Path):
        self.students_file = students_file
        self.students_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.students_file.exists():
            self.students_file.write_text("[]", encoding="utf-8")

    def load_students(self) -> List[Student]:
        raw = json.loads(self.students_file.read_text(encoding="utf-8"))
        return [Student(**student) for student in raw]

    def save_students(self, students: List[Student]) -> None:
        payload = [student.__dict__ for student in students]
        self.students_file.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def upsert_student(self, student: Student) -> None:
        students = self.load_students()
        filtered = [s for s in students if s.student_id != student.student_id]
        filtered.append(student)
        self.save_students(filtered)

    def decrement_balance(self, student_id: str, amount: float) -> Optional[Student]:
        students = self.load_students()
        updated = None
        for idx, student in enumerate(students):
            if student.student_id == student_id:
                student.balance = max(0.0, student.balance - amount)
                students[idx] = student
                updated = student
                break
        if updated:
            self.save_students(students)
        return updated



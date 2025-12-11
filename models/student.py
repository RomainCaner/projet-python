from dataclasses import dataclass, field
from typing import List


@dataclass
class Student:
    student_id: str
    first_name: str
    last_name: str
    balance: float
    image_path: str
    face_encoding: List[float] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

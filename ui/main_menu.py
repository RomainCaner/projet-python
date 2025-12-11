from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable


class MainMenu(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_add_student: Callable[[], None],
        on_access_control: Callable[[], None],
        on_logout: Callable[[], None],
    ):
        super().__init__(master, padding=32)
        self.on_add_student = on_add_student
        self.on_access_control = on_access_control
        self.on_logout = on_logout

        ttk.Label(self, text="Contrôle d'accès - Tableau de bord", font=("Segoe UI", 18)).pack(
            pady=(0, 32)
        )

        ttk.Button(
            self, text="Ajouter un nouvel étudiant", command=self.on_add_student, width=40
        ).pack(pady=8)

        ttk.Button(
            self, text="Contrôle d'accès", command=self.on_access_control, width=40
        ).pack(pady=8)

        ttk.Button(self, text="Se déconnecter", command=self.on_logout, width=40).pack(
            pady=(32, 0)
        )


from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from services.auth import AuthService


class LoginView(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        auth_service: AuthService,
        on_success: Callable[[], None],
    ):
        super().__init__(master, padding=32)
        self.auth_service = auth_service
        self.on_success = on_success

        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Connexion administrateur", font=("Segoe UI", 18)).grid(
            row=0, column=0, columnspan=2, pady=(0, 24)
        )

        ttk.Label(self, text="Nom d'utilisateur").grid(row=1, column=0, sticky="w")
        self.username_var = tk.StringVar(value="admin")
        ttk.Entry(self, textvariable=self.username_var).grid(
            row=1, column=1, sticky="ew", pady=4
        )

        ttk.Label(self, text="Mot de passe").grid(row=2, column=0, sticky="w")
        self.password_var = tk.StringVar(value="admin123")
        ttk.Entry(self, textvariable=self.password_var, show="*").grid(
            row=2, column=1, sticky="ew", pady=4
        )

        ttk.Button(self, text="Se connecter", command=self._handle_login).grid(
            row=3, column=0, columnspan=2, pady=(16, 0)
        )

    def _handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if not username or not password:
            messagebox.showwarning("Champs manquants", "Veuillez renseigner les identifiants.")
            return
        if self.auth_service.verify(username, password):
            self.on_success()
        else:
            messagebox.showerror("Échec", "Identifiants incorrects.")


from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from services.auth import AuthService
from services.camera import CameraService
from services.face_store import FaceStore
from services.storage import StorageService
from services.student_service import StudentService
from ui.access_control_view import AccessControlView
from ui.add_student_view import AddStudentView
from ui.login_view import LoginView
from ui.main_menu import MainMenu
from utils.paths import ADMINS_FILE, IMAGES_DIR, STUDENTS_FILE


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Contrôle d'accès - Restaurant scolaire")
        self.geometry("1200x800")

        # Services partagés
        storage = StorageService(STUDENTS_FILE)
        self.face_store = FaceStore(IMAGES_DIR)

        self.auth_service = AuthService(ADMINS_FILE)
        self.camera_service = CameraService()
        self.student_service = StudentService(storage, self.face_store)

        self.current_view: tk.Widget | None = None
        self.show_login()

    def _set_view(self, widget: tk.Widget):
        if self.current_view is not None:
            teardown = getattr(self.current_view, "teardown", None)
            if callable(teardown):
                teardown()
            self.current_view.destroy()
        self.current_view = widget
        self.current_view.pack(fill="both", expand=True)

    def show_login(self):
        self._set_view(
            LoginView(
                self,
                auth_service=self.auth_service,
                on_success=self.show_dashboard,
            )
        )

    def show_dashboard(self):
        self._set_view(
            MainMenu(
                self,
                on_add_student=self.show_add_student,
                on_access_control=self.show_access_control,
                on_logout=self.show_login,
            )
        )

    def show_add_student(self):
        self._set_view(
            AddStudentView(
                self,
                student_service=self.student_service,
                camera_service=self.camera_service,
                on_back=self.show_dashboard,
            )
        )

    def show_access_control(self):
        try:
            view = AccessControlView(
                self,
                student_service=self.student_service,
                camera_service=self.camera_service,
                face_store=self.face_store,
                on_back=self.show_dashboard,
            )
        except RuntimeError as exc:
            messagebox.showerror("Erreur", str(exc))
            return
        self._set_view(view)


if __name__ == "__main__":
    app = Application()
    try:
        app.mainloop()
    finally:
        # Nettoyage : fermer la caméra proprement
        app.camera_service.release()



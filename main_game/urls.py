from django.urls import path

# from views import LessonsView

from . import views

urlpatterns = [
    path("", views.LessonsView.as_view(), name="lessons"),
    path("<int:lesson_id>/", views.LessonView.as_view(), name="lesson"),
    path("add/", views.EditView.as_view(), name="edit_lesson"),
    path("edit/<int:lesson_id>/", views.EditView.as_view(), name="edit_lesson"),
    path(
        "upload_audio/<int:lesson_id>/",
        views.UploadAudio.as_view(),
        name="upload_audio",
    ),
    path("practice/", views.PracticeView.as_view(), name="practice"),
]

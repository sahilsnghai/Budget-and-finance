from django.urls import path
from . import views 

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("create-ticket/", views.create_ticket, name="create-ticket"),
    path("ticket-list/", views.ticket_list, name="ticket-list"),
    path("create-project/", views.create_project, name="create-project"),
    path("projects/", views.project_list, name="projects"),
    path("project/<int:pk>/", views.project, name="project"),
    path("ticket/<int:pk>/", views.ticket, name="ticket"),

    path('<str:task>/<int:pk>/edit/', views.update, name='edit'),
    path('<str:task>/<int:pk>/delete/', views.delete, name='delete'),
]
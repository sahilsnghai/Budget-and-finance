from django.urls import path
from .views import CreateHierarchy, SavesScenario
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('create-hierarchy', CreateHierarchy.as_view() , name='create-hierarchy'),
    path('save-senario', SavesScenario.as_view() , name='save-senario'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
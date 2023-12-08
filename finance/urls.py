from django.urls import path
from .views import CreateHierarchy, SavesScenario, FetchFrom, FetchScenario, GetData, AlterData
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('create-hierarchy', CreateHierarchy.as_view() , name='create-hierarchy'),
    path('save-scenario', SavesScenario.as_view() , name='save-scenario'),
    path('filter-form', FetchFrom.as_view() , name='    '),
    path('filter-scenario', FetchScenario.as_view() , name='filter-scenario'),
    path('get-data', GetData.as_view() , name='get-data'),
    path('alter-data', AlterData.as_view() , name='get-data'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
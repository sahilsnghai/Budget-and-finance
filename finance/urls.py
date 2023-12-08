from django.urls import path
from .views import CreateHierarchy, SavesScenario, FetchFrom, FetchScenario, GetData, AlterData, filterColumn
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('create-hierarchy', CreateHierarchy.as_view() , name='create-hierarchy'),
    path('save-scenario', SavesScenario.as_view() , name='save-scenario'),
    path('filter-form', FetchFrom.as_view() , name='filter-form'),
    path('filter-scenario', FetchScenario.as_view() , name='filter-scenario'),
    path('get-data', GetData.as_view() , name='get-data'),
    path('alter-data', AlterData.as_view() , name='get-data'),
    path('filter-column', filterColumn.as_view() , name='filter-column'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
from .views import (
    CreateHierarchy,
    SavesScenario,
    FetchFrom,
    FetchScenario,
    GetData,
    AlterData,
    filterColumn,
    GetScenario,
    CreateScenario,
    UpdateChangeValue
)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("create-form", CreateHierarchy.as_view(), name="create-form"),
    path("save-scenario", SavesScenario.as_view(), name="save-scenario"),
    path("filter-form", FetchFrom.as_view(), name="filter-form"),
    path("filter-scenario", FetchScenario.as_view(), name="filter-scenario"),
    path("get-data", GetData.as_view(), name="get-data"),
    path("alter-data", AlterData.as_view(), name="get-data"),
    path("filter-column", filterColumn.as_view(), name="filter-column"),
    path("get-scenario", GetScenario.as_view(), name="get-scenario"),
    path("create-scenario", CreateScenario.as_view(), name="create-scenario"),
    path("update-scenario", UpdateChangeValue.as_view(), name="update-scenario"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from .views import (
    CreateHierarchy,
    SavesScenario,
    FetchFrom,
    FetchScenario,
    GetData,
    filterColumn,
    GetScenario,
    CreateScenario,
    UpdateChangePrecentage,
    UpdateChangeValue,
    UpdateBudget,
    TokenAPIView,
    Login
)


urlpatterns = [
    path("create-form", CreateHierarchy.as_view(), name="create-form"),
    path("save-scenario", SavesScenario.as_view(), name="save-scenario"),
    path("filter-form", FetchFrom.as_view(), name="filter-form"),
    path("filter-scenario", FetchScenario.as_view(), name="filter-scenario"),
    path("get-data", GetData.as_view(), name="get-data"),
    path("filter-column", filterColumn.as_view(), name="filter-column"),
    path("get-scenario", GetScenario.as_view(), name="get-scenario"),
    path("create-scenario", CreateScenario.as_view(), name="create-scenario"),
    path("update-scenario", UpdateChangePrecentage.as_view(), name="update-scenario"),
    path("update-value", UpdateChangeValue.as_view(), name="update-value"),
    path("update-actual", UpdateBudget.as_view(), name="update-actual"),
    path('sso', TokenAPIView.as_view(), name='token_obtain_pair'),
    path('login', Login.as_view(), name='login'),

]

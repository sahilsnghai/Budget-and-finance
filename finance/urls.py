# Copyright © Lumenore Inc. All rights reserved.
# This software is the confidential and proprietary information of
# Lumenore Inc. "Confidential Information".
# You shall * not disclose such Confidential Information and shall use it only in
# accordance with the terms of the intellectual property agreement
# you entered into with Lumenore Inc.
# THIS SOFTWARE IS INTENDED STRICTLY FOR USE BY Lumenore Inc.
# AND ITS PARENT AND/OR SUBSIDIARY COMPANIES. Lumenore
# MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE SOFTWARE,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.
# Lumenore SHALL NOT BE LIABLE FOR ANY DAMAGES SUFFERED BY ANY PARTY AS A RESULT
# OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

"""urls"""

from django.urls import path
from .views import (
    CreateHierarchy,
    SavesScenario,
    FetchFrom,
    FetchScenario,
    GetData,
    FilterColumn,
    GetScenario,
    CreateScenario,
    UpdateChangePrecentage,
    UpdateChangeValue,
    UpdateBudget,
    TokenAPIView,
)


urlpatterns = [
    path("create-form", CreateHierarchy.as_view(), name="create-form"),
    path("save-scenario", SavesScenario.as_view(), name="save-scenario"),
    path("filter-form", FetchFrom.as_view(), name="filter-form"),
    path("filter-scenario", FetchScenario.as_view(), name="filter-scenario"),
    path("get-data", GetData.as_view(), name="get-data"),
    path("filter-column", FilterColumn.as_view(), name="filter-column"),
    path("get-scenario", GetScenario.as_view(), name="get-scenario"),
    path("create-scenario", CreateScenario.as_view(), name="create-scenario"),
    path("update-scenario", UpdateChangePrecentage.as_view(), name="update-scenario"),
    path("update-value", UpdateChangeValue.as_view(), name="update-value"),
    path("update-actual", UpdateBudget.as_view(), name="update-actual"),
    path('sso', TokenAPIView.as_view(), name='sso'),
]

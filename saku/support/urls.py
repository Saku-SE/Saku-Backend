from django.urls import path

from .views import GeneralAdviceView

app_name = "support"
urlpatterns = [
    path("/advice", GeneralAdviceView.as_view(), name="general_advice"),
]

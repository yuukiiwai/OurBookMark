from django.urls import path
from .views import register,detail,serchprocess,tagD,tagSaveApi

app_name = 'assemble'

urlpatterns = [
    path('new/',register,name='new'),
    path('detail/<uuid:url_id>/',detail,name='detail'),
    path('serchapi/',serchprocess,name="serchapi"),
    path('tagDapi/',tagD,name="tagDapi"),
    path('tagSaveApi/',tagSaveApi,name="tagSaveApi"),
]
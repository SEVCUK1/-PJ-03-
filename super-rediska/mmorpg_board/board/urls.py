from django.urls import path
from django.urls import path
from .views import image_upload_view
from .views import RespondCreateView
from .views import AddComment

from . import views
from .views import PostList, PostItem, PostCreate, PostEdit, PostDelete, CommentDetail, CommentEdit, \
    CommentDelete, AddComment, Index, Responses_List, AcceptResponseView


urlpatterns = [
    path('', PostList.as_view(), name='post_list'),
    path('<int:pk>/', PostItem.as_view(), name='post_detail'),
    path('index/', Index.as_view(), name='index'),
    path('upload/', views.image_upload_view, name='image_upload'),

    path('create/', PostCreate.as_view(), name='post_create'),
    path('<int:pk>/edit/', PostEdit.as_view(), name='post_edit'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),

    path('responses/', Responses_List.as_view(), name='comments'),
    # Список комментариев по адресу /board/responses/
    path('response/<int:pk>/', CommentDetail.as_view(), name='one_comment'),
    # Детали комментария по адресу /board/response/<id>/
    path('response/<int:pk>/edit/', CommentEdit.as_view(), name='comment_edit'),
    # Редактирование комментария по адресу /board/response/<id>/edit/
    path('response/<int:pk>/delete/', CommentDelete.as_view(), name='comment_delete'),
    # Удаление комментария по адресу /board/response/<id>/delete/
    path('response/create/', AddComment.as_view(), name='add_comment'),
    # Добавление комментария по адресу /board/response/create/

    path('response/accept/<int:pk>/', AcceptResponseView.as_view(), name='accept_response'),

    path('upload/', image_upload_view, name='image_upload'),

    path('respond/<int:post_id>/', RespondCreateView.as_view(), name='respond'),

    path('post/<int:pk>/respond/', AddComment.as_view(), name='add_respond'),
]


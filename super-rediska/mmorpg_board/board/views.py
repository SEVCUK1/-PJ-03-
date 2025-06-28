from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm, ResponsesFilterForm
from .models import Post, Response
from django.contrib import messages 
from .filters import PostFilter
from django.urls import reverse
from .tasks import respond_send_email, respond_accept_send_email
from .forms import RespondForm
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail

class PostList(ListView):
    model = Post
    template_name = 'board/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10  # Пагинация

    def get_queryset(self):
        queryset = super().get_queryset()
        # Примените фильтрацию
        self.filterset = PostFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs  # Возвращаем отфильтрованные результаты

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class Index(ListView):
    model = Post
    template_name = 'index.html'
    context_object_name = 'posts'


class PostItem(DetailView):
    model = Post
    template_name = 'board/post_item.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_id = self.kwargs.get('pk')
        context['respond'] = "Откликнулся" if Response.objects.filter(author=self.request.user,
                                                                     ad_id=post_id) else "Мое_объявление" if self.request.user == self.get_object().author else None
        return context


def image_upload_view(request):
    """Process images uploaded by users"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Get the current instance object to display in the template
            img_obj = form.instance
            return render(request, 'index.html', {'form': form, 'img_obj': img_obj})
    else:
        form = PostForm()
    return render(request, 'index.html', {'form': form})


class PostCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = ('board.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'board/post_create.html'
    raise_exception = True

    @login_required
    def form_valid(self, form):
        form.instance.author = self.request.user  # Устанавливаем автора
        return super().form_valid(form)

    def add_post(request):
        if not request.user.has_perm('board.add_post'):
            raise PermissionDenied

    def get_success_url(self):
        return reverse('post_list')


class PostEdit(PermissionRequiredMixin, UpdateView):
    permission_required = ('board.change_post',)
    model = Post
    form_class = PostForm
    template_name = 'board/post_edit.html'
    raise_exception = True

class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('board.delete_post',)
    model = Post
    template_name = 'board/post_delete.html'
    success_url = reverse_lazy('post_list')
    raise_exception = True


class CommentDetail(DetailView):
    model = Response
    template_name = 'board/comment_detail.html'
    context_object_name = 'one_comment'


class CommentDelete(LoginRequiredMixin, DeleteView):
    model = Response
    template_name = 'board/comment_delete.html'
    success_url = reverse_lazy('post')


class CommentEdit(LoginRequiredMixin, UpdateView):
    model = Response
    template_name = 'board/comment_edit.html'
    success_url = reverse_lazy('post')


class AddComment(LoginRequiredMixin, CreateView):
    model = Response
    form_class = RespondForm
    template_name = 'board/respond_form.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        post_id = self.request.GET.get('post_id')  # Получаем ID из GET-параметра
        post = get_object_or_404(Post, id=post_id)  # Безопасное получение объекта
        form.instance.author = self.request.user
        form.instance.ad = post  # Связываем отклик с объявлением
        return super().form_valid(form)


class Responses_List(LoginRequiredMixin, ListView):
    model = Response
    template_name = 'board/responses.html'
    context_object_name = 'responses'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = None
        
        # Получаем title если передан pk
        if self.kwargs.get('pk'):
            try:
                post = Post.objects.get(id=self.kwargs.get('pk'))
                title = post.title
            except Post.DoesNotExist:
                pass
        
        # Форма фильтрации
        context['form'] = ResponsesFilterForm(self.request.user, initial={'title': title})
        context['title'] = title
        
        # Фильтрация откликов
        if title:
            post = Post.objects.get(title=title)
            context['filter_responses'] = Response.objects.filter(ad=post).order_by('-created_at')
            context['response_post_id'] = post.id
        else:
            # Отклики на посты текущего пользователя
            context['filter_responses'] = Response.objects.filter(
                ad__author=self.request.user
            ).order_by('-created_at')
        
        # Отклики текущего пользователя
        context['myresponses'] = Response.objects.filter(
            author=self.request.user
        ).order_by('-created_at')
        
        return context

    def post(self, request, *args, **kwargs):
        if self.kwargs.get('pk'):
            return HttpResponseRedirect('/responses')
        return self.get(request, *args, **kwargs)


@login_required
def response_accept(request, **kwargs):
    if request.user.is_authenticated:
        response = Response.objects.get(id=kwargs.get('pk'))
        response.status = True
        response.save()
        respond_accept_send_email.delay(response_id=response.id)
        return HttpResponseRedirect('/responses')
    else:
        return HttpResponseRedirect('/accounts/login')


@login_required
def response_delete(request, **kwargs):
    if request.user.is_authenticated:
        response = Response.objects.get(id=kwargs.get('pk'))
        response.delete()
        return HttpResponseRedirect('/responses')
    else:
        return HttpResponseRedirect('/accounts/login')
class AcceptResponseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        application = get_object_or_404(Response, id=pk)
        application.accepted = True
        application.save()

        # Уведомление пользователя, который оставил отклик
        send_notification(application.user, application)

        messages.success(request, "Отклик принят.")
        return redirect('applications_list')

def send_notification(user, application):
    # Реализация уведомления
    pass

class RespondCreateView(LoginRequiredMixin, CreateView):
    model = Response
    form_class = RespondForm
    template_name = 'board/respond_form.html'

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs.get('pk'))
        form.instance.author = self.request.user
        form.instance.ad = post
        response = super().form_valid(form)
        
        # Запуск асинхронной задачи
        respond_send_email.delay(response.id)
        
        return response

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.kwargs['pk']})
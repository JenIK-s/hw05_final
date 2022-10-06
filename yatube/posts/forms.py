from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': _('Текст поста'),
            'group': _('Группа'),
        }
        help_texts = {
            'text': _('Текс нового поста'),
            'group': _('Группа, к которой будет относиться пост')
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': _('Ваш комментарий')
        }
        help_text = {
            'text': _('Текст комментария')
        }

from django import forms

from .models import Comment, Post


POST_HELP_TEXTS = {
    'text': 'Введите текст поста',
    'group': 'Выберите сообщество',
    'image': 'Загрузите изображение',
}
COMMENT_HELP_TEXTS = {
    'text': 'Введите текст комментария'
}


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        help_texts = POST_HELP_TEXTS


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ['text', ]
        help_texts = COMMENT_HELP_TEXTS

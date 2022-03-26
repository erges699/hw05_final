from django import forms

from .models import Group, Post, Comment


class PostForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects,
        help_text='Группа, к которой будет относиться пост',
        label='Group',
        required=False)
    text = forms.CharField(
        widget=forms.Textarea,
        label="Текст поста",
        help_text='Текст нового поста')

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea,
        label="Текст комментария",
        help_text='Текст нового комментария')

    class Meta:
        model = Comment
        fields = ('text',)

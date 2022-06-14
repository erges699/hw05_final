from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Об авторе проекта'
        context['text'] = ('На создание этой страницы '
                           'у меня ушло пять минут! <br> Ай да я.')
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['text'] = ('И может быть, уже в этом тысячелетии, '
                           'я изучу все эти технологии '
                           'в совершенстве!')
        return context

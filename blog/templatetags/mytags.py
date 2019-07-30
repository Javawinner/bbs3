from django import template
from django.db.models import Count
from django.db.models.functions import TruncMonth

from blog import models

register = template.Library()


@register.simple_tag()
def multify(x, y):
    return x * y


# inclusion tag

@register.inclusion_tag('classification.html')
def get_classification_style(username):
    blog = models.Blog.objects.filter(site_name=username).first()
    article_list = models.Article.objects.filter(blog=blog)
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values_list('title', 'c',
                                                                                                       'nid')
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values_list('title', 'c', 'nid')
    month_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
        'month').annotate(c=Count('pk')).values_list('month', 'c')
    return locals()

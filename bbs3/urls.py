"""bbs3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from blog import views
from bbs3 import settings
from django.views.static import serve

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # 注册功能
    url(r'^register/', views.Register.as_view()),

    # 登录功能
    url(r'^login/', views.Login.as_view()),
    url(r'^get_valid_img/', views.Login.get_valid_img),
    url(r'^logout/', views.Login.logout),
    url(r'^set_password/', views.Login.set_password),

    # 主页
    url(r'^index/', views.index),

    # 配置media路由
    url(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),

    # 侧边栏筛选功能
    url(r'^(?P<username>\w+)/(?P<conditions>tag|category|archive)/(?P<param>.*)', views.site),

    # 配置文章详情页
    url(r'^(?P<username>\w+)/articles/(?P<article_id>\d+)$', views.article_detail),

    # 点赞点踩
    url(r'^digg/', views.digg),

    # 父评论页面
    url(r'^comment', views.comment),



    # 后台管理
    url(r'^backend/$', views.backend),
    url(r'^add_article/$', views.add_article),
    url(r'^upload_img/$', views.upload_img),

    # 配置404页面
    url(r'^(?P<username>\w+)/$', views.site),
]

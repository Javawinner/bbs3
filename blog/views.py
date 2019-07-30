from django.db.models.functions import TruncMonth
from django.shortcuts import render, HttpResponse, redirect

# Create your views here.

from django.views import View
from blog import models
from blog import myforms
from django.http import JsonResponse
from django.db.models import Count

def index(request):
    # 查出所有的文章
    article_list = models.Article.objects.all()
    category_list = models.Category.objects.annotate(c=Count('article')).values_list('title', 'c', 'nid',
                                                                                     'blog__userinfo__username')
    tag_list = models.Tag.objects.annotate(c=Count('article')).values_list('title', 'c', 'nid',
                                                                           'blog__userinfo__username')
    month_list = models.Article.objects.annotate(month=TruncMonth('create_time')).values('month').annotate(
        c=Count('pk')).values_list('month', 'c', 'blog__userinfo__username')
    return render(request, 'index.html', locals())


class Register(View):
    form = myforms.MyForm()

    def get(self, request):
        return render(request, 'register.html', {'form': self.form})

    def post(self, request):
        # 前端提交后进行校验，提交就是post请求
        # {'csrfmiddlewaretoken': ['FELJgdjWNKdUXizMQ2GAqF6QMtZxYHvquEXJodcjrL8GRaVBknZ8VINjud6bX52X'],
        #  'username': ['lxx'],
        #  'password': ['123'],
        #  'confirm_password': ['123'],
        #  'email': ['123@qq.com']}
        response = {'status': False, 'msg': None}
        form = myforms.MyForm(request.POST)
        print(form.is_valid())
        print(form.cleaned_data)
        if form.is_valid():
            # 校验通过，数据库查数据
            response['status'] = True
            response['msg'] = '注册成功'
            # {'username': 'lxx', 'password': '123', 'confirm_password': '123', 'email': '123@qq.com'}
            clean_data = form.cleaned_data
            clean_data.pop('confirm_password')  # {'username': 'lxx', 'password': '123', 'email': '123@qq.com'}
            if request.FILES:
                # < MultiValueDict: {'file_obj': [ < InMemoryUploadedFile: timg.jpeg(image / jpeg) >]} >
                clean_data['avatar'] = request.FILES.get('file_obj')
            # 前面数据准备成功了，写入数据库
            # {'username': 'lxx', 'password': '123', 'email': '123@qq.com', 'avatar': < InMemoryUploadedFile: timg.jpeg(image / jpeg) >}
            models.Userinfo.objects.create_user(**clean_data)

        else:
            # 校验不通过，返回错误信息
            response['msg'] = form.errors

        return JsonResponse(response, json_dumps_params={'ensure_ascii': False})


from django.contrib import auth


class Login(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        response = {'status': False, 'msg': None}
        print(request.POST)
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        valid_code = request.POST.get('valid_code')
        if not valid_code.upper() == request.session['valid_code'].upper():
            response['msg'] = '验证码错误'
            return JsonResponse(response, json_dumps_params={'ensure_ascii': False})

        # 参数传入用户名和密码，他会去系统表中进行查找，有相同的返回对象，没有就返回None
        usr = auth.authenticate(request, username=user, password=pwd)
        if not usr:
            response['msg'] = '用户不存在'
            return JsonResponse(response, json_dumps_params={'ensure_ascii': False})
        else:
            auth.login(request, usr)
            # 调用login系统相当于做了以下三部
            #   1.设置session和cookie
            #   2.生成request.user对象，这个对象是可以在函数视图中使用的(详情见auth中间件)
            #   3.request.user 相当于request.session
            response['status'] = True
            response['msg'] = '登录成功'
            return JsonResponse(response, json_dumps_params={'ensure_ascii': False})

    @staticmethod
    def get_valid_img(request):
        def get_random_color():
            import random
            return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        import random
        img = Image.new('RGB', (270, 35), color=get_random_color())

        draw = ImageDraw.Draw(img)
        kumo_font = ImageFont.truetype('static/font/大梁体繁简精全2016版(9月版).ttf', size=28)
        random_num = str(random.randint(0, 9))
        random_low_alpha = chr(random.randint(65, 90))
        random_upper_alpha = chr(random.randint(97, 122))

        valid_code_str = ""

        for i in range(6):
            res = random.choice([random_num, random_low_alpha, random_upper_alpha])
            draw.text([i * 40 + 20, 5], res, get_random_color(), font=kumo_font)

            # 保存验证码字符串
            valid_code_str += res

        print(111111, valid_code_str)
        request.session['valid_code'] = valid_code_str
        print(request.session)
        # img.show()

        # 设置噪点燥线
        width = 270
        height = 35
        for i in range(10):
            x1 = random.randint(0, width)
            x2 = random.randint(0, width)
            y1 = random.randint(0, height)
            y2 = random.randint(0, height)
            draw.line((x1, y1, x2, y2), fill=get_random_color())

        for i in range(200):
            draw.point([random.randint(0, width), random.randint(0, height)], fill=get_random_color())
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.arc((x, y, x + 1, y + 1), 0, 90, fill=get_random_color())

        f = BytesIO()
        img.save(f, 'png')
        data = f.getvalue()

        return HttpResponse(data)

    @staticmethod
    def logout(request):
        auth.logout(request)
        return redirect('/login/')

    @staticmethod
    def set_password(request):
        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
            return redirect('/login/')
        return render(request, 'set_password.html')


def site(request, username, **kwargs):
    blog = models.Blog.objects.filter(site_name=username).first()
    print(blog)

    if not blog:
        return render(request, 'error.html')
    else:
        article_list = models.Article.objects.filter(blog=blog)
        category_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values_list('title', 'c',
                                                                                                           'nid')
        tag_list = models.Tag.objects.annotate(c=Count('article')).values_list('title', 'c', 'nid')
        month_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values(
            'month').annotate(c=Count('pk')).values_list('month', 'c')
        print(tag_list)

    if kwargs:
        conditions = kwargs.get('conditions')
        param = kwargs.get('param')
        if conditions == 'category':
            article_list = article_list.filter(category=param)
        if conditions == 'tag':
            article_list = article_list.filter(tags=param)
        if conditions == 'archive':
            year, month = param.split('/')
            article_list = article_list.filter(create_time__year=year, create_time__month=month)

    return render(request, 'site.html', locals())


def article_detail(request, username, article_id):
    article_obj = models.Article.objects.filter(nid=article_id).first()
    blog = article_obj.blog
    comment_list = models.Comment.objects.filter(article=article_obj)
    return render(request, 'article_detail.html', locals())


# 点赞视图函数
import json
from django.db.models import F


def digg(request):
    print(request.POST)
    article_id = request.POST.get('article_id')

    print('article_id', article_id)
    # 点赞人就是当前登录人
    user_id = request.user.pk
    print(user_id)

    # 生成点赞记录
    send_dic = {'state': False, 'msg': None}
    # 判断用户没有登录
    print(11111111, request.user.is_authenticated)
    if not request.user.is_authenticated:
        send_dic['msg'] = '你未登录'
        return JsonResponse(send_dic, json_dumps_params={'ensure_ascii': False})

    # 下面的情况用户都是登录的
    # 登录用户就是文章的作者
    if request.user.username == models.Article.objects.filter(pk=article_id).first().blog.userinfo.username:
        print(1111, request.user)
        print(2222, models.Article.objects.filter(pk=article_id).first().blog.userinfo.username)
        send_dic['msg'] = '臭不要脸，给自己点赞'
        return JsonResponse(send_dic, json_dumps_params={'ensure_ascii': False})

    is_up = json.loads(request.POST.get('is_up'))
    obj = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id)
    if not obj:
        models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id)
        query_set = models.Article.objects.filter(pk=article_id)
        if is_up:
            query_set.update(up_count=F('up_count') + 1)
            send_dic['state'] = True
            send_dic['msg'] = '点赞成功'
        else:
            query_set.update(down_count=F('down_count') + 1)
            send_dic['state'] = True
            send_dic['msg'] = '点踩成功'

    else:
        send_dic['msg'] = '你已经点过赞'
    return JsonResponse(send_dic, json_dumps_params={'ensure_ascii': False})


# 评论视图函数
from django.db import transaction
from django.db.models import F
from django.contrib.auth.decorators import login_required


@login_required(login_url='/login/')
def comment(request):
    send_dic = {'state': False, 'msg': None}
    if request.is_ajax():
        print(request.POST)
        # {'comment': ['dfddffd'], 'article_id': ['2'],}
        parent_id = request.POST.get('parent_id')
        comment = request.POST.get('comment')
        article_id = request.POST.get('article_id')
        user_id = request.user.pk
        with transaction.atomic():
            # 写入数据库
            models.Comment.objects.create(content=comment, article_id=article_id, user_id=user_id,
                                          parent_comment_id=parent_id)
            models.Article.objects.filter(pk=article_id).update(comment_count=F('comment_count') + 1)
        send_dic['state'] = True
        send_dic['msg'] = '评论成功'
    return JsonResponse(send_dic, json_dumps_params={'ensure_ascii': False})

from blog.utils.my_page import Pagination

@login_required(login_url='/login/')
def backend(request):
    print(request.user.blog)
    article_list = models.Article.objects.filter(blog=request.user.blog)
    print(article_list.query)
    page_obj = Pagination(current_page=request.GET.get('page', 1), all_count=article_list.count())
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request, 'backend/backend.html', locals())


from bs4 import BeautifulSoup


def add_article(request):
    if request.method == 'POST':
        print(request.POST)
        title = request.POST.get('title')
        content = request.POST.get('content')
        # 能够帮我拿到当前用户写的所有的标签 将script删除
        res = BeautifulSoup(content, 'html.parser')
        print(type(res))
        tags = res.find_all()
        print(0000, tags)
        for tag in tags:
            print(1111, tag.name, type(tag.name))
            # 将script全部删除
            if tag.name == "script":
                tag.decompose()  # 删除指定的标签
                print(2222, tag.name)
        desc = res.text[0:150]

        # 写入数据库
        models.Article.objects.create(title=title, content=str(res), desc=desc, blog=request.user.blog)
        return redirect('/backend/backend.html')
    return render(request, 'backend/add_article.html')


from bbs3 import settings
import os


def upload_img(request):
    back_dic = {'error': ''}
    if request.method == 'POST':
        print(request.FILES)
        img_obj = request.FILES.get('imgFile')
        # 规定编辑器上传的图片全部放到media文件夹里面的upload_img文件夹下
        # 1.将文件存储到media文件夹下
        path = os.path.join(settings.BASE_DIR, 'media', 'upload_img')
        if not os.path.exists(path):
            os.mkdir(path)
        file_path = os.path.join(path, img_obj.name)
        with open(file_path, 'wb') as f:
            for line in img_obj:
                f.write(line)
        # 2.将文件路径返回给前端
        back_dic['error'] = 0
        back_dic['url'] = '/media/upload_img/%s' % img_obj.name
        """
        //成功时
        {
                "error" : 0,
                "url" : "http://www.example.com/path/to/file.ext"
        }
        //失败时
        {
                "error" : 1,
                "message" : "错误信息"
        }

        """
    return JsonResponse(back_dic)

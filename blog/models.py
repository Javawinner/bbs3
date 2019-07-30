from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class Userinfo(AbstractUser):
    '''
    用户信息
    '''
    nid = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=11, null=True, unique=True, blank=True)
    avatar = models.FileField(upload_to='avatar/', default='avatar/default.jpg')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    # 一对一关系
    blog = models.OneToOneField(to='Blog', to_field='nid', null=True)

    class Meta:
        verbose_name_plural = '用户表'

    def __str__(self):
        return self.username


class Blog(models.Model):
    '''
    个人站点表
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64, verbose_name='个人博客标题')
    site_name = models.CharField(max_length=64, verbose_name='站点名称')
    theme = models.CharField(max_length=32, verbose_name='博客主题', null=True, blank=True)

    class Meta:
        verbose_name_plural = '个人站点表'

    def __str__(self):
        return self.title


class Category(models.Model):
    '''
    博客文章分类表
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='分类标题', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')

    class Meta:
        verbose_name_plural = '博客文章分类表'

    def __str__(self):
        return self.title


class Tag(models.Model):
    '''
    标签表
    '''
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标签名称', max_length=32)
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid')

    class Meta:
        verbose_name_plural = '标签表'

    def __str__(self):
        return self.title


class Article(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章描述')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    content = models.TextField()

    # 添加评论数，点赞数，点猜数，避免查询时候跨表获取
    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)

    # 外键关系
    blog = models.ForeignKey(to='Blog', to_field='nid', null=True)
    category = models.ForeignKey(to='Category', to_field='nid', null=True)
    tags = models.ManyToManyField(to='Tag', through='Article2tag', through_fields=('article', 'tag'))

    class Meta:
        verbose_name_plural = '文章表'

    def __str__(self):
        return self.title


class Article2tag(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='文章', to='Article', to_field='nid')
    tag = models.ForeignKey(verbose_name='标签', to='Tag', to_field='nid')

    # 联合唯一索引
    class Meta:
        verbose_name_plural = '文章表标签表多对多关系'
        unique_together = [('article', 'tag'), ]

    def __str__(self):
        v = self.article.title + '---' + self.tag.title
        return v


class ArticleUpDown(models.Model):
    '''
    点赞表
    '''
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(to='Userinfo', null=True)
    article = models.ForeignKey(to='Article', null=True)
    is_up = models.BooleanField(default=False)

    # 联合唯一索引
    class Meta:
        verbose_name_plural = '点赞表'
        unique_together = [('user', 'article'), ]

    def __str__(self):
        return self.user.username


class Comment(models.Model):
    '''
    评论表
    根评论 >>>
    子评论 >>>
    '''
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to='Article', to_field='nid', verbose_name='评论文章')  # 一对多
    user = models.ForeignKey(to='Userinfo', to_field='nid', verbose_name='评论者')  # 一对多
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    parent_comment = models.ForeignKey(to='self', null=True)

    class Meta:
        verbose_name_plural = '评论表'

    def __str__(self):
        return self.content

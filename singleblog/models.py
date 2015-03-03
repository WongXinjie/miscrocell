# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.db import models

class Author(models.Model):
    user_name = models.CharField(max_length=100, unique=True,  verbose_name=u'用户名')
    email = models.EmailField(unique=True, verbose_name=u'邮箱')
    password = models.CharField(max_length=200, verbose_name=u'密码')
    url = models.CharField(max_length=50, unique=True, default='', verbose_name=u'个性域名')
    registered_date = models.DateTimeField(auto_now_add=True, verbose_name=u'加入时间')
    level = models.IntegerField(default=1, verbose_name=u'等级')
    visitors = models.IntegerField(default=0,  verbose_name=u'主页访问量')
    description = models.TextField(default="", verbose_name=u'作者简介')
    is_active = models.BooleanField(default=True, verbose_name=u'是否禁用')
    avatartype = models.SmallIntegerField(default=1, verbose_name=u'头像类型')

    def __unicode__(self):
        return self.user_name

    def get_avatar_url(self):
	url = "/static/images/user_avatar_%d_large.png" % self.avatartype
	return url

    class Meta:
        ordering = ['id']
        verbose_name_plural = verbose_name = u'作者'


class Category(models.Model):
    category_name = models.CharField(max_length=100, verbose_name=u'分类')
    author = models.ForeignKey(Author, verbose_name=u'作者')

    def __unicode__(self):
        return self.category_name

    class Meta:
	ordering = ['id']
	verbose_name_plural = verbose_name = u'分类'

class Tag(models.Model):
    tag_name = models.CharField(max_length=100, verbose_name=u'标签')
    author = models.ForeignKey(Author, verbose_name=u'作者')

    def __unicode__(self):
        return self.tag_name
   
    class Meta:
	ordering = ['id']
	verbose_name_plural = verbose_name = u'标签'


class Blog(models.Model):
    title = models.CharField(max_length=200, verbose_name= u'标题')
    content = models.TextField(verbose_name=u'内容')
    count = models.IntegerField(default=0, verbose_name=u'阅读次数')
    published_date = models.DateTimeField(auto_now_add=True, verbose_name=u'发表时间')
    updated_date = models.DateTimeField(verbose_name=u'修改时间')
    author = models.ForeignKey(Author, verbose_name=u'作者')
    #is_delete = models.BooleanField(default=False, verbose_name=u'是否删除')
    visible = models.BooleanField(default=True, verbose_name=u'公开可见')
    markdown = models.BooleanField(default=False, verbose_name=u'是否使用Markdown')
    category = models.ForeignKey(Category, verbose_name=u'分类')
    tag = models.ManyToManyField(Tag, verbose_name=u'标签')

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-published_date']
        verbose_name_plural = verbose_name = u'博客'


class Comment(models.Model):
    content = models.CharField(max_length=280, verbose_name=u'内容')
    add_time = models.DateTimeField(auto_now=True, verbose_name=u'评论时间')
    sender = models.ForeignKey(Author, verbose_name=u'发送者')
    receiver_id = models.IntegerField(verbose_name=u'接收者')
    has_been_read = models.BooleanField(default=False, verbose_name=u'是否已读') 
    blog = models.ForeignKey(Blog, verbose_name=u'博客')
    #is_delete = models.BooleanField(default=False, verbose_name=u'是否删除')


    def __unicode__(self):
        return self.content

    class Meta:
        ordering = ['id']
        verbose_name_plural = verbose_name = u'评论'

class Message(models.Model):
	content = models.CharField(max_length=280, verbose_name=u'内容')
	sended_time = models.DateTimeField(auto_now=True, verbose_name=u'发送时间')
	sender_id = models.IntegerField(verbose_name=u'发送者')
	receiver_id = models.IntegerField(verbose_name=u'接收者')
	has_been_read = models.BooleanField(default=False, verbose_name=u'是否已读')
	receiver_delete = models.BooleanField(default=False, verbose_name=u'收信者删除')
	sender_delete = models.BooleanField(default=False, verbose_name=u'发信者删除')
	
	def __unicode__(self):
		return self.content
	
	def get_sender_name(self):
		sender = get_object_or_404(Author, pk=self.sender_id)
		return sender.user_name
	
	class Meta:
		ordering = ['-id']









 

    

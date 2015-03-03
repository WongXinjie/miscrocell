#-*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404, RequestContext, redirect,render
from django.template import loader, RequestContext as TemplateRequestContext
from django.utils.encoding import smart_str, smart_unicode
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from sae.mail import send_mail
from blog import settings
from models import Author, Blog, Comment, Message, Category, Tag
from datetime import datetime
from DjangoVerifyCode import Code
from decorators import login_required
from upload_images import upload 
from utils import color_tags, all_user_tags
import json, os, time
import clean_context
import auth

def index(request):
	blog_list = Blog.objects.filter(visible=True)
	paginator = Paginator(blog_list, 4)

	page = request.GET.get("page", "")
	try:
		blogs = paginator.page(page)
	except PageNotAnInteger:
		blogs = paginator.page(1)
	except EmptyPage:
		blogs = paginator.page(paginator.num_pages)
	
	top5blogs = Blog.objects.filter(visible=True).order_by('-count')[0:5]
	tags = all_user_tags()
	login_author = None
	if 'login_author' in request.session:
		login_author = request.session['login_author']
	return render_to_response("index.html", {"blogs": blogs, "login_author": login_author, "top5blogs": top5blogs, "paginator": paginator, "tags": tags}) 
	

def archive(request):
	arcdate = request.GET.get("arcdate", "")
	if arcdate:
		year, month = arcdate.split("-")
	else:
		year, month = "", ""

	blog_list = Blog.objects.filter(visible=True).order_by('-published_date')
	#get ['2014-09', '2014-10', ...]
	time_list = list(set([ blog.published_date.strftime("%Y-%m") for blog in blog_list]))

	if year and month and year.isdigits() and month.isdigit():
		blog_list = blog_list.filter(Q(published_date__year=int(year) & Q(published_date__month=int(month))))

	paginator = Paginator(blog_list, 10)
	
	page = request.GET.get("page", "")
	try:
		blogs = paginator.page(page)
	except PageNotAnInteger:
		blogs = paginator.page(1)
	except EmptyPage:
		blogs = paginator.page(paginator.num_pages)

	login_author = None
	if 'login_author' in request.session:
		login_author = request.session['login_author']
	return render_to_response("archive.html", {"blogs": blogs, "login_author": login_author, "time_list": time_list, "paginator": paginator})
	
	
def view_author(request, id):
	author = get_object_or_404(Author, pk=id)
	if author.url:
		return HttpResponseRedirect("/author/%s" % author.url)
	blog_list = author.blog_set.all()
	paginator = Paginator(blog_list, 4)

	page = request.GET.get('page', '')
	try:
		blogs = paginator.page(page)
	except PageNotAnInteger:
		blogs = paginator.page(1)
	except EmptyPage:
		blogs = paginator.page(paginator.num_pages)
	login_author = None
	if 'login_author' in request.session:
		login_author = request.session['login_author']
	
	categories = author.category_set.all()

	if login_author and author.id == login_author.id:
		comment_list = Comment.objects.filter(receiver_id=author.id)
		new_comment_list = comment_list.filter(has_been_read=False)
		#history_comment_list = comment_list.filter(has_been_read=True)
		
		message_list = Message.objects.filter(receiver_id=author.id)
		new_message_list = message_list.filter(has_been_read=False)
		tags = author.tag_set.all()
		#history_message_list = message_list.filter(has_been_read=True)	
		return render_to_response("author_admin.html", {"author": author, "login_author": login_author, "blogs": blogs, "new_comment_list": new_comment_list, "new_message_list": new_message_list, "total_count": len(new_message_list)+len(new_comment_list), "categories": categories, "tags": tags, "paginator": paginator}, RequestContext(request))
	else:
		tags = color_tags(author) 
		author.visitors += 1
		author.save()
		return render_to_response("author_page.html", {"author": author, "login_author": login_author, "blogs": blogs, "categories": categories, "tags": tags, "paginator":paginator}, RequestContext(request))


def view_url(request, url):
	author = get_object_or_404(Author, url=url)
	blog_list = author.blog_set.all()
	paginator = Paginator(blog_list, 4)

	page = request.GET.get('page', '')
	try:
		blogs = paginator.page(page)
	except PageNotAnInteger:
		blogs = paginator.page(1)
	except EmptyPage:
		blogs = paginator.page(paginator.num_pages)
	login_author = None
	if 'login_author' in request.session:
		login_author = request.session['login_author']
	
	categories = author.category_set.all()

	if login_author and author.id == login_author.id:
		comment_list = Comment.objects.filter(receiver_id=author.id)
		new_comment_list = comment_list.filter(has_been_read=False)
		#history_comment_list = comment_list.filter(has_been_read=True)
		
		message_list = Message.objects.filter(receiver_id=author.id)
		new_message_list = message_list.filter(has_been_read=False)
		tags = author.tag_set.all()
		#history_message_list = message_list.filter(has_been_read=True)	
		return render_to_response("author_admin.html", {"author": author, "login_author": login_author, "blogs": blogs, "new_comment_list": new_comment_list, "new_message_list": new_message_list, "total_count": len(new_message_list)+len(new_comment_list), "categories": categories, "tags": tags, "paginator": paginator}, RequestContext(request))
	else:
		tags = color_tags(author) 
		author.visitors += 1
		author.save()
		return render_to_response("author_page.html", {"author": author, "login_author": login_author, "blogs": blogs, "categories": categories, "tags": tags, "paginator":paginator}, RequestContext(request))


def view_blog(request, id):
    blog = get_object_or_404(Blog, pk=id)
    blog.count += 1
    blog.save()

    author = get_object_or_404(Author, pk=blog.author.id)
    comments = blog.comment_set.all()
    login_author = None
    if 'login_author' in request.session:
	login_author = request.session['login_author']
    return render_to_response("blog_page.html", {"author": author,"login_author": login_author,  "blog": blog, "comments": comments}, RequestContext(request))


def search(request):
	query = request.GET.get('title', '')
	if query:
		query_set = (Q(title__icontains = query))
		blogs = Blog.objects.filter(query_set).distinct()

		authors = Author.objects.filter(Q(user_name__icontains = query))
	else:
		blogs = []
		authors = []
	top5blogs = Blog.objects.filter(visible=True).order_by('-count')[0:5]
	login_author = None
	if 'login_author' in request.session:
		login_author = request.session['login_author']
	return render_to_response("search_result.html", {"blogs": blogs, "authors": authors, "login_author": login_author, "top5blogs": top5blogs})
	
def category(request, cid):
	category = Category.objects.get(pk=cid) 
	author = category.author 

	blog_list = category.blog_set.all()
	paginator = Paginator(blog_list, 4)

	page = request.GET.get("page", "")
	try:
		blogs = paginator.page(page)
	except PageNotAnInteger:
		blogs = paginator.page(1)
	except EmptyPage:
		blogs = paginator.page(paginator.num_pages)
	
	categories = author.category_set.all() 
	tags = color_tags(author) 
	login_author = None
	if 'login_author' in request.session:
		login_author = request.session['login_author']
	return render_to_response("author_page.html", {"author": author, "login_author": login_author, "blogs": blogs, "categories": categories, "tags": tags, "paginator": paginator})

def tag(request, tid):
	tag = Tag.objects.get(pk=tid)
	author = tag.author

	blog_list = tag.blog_set.all()
	paginator = Paginator(blog_list, 4)
	page = request.GET.get("page", "")
	try:
		blogs = paginator.page(page)
	except PageNotAnInteger:
		blogs = paginator.page(1)
	except EmptyPage:
		blogs = paginator.page(paginator.num_pages)

	categories = author.category_set.all() 
	tags = color_tags(author)
	login_author = None
	if 'login_author' in request.session:
		login_author =  request.session['login_author']
	return render_to_response("author_page.html", {"author": author, "login_author": login_author, "blogs": blogs, "categories": categories, "tags": tags, "paginator": paginator})
	
def register(request):
    if request.method == 'GET':
	return render_to_response("register.html", {}, RequestContext(request))

    username = request.POST.get("username", "")
    email = request.POST.get("email", "")
    password = request.POST.get("password2", "")
    verify = request.POST.get("verify", "")

    #response_data = {}
    code = Code(request)
    if not code.check(verify):
	#response_data['status'] = 'verify_code_error'
	#return HttpResponse(json.dumps(response_data), content_type="application/json")
	return render_to_response("register.html", {"user_name_taken_error": False, "email_taken_error": False, "verify_code_error":True, "username": username, "email": email}, RequestContext(request))
    login_author = auth.register_auth(email, username, password)
    if login_author:
	login_author.url=''
        login_author.save()
        request.session['login_author'] = login_author
	category = Category(category_name='未知分类', author = login_author)
	category.save()
	return HttpResponseRedirect('/author/%d' % login_author.id)
    else:
	exist_author = Author.objects.filter(email=email)
	if exist_author:
		#response_data['status'] = 'email_taken_error'
		email_taken_error = True
	exist_author = Author.objects.filter(user_name=username)
	if exist_author:
		#response_data['status'] = 'user_name_taken_error'
		username_taken_error = True
    #print json.dumps(response_data)
    #return HttpResponse(json.dumps(response_data))
        return render_to_response("register.html", {"username_taken_error": username_taken_error, "email_taken_error": email_taken_error, "verify_code_error": False},  RequestContext(request))

		
def login(request):
    if request.method == 'GET':
        return render_to_response("login.html", {"account_error": False, "trytime": 0 },  RequestContext(request))

    email = request.POST.get("email", "")
    password = request.POST.get("password", "")
    trytime = request.POST.get("trytime", "")
    if trytime.isdigit():
	trytime = int(trytime) + 1
    else:
	trytime = 3
	
    if trytime > 2:
	verify = request.POST.get("verify", "")
	code = Code(request)
	if not code.check(verify):
		return render_to_response("login.html", {"account_error": True, "trytime":  trytime}, RequestContext(request))

    login_author = auth.login_auth(email, password)
    if login_author:
        request.session['login_author'] = login_author
        return HttpResponseRedirect("/")
    else:
        return render_to_response("login.html", {"account_error": True, "trytime": trytime}, RequestContext(request))


def forget_password(request):
	response_data = {}
	response_data['status'] = ""
	email = request.POST.get("email", "")
	if not email:
		response_data['status'] = 'email_error'
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	try:
		author = Author.objects.get(email=email)
	except Author.DoesNotExist:
		response_data['status'] = 'email_does_not_exist'
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	password = auth.get_random_password()
	author.password = auth.get_hash_password(email, password)
	author.save()
	
	subject = u'重置微克密码'
	body = u'%s先生/女士，您的微克帐号新密码为%s，请登录微克后修改为一个容易记忆的密码' % (author.user_name, password)
	#subject = subject.encode("utf-8")
	#body = body.encode("utf-8")
	send_mail(to=email, subject=subject, body=body, smtp=(settings.EMAIL_HOST, settings.EMAIL_POST, settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD, settings.EMAIL_USE_TLS))
	#send_mail(subject, body, settings.EMAIL_HOST_USER, [email], fail_silently=False)
	response_data['status'] = 'success'
	return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required("/login")
def logout(request):
    try:
        del request.session['login_author']
    except KeyError:
        pass
    return HttpResponseRedirect("/")


@login_required("/login")
def add_blog(request):
    if request.method == 'GET':
	login_author = None
	if 'login_author' in request.session:
		login_author = request.session['login_author']
	categories = login_author.category_set.all()
	tags = login_author.tag_set.all()	
        return render_to_response("edit_page.html", {"login_author": login_author, "categories": categories, "tags": tags}, RequestContext(request))
    
    login_author = request.session['login_author']
    title = request.POST.get("title", "")
    content = request.POST.get("content", "")
    cid = request.POST.get("cid", "")
    tags_list = request.POST.get("tags", "")

    if not content:
	return render_to_response("edit_page.html", {"login_author": login_author}, RequestContext(request))
 
    visible_status = request.POST.get("visible_status", "")
    if visible_status == 'private':
	visible = False
    else:
	visible = True
	

    author = request.session['login_author']
    if cid and cid.isdigit():
	category = get_object_or_404(Category, pk=int(cid))
    else:
	category = Category.objects.filter(author_id = author.id)[0]
    blog = Blog(title=title, content=content, author=author, category=category, visible=visible, updated_date=datetime.now())
    blog.count -= 1
    blog.save()
    for tid in tags_list:
	tag = get_object_or_404(Tag, pk = int(tid))
	blog.tag.add(tag)
    blog.save()
    return HttpResponseRedirect("/article/%d" % blog.id)



@login_required("/login")
def edit_blog(request, id):
    blog = get_object_or_404(Blog, pk=id)
    author = request.session['login_author']
    login_author=None
    if author.id != blog.author.id:
        return HttpResponseRedirect("/article/%d" % blog.id)
	
    blog.content = clean_context.get_original_data(blog.content) 
    if request.method == 'GET':
	if 'login_author' in request.session:
		login_author = request.session['login_author']
	categories = login_author.category_set.all()
	tags = login_author.tag_set.all()
        return render_to_response("edit_page.html", {"login_author": login_author, "blog": blog, "categories": categories, "tags": tags},  RequestContext(request))

    title = request.POST.get("title", "")
    content = request.POST.get("content", "")

    if not content:
	return render_to_response("edit_page.html", {"login_author": login_author, "blog": blog},  RequestContext(request))
    
    visible_status = request.POST.get("visible_status", "")
    if visible_status == 'private':
	visible = False
    else:
	visible = True

    cid = request.POST.get("cid", "")
    if cid and cid.isdigit():
	category = get_object_or_404(Category, pk = int(cid))
    else:
	category = Category.objects.filter(author_id = author.id)[0]

    tags_list = request.POST.getlist("tags", "")

    blog.title=title
    blog.content=content
    blog.category = category
    blog.visible=visible
    blog.updated_date=datetime.now()
    blog.count -= 1
    blog.save()
    
    for tid in tags_list:
	tag = get_object_or_404(Tag, pk = int(tid))
	blog.tag.add(tag)
    blog.save()
    return HttpResponseRedirect("/article/%d" % blog.id)


@login_required("/login")
def remove_blog(request, id):
    blog = get_object_or_404(Blog, pk=id)
    author = request.session['login_author']
    if author.id != blog.author.id:
        return HttpResponseRedirect("/article/%d" % blog.id)
    #just set it not visible
    #blog.update(is_delete=True)
    #delete it!!
    comment_set = blog.comment_set.all().delete()
    blog.delete()
    return HttpResponseRedirect("/author/%d" % author.id)


@login_required("/login")
def add_comment(request, id):
    blog = get_object_or_404(Blog, pk=id)
    author = request.session['login_author']
    comment = None

    if request.method == 'POST':
	content = request.POST.get("content", "")
	receiver_id = blog.author.id

	if content.startswith("@") and ":" in content:
		uname = content.split(":")[0].split("@")[1]
		try:
			receiver = Author.objects.get(user_name=uname)
			receiver_id = receiver.id
		except Author.DoesNotExist:
			pass
	comment = Comment(sender=author, blog=blog, content=content, receiver_id=receiver_id)
	comment.save()
    #return HttpResponseRedirect("/article/%d" % blog.id)
    t = loader.get_template('comment_piece.html')
    c = TemplateRequestContext(request, {"comment": comment, "login_author": author})
    return HttpResponse(t.render(c))

@login_required("/login")
def edit_category(request):
	cid = request.POST.get("cid", "")
	cname = request.POST.get("cname", "")
	login_author = request.session['login_author']
	category_set = Category.objects.filter(category_name=cname, author_id=login_author.id)
	if cname.strip() and not category_set:
		if cid and cid.isdigit():
			category = get_object_or_404(Category, pk=int(cid))
		else:
			category = Category(author = login_author)
		category.category_name = cname
		category.save()
		result = 'SUCCESS'
		msg = '添加/修改成功'
	elif not cname.strip():
		result = 'FAIL'
		msg = '分类不能为空'
	else:
		result = 'FAIL'
		msg = '分类已存在'
	response_data = {'status': result, 'msg': msg}
	return HttpResponse(json.dumps(response_data))


@login_required("/login")
def edit_tag(request):
	tid = request.POST.get("tid", "")
	tname = request.POST.get("tname", "")
	login_author = request.session['login_author']
	tag_set = Tag.objects.filter(tag_name=tname, author_id=login_author.id)
	if tname.strip() and not tag_set:
		if tid and tid.isdigit():
			tag = get_object_or_404(Tag, pk=int(tid))
		else:
			tag = Tag(author=login_author)
		tag.tag_name = tname
		tag.save()
		result = 'SUCCESS'
		msg = '添加/修改成功'
	elif not tname.strip():
		result = 'FAIL'
		msg = '标签不能为空'
	else:
		result = 'FAIL'
		msg = '标签已存在'
	response_data = {'status': result, 'msg':msg}
	return HttpResponse(json.dumps(response_data))
	
@login_required("/login")
def remove_comment(request, id):
    comment = get_object_or_404(Comment, pk=id)
    blog = comment.blog
    blog.count -= 1
    blog.save() 
    author = request.session['login_author']
    if author.id == comment.sender.id or author.id == blog.author.id:
        comment.delete()

    return HttpResponseRedirect("/article/%d" % blog.id)

@login_required("/login")
def read_comment(request, id):
	comment = get_object_or_404(Comment, pk=id)
	blog = comment.blog
	comment.has_been_read = True
	comment.save()
	return HttpResponseRedirect("/article/%d" % blog.id)

@login_required("/login")
def send_letter(request):
	sender = request.session['login_author']
	
	response_data ={}
	response_data['status'] = 'fail'

	if request.method == 'POST':
		uid = request.POST.get("uid", "")
		content = request.POST.get("content", "")
		receiver = get_object_or_404(Author, pk=int(uid))
		
		if len(content) == 0:
			return HttpResponseRedirect("/author/%d" % receiver.id)
		
		message = Message(content=content, sended_time=datetime.now(), sender_id=sender.id, receiver_id=receiver.id)
		message.save()
		response_data['status'] = 'success'
		response_data['content'] = smart_str(content)
		response_data['sended_time'] = message.sended_time.strftime("%Y-%m-%d %H:%M:%S")
		response_data['sender_name'] = sender.user_name
	return HttpResponse(json.dumps(response_data), content_type="application/json")
		

@login_required("/login")
def read_letter(request, id):
	login_author = request.session['login_author']
	message = get_object_or_404(Message, pk=id)
	message.has_been_read = True
	message.save()
	return HttpResponseRedirect("/user/message/view/?uid=%d&lid=%d" % (login_author.id, message.id))

@login_required("/login")
def delete_messages(request):
	login_author = request.session['login_author']
	sid = request.GET.get("sid", "")
	
	if not (sid and sid.isdigit()):
		return HttpResponseRedirect("/user/message/view/")

	sender = get_object_or_404(Author, pk=int(sid))
	Message.objects.filter(Q(sender_id=sender.id) & Q(receiver_id=login_author.id)).update(receiver_delete=True)
	Message.objects.filter(Q(sender_id=login_author.id) & Q(receiver_id=sender.id)).update(sender_delete=True)
	Message.objects.filter(sender_delete=True).filter(receiver_delete=True).delete()

	response_data = {}
	response_data['status'] = 'success'
	return HttpResponse(json.dumps(response_data), content_type="application/json")
	
	 
@login_required("/login")
def view_history_message(request):
	login_author = request.session['login_author']
	uid = request.GET.get("uid", "")
	lid = request.GET.get("lid", "")
	sid = request.GET.get("sid", "")

	if uid and uid.isdigit():
		author = get_object_or_404(Author, pk=int(uid))
	else:
		author = login_author
	
	if author.id != login_author.id:
		return HttpResponseRedirect("/author/%d" % author.id)
	
	receive_messages = Message.objects.filter(receiver_id=author.id).filter(receiver_delete=False)
	receive_message_list = list(receive_messages)
	send_messages = Message.objects.filter(sender_id=author.id).filter(sender_delete=False)
	send_message_list = list(send_messages)
	sender_id_set = set([ message.sender_id for message in receive_message_list])
	sender_id_set |= set([ message.receiver_id for message in send_message_list])
	sender_list = [ get_object_or_404(Author, pk=uid) for uid in sender_id_set ]
	if len(sender_list) == 0:
		return render_to_response("message_page.html", {"login_author": login_author}, RequestContext(request))

	message = None	
	if lid and lid.isdigit():
		message = get_object_or_404(Message, id=int(lid))

	if sid and sid.isdigit():
		sender_id = int(sid)
	elif message:
		sender_id = message.sender_id
	else:
		sender_id = sender_list[0].id
	
	sender = get_object_or_404(Author, pk=sender_id)
	received_messages = Message.objects.filter(Q(sender_id=sender_id) & Q(receiver_id=author.id))
	received_messages.update(has_been_read=True)
	received_messages = received_messages.filter(receiver_delete=False)
	received_messages = list(received_messages)
	sended_messages = Message.objects.filter(Q(sender_id=author.id) & Q(receiver_id=sender_id))
	sended_messages = sended_messages.filter(sender_delete=False)
	sended_messages = list(sended_messages)
	received_messages.extend(sended_messages)
	message_list = received_messages
	message_list.sort(key=lambda x: x.sended_time)
	
	return render_to_response("message_page.html", {"login_author": login_author, "sender": sender, "sender_list": sender_list, "message_list": message_list}, RequestContext(request))
	
		
@login_required("/login")
def ajax_set_author_info(request):
	uid = request.POST.get("uid", "")
	username = request.POST.get("username", "")
	description = request.POST.get("info", "")
	url = request.POST.get("url", "")
		
	uid = int(uid)
	author = get_object_or_404(Author, pk=uid)
	#so if user_name exist in database, what will happend ??
	#will be crash, what should we do
	response_data = {}
	#exist_author = Author.objects.filter(user_name=username)
	try:
		exist_author = Author.objects.get(user_name = username)
	except Author.DoesNotExist:
		exist_author = None
	if exist_author and exist_author.id != author.id:
		response_data['status'] = 'name_error'
		return HttpResponse(json.dumps(response_data), content_type="application/json")

	url = url.strip()
	if url and not author.url:
		try:
			exist_author = Author.objects.get(url=url)
		except Author.DoesNotExist:
			exist_author = None
		if exist_author and exist_author.id != author.id:
			response_data['status'] = 'url_error'
			return HttpResponse(json.dumps(response_data), content_type="application/json")
		else:
			author.url = url

	author.user_name = username
	author.description=description
	author.save()
	
	response_data['status'] = 'success'
	response_data['username'] = author.user_name
	response_data['info'] = author.description
	response_data['url'] = author.url 
	return HttpResponse(json.dumps(response_data), content_type="application/json")

@login_required("/login")
def reset_password(request):
	uid = request.POST.get("uid", "")
	oldpass = request.POST.get("oldpass", "")
	newpass1 = request.POST.get("newpass1", "")
	newpass2 = request.POST.get("newpass2", "")
		
	response_data = {}
	if newpass1 != newpass2:
		response_data['status'] = 'password_not_pairs'
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	
	login_author = None
	if 'login_author' in request.session:
		login_author = request.session['login_author']
	if not( login_author and login_author.id == int(uid)):
		return render(request, "login.html")
	
	email = login_author.email
	auth_author = auth.login_auth(email, oldpass)
	if not auth_author:
		response_data['status'] = 'password_incorrect'
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	
	auth_author.password = auth.get_hash_password(email, newpass2)
	auth_author.save()
	response_data['status'] = 'success'
	return HttpResponse(json.dumps(response_data), content_type="application/json")

@login_required("/login")
def set_avatar(request):
	uid = request.POST.get("uid", "")
	avatar_type = request.POST.get("avatar_type", "")
	
	response_data = {}
	if uid and uid.isdigit() and avatar_type and avatar_type.isdigit():
		author = get_object_or_404(Author, pk=int(uid))
		author.avatartype = int(avatar_type)
		author.save()
		response_data['status'] = 'success'
	else:
		response_data['status'] = 'fail'
	return HttpResponse(json.dumps(response_data), content_type="application/json")
	

def get_verifycode(request):
	code = Code(request)
	return code.display()


@csrf_exempt
def upload_images(request):
	ext_allowed = ['gif', 'jpg', 'jpeg', 'png']
	max_size = 2097152 
	img = request.FILES['imgFile']

	if not img.name:
		return HttpResponse(json.dumps({'error':1, 'message': u'请选择要上传的文件'}), content_type="application/json")

	ext = img.name.split('.')[-1]
	if ext not in ext_allowed:
		return HttpResponse(json.dumps({'error':1, 'message': u'请上传后缀为%s的文件' % ext_allowed}))

	if img.size > max_size:
		return HttpResponse(json.dumps({'error': 1, 'messate': u'上传的文件大小不能超过2MB'}))
	img_path = 'images/%s.%s' % (int(time.time()), ext)

	state =upload(img, img_path)
	if state == 'SUCCESS':
		QINIU_BASE_DOMAIN = 'http://7u2lxf.com1.z0.glb.clouddn.com/'
		url = QINIU_BASE_DOMAIN + img_path 
		return HttpResponse(json.dumps({'error': 0, 'url':url}))
	else:
		return HttpResponse(json.dumps({'error': 1, 'message': u'上传图片失败'}))


def about(request):
	login_author = None
	if 'login_author' in request.session:
		login_author = request.session['login_author']

	return render_to_response("about.html", {"login_author": login_author})


def contact(request):
	login_author = None
	if 'login_author' in request.session:
		login_author = request.session['login_author']
	return render_to_response("contact.html", {"login_author": login_author}, RequestContext(request))


def leave_message(request):
	contact = request.POST.get("contact", "")
	content = request.POST.get("content", "")
	verify = request.POST.get("verify", "")
	response_data = {}
	if 'send_time' in request.session:
		last_send_time = request.session['send_time']
		current = int(time.time())
		if current - int(last_send_time) < 3600:
			response_data['message'] = 'sended'
			return HttpResponse(json.dumps(response_data), content_type="application/json")
	if not (contact and content and verify):
		response_data['message'] = 'empty_error'
		return HttpResponse(json.dumps(response_data), content_type="application/json")
	code = Code(request)
	if not code.check(verify):
		response_data['message'] = 'verify_error'
		return HttpResponse(json.dumps(response_data), content_type="application/json")

	email = 'hgxinjie@163.com'
	subject = u'微克访客来信'
	body = contact + '\n'+ content  
	#subject = subject.encode("utf-8")
	#body = body.encode("utf-8")
	send_mail(to=email, subject=subject, body=body, smtp=(settings.EMAIL_HOST, settings.EMAIL_POST, settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD, settings.EMAIL_USE_TLS))
	request.session['send_time'] = int(time.time())	
	response_data['message'] = 'success'
	return HttpResponse(json.dumps(response_data), content_type="application/json")

	
		
	
		
		
		
	







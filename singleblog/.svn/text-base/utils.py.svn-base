#-*- coding:utf-8 -*-
import random
from models import Tag, Author

def randon_color():
	hex_str = '0123456789abcdef'
	str_slice = random.sample(hex_str, 6)
	color = '#' + ''.join(str_slice)
	if color == "#ffffff":
		return randon_color()
	else:
		return color

def color_tags(author):
	tags = author.tag_set.all()
	tag_weight = [ len(tag.blog_set.all()) for tag in tags]
	tag_list = []
	if not tag_weight:
		return tag_list
	max_weight = max(tag_weight)
	min_weight = min(tag_weight)
	weight = 3.0 /((max_weight-min_weight)+1)
	for tag in tags:
		blog_count = len(tag.blog_set.all())
		font_size = str(weight*blog_count+14) + "px"
		color = randon_color()
		tag_list.append('<a href="/tag/'+str(tag.id)+'/" style="color:'+color+'; font-size:'+font_size+';" data-toggle="tooltip" data-placement="top" title="'+str(blog_count)+'">'+ tag.tag_name + '</a>&nbsp;&nbsp;')
	return tag_list

def all_user_tags():
	tags = Tag.objects.all()
	tag_weight = [ len(tag.blog_set.all()) for tag in tags]
	max_weight = max(tag_weight)
	min_weight = min(tag_weight)
	weight = 3.0 /((max_weight-min_weight)+1)
	tag_list = []
	for tag in tags:
		blog_count = len(tag.blog_set.all())
		font_size = str(weight*blog_count+14) + "px"
		color = randon_color()
		tag_list.append('<a href="/tag/'+str(tag.id)+'/" style="color:'+color+'; font-size:'+font_size+';" data-toggle="tooltip" data-placement="top" title="'+str(blog_count)+'">'+ tag.tag_name + '</a>&nbsp;&nbsp;')
	return tag_list
	

	
		
	












	

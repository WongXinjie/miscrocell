#-*- coding: utf-8 -*-
import re
def clean_data(content):
	decoder = {">":"&gt;", "<":"&lt;", " ":"&nbsp;", "\"":"&quot;", "\'":"&#39;" }
	if len(content) == 0:
		return None
	content = re.sub("&", "&amp;", content)
	for key in decoder.keys():
		content=re.sub(key, decoder[key], content)
	content = re.sub("\n", "<br/>", content)
	return content

def get_original_data(content):
	undecoder = {"&gt;":">", "&lt;":"<", "&nbsp;":" ", "&quot;":"\"", "&#39;":"\'"}	
	content = re.sub("<br/>", "", content)
	for key in undecoder.keys():
		content=re.sub(key, undecoder[key], content)
	content = re.sub("&amp;", "&", content)
	return content

def get_clean_data(blog_content):
	content_list = blog_content.split("<code>")
	result = ''
	for content in content_list:
		if not content.strip().startswith('<pre class="prettyprint">'):
			content = clean_data(content)
		result += content
	return result

			



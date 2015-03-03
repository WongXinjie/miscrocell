#-*- coding:utf-8 -*-
import requests
import qiniu
def upload(upload_file, key):
	ACCESS_KEY = 'xxxxxxxxxxxx'
	SECRET_KEY = 'xxxxxxxxxxxx'
	bucket_name = 'staticfiles'
	auth = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
	token = auth.upload_token(bucket_name)
	ret, info = qiniu.put_data(token, key, upload_file)
	if ret is not None:
		return 'SUCCESS'
	else:
		print info
		return 'FAIL'

		

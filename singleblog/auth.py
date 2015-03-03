#-*- coding: utf-8 -*-
import hashlib
import random
from django.db.models import Q
from models import Author

def register_auth(email, username, password):
	authors = Author.objects.filter(Q(email=email)|Q(user_name=username))
	if not authors:
		hash_password = hashlib.md5(password.join(email)).hexdigest()
		author = Author(user_name=username, email=email, password=hash_password)
		return author
	else:
		return None

def login_auth(email, password):
	try:
		author = Author.objects.get(email=email)
	except Author.DoesNotExist:
		return None 
	else:
		hash_password = hashlib.md5(password.join(email)).hexdigest()
		if author.password == hash_password:
			return author 
	return None


def get_hash_password(email, password):
	hash_password = hashlib.md5(password.join(email)).hexdigest()
	return hash_password


def get_random_password():
	characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcedfghijklmnopqrstuvwxyz'
	password = "".join(random.sample(characters, 8))
	return password



from flask import Flask, request, jsonify
import pickle
import os
from hashlib import sha256
from datetime import datetime
import re
import random
import string

app = Flask(__name__)
DEFAULT_PATH = "./collections.pickle"

def hasher(password, salt = None):
	if salt == None:
		letters_and_digits = string.ascii_letters + string.digits
		salt = ''.join(random.sample(letters_and_digits, 16))
		salt = salt.encode('utf-8')
	password = sha256((password).encode('utf-8')+salt).hexdigest()
	return salt,password

def save_collection(dict_obj, filename = None):
	filename = DEFAULT_PATH if filename == None else filename
	with open(filename, "wb") as picklefile:
		pickle.dump(dict_obj, picklefile)

def load_collection(filename = None):
	filename = DEFAULT_PATH if filename == None else filename
	if os.path.exists(filename):
		with open(filename, "rb") as picklefile:
			buffered = pickle.load(picklefile)
		return buffered
	else:
		return {}

def returned(result = True, description = "", exception = None):
	return {
		"результат":result,
		"описание":description,
		"исключение": exception
		}

def email_validator(email):
	collection = load_collection()
	return not bool(collection.get(email))

def write_userinfo(userinfo):
	collection = load_collection()
	password = userinfo["пароль"]
	if not re.search("^(\w|\d|\_){8,}$", password):
		return False
	email = userinfo["почта"]
	date = datetime.now().strftime("%H:%M:%S, %d.%m.%Y")
	password = hasher(password)
	collection[email] = {"пароль": password, "дата": date, }
	save_collection(collection)
	return True

def check_auth(userinfo):
	collection = load_collection()
	email = userinfo["почта"]
	password = userinfo["пароль"]
	curr_pass = collection.get(email)
	if not curr_pass:
		return returned(False,"Пользователь не существует", "почта не существует")
	curr_pass = curr_pass["пароль"]
	checked = hasher(password, curr_pass[0])
	if curr_pass == checked:
		return returned(True, "вход успешный")
	else:
		return returned(False, "другой пароль", "неправильный пароль")



@app.route('/user/auth', methods=['POST'])
def auth():
	userinfo = request.get_json()
	return check_auth(userinfo)


@app.route('/user/reg', methods=['POST'])
def reg():
	userinfo = request.get_json()
	if email_validator(userinfo["почта"]):
		if write_userinfo(userinfo):
			return returned(True, "регистрация прошла успешно")
		else:
			return returned(False,"Должно содержать буквы, цифры" "недопустимые значения")
	else:
		return returned(False,"пользователь сущестует" "почта уже используется")




if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
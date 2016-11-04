import os
import requests
from dbms.models import User
from dbms.rdb import db

GRAPH_API_URL = '/v2.8/'

def _get_user_data(user_id):
    access_token = os.environ.get('ACCESS_TOKEN')
    return requests.get('https://graph.facebook.com'+ GRAPH_API_URL + str(user_id), params={'access_token': access_token }).json()


def user_name(user_id):
    user_pref = User.query.filter_by(user_id=user_id).first()
    if user_pref and user_pref.name != '':
        u_name = user_pref.name
    else:
        fill_user_pref(user_id)
        user_pref = User.query.filter_by(user_id=user_id).first()
        u_name = user_pref.name

    return u_name

def _user_name_internal(user_id):
    data = _get_user_data(user_id)
    if ('first_name' in data):
        return data['first_name'].encode("utf-8")
    else:
        if ('name' in data):
            return data['name'].split(' ')[0].encode("utf-8")
        else:
            return u"Unknown"


def img_url(user_id):
    try:
        return _get_user_data(user_id)['profile_pic']
    except Exception as e:
        return 'http://s32.postimg.org/hw25wtznp/def_prof_pic.jpg'


def locale(user_id):
    user_pref = User.query.filter_by(user_id=user_id).first()
    if user_pref and user_pref.locale != '':
        u_locale = user_pref.locale
    else:
        fill_user_pref(user_id)
        user_pref = User.query.filter_by(user_id=user_id).first()
        u_locale = user_pref.locale

    return u_locale


def _locale_internal(user_id):
    try:
        return _get_user_data(user_id)['locale']
    except Exception as e:
        return 'pl_PL'


def gender(user_id):
    user_pref = User.query.filter_by(user_id=user_id).first()
    if user_pref and user_pref.gender != '':
        u_gender = user_pref.gender
    else:
        fill_user_pref(user_id)
        user_pref = User.query.filter_by(user_id=user_id).first()
        u_gender = user_pref.gender

    return u_gender

def _gender_internal(user_id):
    try:
        return _get_user_data(user_id)['gender']
    except Exception as e:
        return 'male'


def fill_user_pref(user_id):
    locale_pref = _locale_internal(user_id)
    name_pref = _user_name_internal(user_id)
    gender_pref = _gender_internal(user_id)

    # check if record exists
    user_pref = User.query.filter_by(user_id=user_id).first()
    if user_pref:
        # record exists - update it
        user_pref.locale = locale_pref
        user_pref.name = name_pref
        user_pref.gender = gender_pref
    else:
        # record does Not exist - create new
        user_pref = User(user_id, locale_pref, name_pref, gender_pref)
        db.session.add( user_pref )

    db.session.commit()
    db.session.flush()

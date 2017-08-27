from random import randint

from django.conf import settings
from pyrebase import pyrebase

categories = [
    'abstract', 'animals', 'business', 'cats', 'city', 'food', 'nightlife', 'fashion', 'people', 'nature', 'sports',
    'technics', 'transport'
]


def random_category():
    len_categories = len(categories)
    first = randint(0, len_categories - 1)
    second = first
    while first == second:
        second = randint(0, len_categories - 1)
    return {'first': categories[first], 'second': categories[second]}


def get_firebase():
    return pyrebase.initialize_app(settings.FIREBASE_CONFIG)

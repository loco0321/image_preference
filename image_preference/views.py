from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.base import TemplateView, View

from image_preference.forms import AuthenticationFormCustom
from image_preference.utilities import random_category, get_firebase


class Home(TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context.update(random_category())
        return context


class LoginViewCustom(LoginView):
    form_class = AuthenticationFormCustom
    template_name = 'pages/login.html'


class SelectImageView(View):
    def get(self, request, *args, **kwargs):
        firebase = get_firebase()
        db = firebase.database()
        token = self.request.session['firebase_user']['idToken']
        data = db.child("preferences").get(token)
        category = request.GET.get('category')
        if not category:
            messages.error(self.request, 'You need to select a image')
            return redirect('/')
        preferences = data.val()
        preference = None
        if preferences:
            preference = preferences.get(self.request.user.username)
        if not preference:
            db.child("preferences").child(self.request.user.username).set({
                'name': self.request.user.get_full_name(),
                'categories': {category: 1}
            }, token)
        else:
            categories = preference.get('categories')
            if not categories.get(category):
                categories.update({category: 1})
            else:
                categories.update({category: categories.get(category) + 1})
            db.child("preferences").child(self.request.user.username).update({
                'name': self.request.user.get_full_name(),
                'categories': categories
            }, token)
        messages.success(self.request, 'Your selection was: {}'.format(category))
        return redirect('/')

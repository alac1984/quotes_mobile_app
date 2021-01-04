from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from hoverable import HoverBehavior
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from urllib3.exceptions import HTTPError, MaxRetryError
import urllib3
import json

# base_url = 'http://loginrestformobileapp.herokuapp.com/'
base_url = 'http://127.0.0.1:8000/'
user_key = 0

store = JsonStore('token.json')
http = urllib3.PoolManager()

Builder.load_file('design.kv')


class LoginScreen(Screen):

    def sign_up(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'sign_up_screen'

    def login(self, username, password):
        try:
            r = http.request('POST', base_url, fields={
                'username': username,
                'password': password,
            })
            data = json.loads(r.data.decode('utf-8'))
            if 'key' in data.keys():
                store.put('user', token=data['key'])
                # To get the user token
                # print(store.get(username)['token'])
                self.manager.transition.direction = 'left'
                self.manager.current = 'login_screen_success'
            else:
                for key in data:
                    self.ids.error.text = f'{data[key][0]}'
        except MaxRetryError:
            self.ids.error.text = 'Unable to connect to server. Please retry later.'


class LoginScreenSuccess(Screen):

    def logout(self):
        r = http.request('POST', f'{base_url}logout/', fields={})
        data = json.loads(r.data.decode('utf-8'))
        if 'detail' in data.keys():
            self.manager.transition.direction = 'right'
            self.manager.current = 'login_screen'

    def enlight(self, feeling):
        try:
            r = http.request('GET', f'{base_url}quotes?cat={feeling}',
                             headers={"Authorization": "Token " + f"{store.get('user')['token']}"})
            data = json.loads(r.data.decode('utf-8'))
            self.ids.quote.text = data[0]['text']
        except HTTPError as e:
            print(json.loads(e.read().decode('utf-8')))


class SignUpScreen(Screen):
    def add_user(self, username, email, password1, password2):
        try:
            r = http.request('POST', f'{base_url}registration/', fields={
                'username': username,
                'email': email,
                'password1': password1,
                'password2': password2,
            })
            data = json.loads(r.data.decode('utf-8'))
            if 'key' in data.keys():
                self.manager.current = 'sign_up_screen_success'
            else:
                print(data)
        except HTTPError as e:
            print(e)
        # try:
            # response = urllib.request.urlopen(req)
            # if 'key' in json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8')):
        # except HTTPError as e:
            # message = json.loads(e.read().decode('utf-8'))
            # for key in message:
                # self.ids.error.text = f'{message[key][0]}\\n'


class SignUpScreenSuccess(Screen):
    def go_to_login(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login_screen'


class ImageButton(ButtonBehavior, HoverBehavior, Image):
    pass


class RootWidget(ScreenManager):
    pass


class MainApp(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    MainApp().run()

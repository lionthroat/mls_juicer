import pickle
import os

class UserProfile:
    def __init__(self):
        self.user = None # user's profile name
        self.data = None # user's stored MLS data
        self.colors = [] # user's personal branding or preferred colors, RGB space only

    # if the pickle file exists, open it and look for user data
    def load_user_data(self):
        if os.path.exists('user.pickle'):
            with open('user.pickle', 'rb') as handle:
                data = pickle.load(handle)
                if isinstance(data, UserProfile):
                    self.user = data.user
                    self.data = data.data
                    self.colors = data.colors

    def save_user_data(self):
        with open('user.pickle', 'wb') as handle:
             pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def set_user_name(self, user):
        self.user = user

    def get_user_name(self):
        return self.user
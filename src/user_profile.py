import pickle
import pandas as pd
import os

class UserProfile:
    def __init__(self):
        self.user = None # user's profile name
        self.data = None # user's stored MLS data
        self.colors = [] # user's personal branding or preferred colors, RGB space only

    # if the pickle file exists, open it and look for user data
    def load_user_name(self):
        if os.path.exists('user.pickle'):
            with open('user.pickle', 'rb') as handle:
                data = pickle.load(handle)
                if isinstance(data, UserProfile):
                    self.user = data.user
                    #self.data = data.data
                    #self.colors = data.colors

    def load_user_data(self):
        # Retrieve DataFrame from HDF5
        if os.path.exists(f'{self.user}.h5'):
            with pd.HDFStore(f'{self.user}.h5', mode="r") as store:
                self.data = store.get('csv_data')

    def save_user_name(self):
        # store username
        with open('user.pickle', 'wb') as handle:
             pickle.dump(self, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def save_user_data(self):
        # store user data
        if self.data is not None:
            with pd.HDFStore(f'{self.user}.h5', mode="w") as store:
                store.put('csv_data', self.data)

    def set_user_name(self, user):
        self.user = user

    def get_user_name(self):
        return self.user
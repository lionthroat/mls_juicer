import pickle
import pandas as pd
import os

class UserProfile:
    def __init__(self):
        self.user = None # user's profile name
        self.data = None # user's stored MLS data
        self.colors = [] # user's personal branding or preferred colors, RGB space only

    # Load user name
    def load_user_name(self):
        if os.path.exists(f'data/{self.user}.h5'):
            with pd.HDFStore(f'data/{self.user}.h5', mode="r") as handle:
                if 'user' in handle:
                    self.user = handle['user'][0]
                
    # Load user data (Retrieve DataFrame from HDF5)
    def load_user_data(self):
        if os.path.exists(f'data/{self.user}.h5'):
            with pd.HDFStore(f'data/{self.user}.h5', mode="r") as handle:
                if 'data' in handle:
                    print("Loading in data", flush=True)
                    self.data = handle['data']

    # Save user name
    def save_user_name(self):
        user_series = pd.Series([self.user])
        with pd.HDFStore(f'data/{self.user}.h5', mode="w") as handle:
            handle.put('user', user_series)

    # Save user data
    def save_user_data(self):
        if self.data is not None:
            with pd.HDFStore(f'data/{self.user}.h5', mode="a") as handle:
                handle.put('data', self.data)

    # Set user name
    def set_user_name(self, user):
        self.user = user

    def get_user_name(self):
        return self.user
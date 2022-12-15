import cortex
from cortex import *
import pyautogui

PROFILE_NAME = 'RUN'

class Run():
    
    def __init__(self, app_client_id, app_client_secret, **kwargs):
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=True, **kwargs)
        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(query_profile_done=self.on_query_profile_done)
        self.c.bind(load_unload_profile_done=self.on_load_unload_profile_done)
        self.c.bind(save_profile_done=self.on_save_profile_done)
        self.c.bind(new_data_labels=self.on_new_data_labels)
        self.c.bind(inform_error=self.on_inform_error)

    def start(self, profile_name, headsetId=''):
        if profile_name == '':
            raise ValueError(' Empty profile_name. The profile_name cannot be empty.')

        self.profile_name = profile_name
        self.action_idx = 0

        self.c.set_wanted_profile(profile_name)

        if headsetId != '':
            self.c.set_wanted_headset(headsetId)

        self.c.open()

    def subscribe_data(self, streams):
        self.c.sub_request(streams)

    def load_profile(self, profile_name):
        status = 'load'
        self.c.setup_profile(profile_name, status)

    def unload_profile(self, profile_name):
        self.c.setup_profile(profile_name, 'unload')

    def save_profile(self, profile_name):
        self.c.setup_profile(profile_name, 'save')

    def run_move_mouse(self):

        while True:
            while True:
                try:
                    startCode = input('\n\nTo begin the game, type "1"\n>>> ')
                    if startCode == "1":
                        break
                    else:
                        print("Invalid input")
                except ValueError:
                    print("Invalid input")
                        
            if startCode == "1":

                print("Getting USER login...")

                get_user_login = {
                    "jsonrpc": "2.0",
                    "method": "getUserLogin",
                    "id": LOGIN
                }
                self.c.ws.send(json.dumps(get_user_login, indent=4))

                profile = self.c.profile
                print(profile)

                subscribe = {
                    "jsonrpc": "2.0",
                    "method": "subscribe",
                    "params": {
                        "cortexToken": self.c.auth,
                        "session": self.c.session_id,
                        "streams": [
                            "com"
                        ]
                    },
                    "id": SUB_REQUEST_ID
                }
                self.c.ws.send(json.dumps(subscribe, indent=4))
                self.c.setup_profile(self, profile, PROFILE_NAME)

    # callbacks functions
    def on_create_session_done(self, *args, **kwargs):
        print('on_create_session_done')
        self.c.query_profile()

    def on_query_profile_done(self, *args, **kwargs):
        print('on_query_profile_done')
        self.profile_lists = kwargs.get('data')
        if self.profile_name in self.profile_lists:
            # the profile is existed
            self.c.get_current_profile()
        else:
            # create profile
            self.c.setup_profile(self.profile_name, 'create')

    def on_load_unload_profile_done(self, *args, **kwargs):
        is_loaded = kwargs.get('isLoaded')
        
        if is_loaded == True:
            self.subscribe_data(['sys'])
        else:
            print('The profile ' + self.profile_name + ' is unloaded')
            self.profile_name = ''
            # close socket
            self.c.close()

    def on_save_profile_done (self, *args, **kwargs):
        print('Save profile ' + self.profile_name + " successfully")
        self.unload_profile(self.profile_name)

    def on_new_data_labels(self, *args, **kwargs):
        data = kwargs.get('data')
        print('on_new_data_labels')
        print(data)
        if data['streamName'] == 'sys':
            # subscribe sys event successfully
            print('on_new_data_labels: start')
            self.run_move_mouse()

    def on_inform_error(self, *args, **kwargs):
        error_data = kwargs.get('error_data')
        error_code = error_data['code']
        error_message = error_data['message']

        print(error_data)

        if error_code == cortex.ERR_PROFILE_ACCESS_DENIED:
            # disconnect headset for next use
            print('Get error ' + error_message + ". Disconnect headset to fix this issue for next use.")
            self.c.disconnect_headset()

def main():

    # Please fill your application clientId and clientSecret before running script
    your_app_client_id = 'XXX'
    your_app_client_secret = 'XXX'

    r = Run(your_app_client_id, your_app_client_secret)
    r.start(PROFILE_NAME)

if __name__ =='__main__':
    main()

# -----------------------------------------------------------







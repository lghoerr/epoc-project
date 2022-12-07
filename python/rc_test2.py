import cortex
from cortex import *
import pyautogui

# name of training profile
PROFILE_NAME = 'Test2'

class Train():
    
    def __init__(self, app_client_id, app_client_secret, **kwargs):
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=True, **kwargs)
        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(query_profile_done=self.on_query_profile_done)
        self.c.bind(load_unload_profile_done=self.on_load_unload_profile_done)
        self.c.bind(save_profile_done=self.on_save_profile_done)
        self.c.bind(new_data_labels=self.on_new_data_labels)
        self.c.bind(new_sys_data=self.on_new_sys_data)
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

    def get_detection_info(self):

        print("\nGetting detection info...")
        get_detection_info = {
            "jsonrpc": "2.0",
            "method": "getDetectionInfo",
            "params": {
                "detection": "mentalCommand"
            },
            "id": 1
        }
        self.c.ws.send(json.dumps(get_detection_info, indent=4))

    def train_command(self, request):

        print("Training " + request + " command...")
        mental_command = {
            "jsonrpc": "2.0", 
            "method": "training", 
            "params": {
                "cortexToken":self.c.auth,
                "detection":"mentalCommand",
                # "detection":'facialExpression', # Maybe try this later? May work better?
                "action":request,
                "status":"start"
            }, 
            "id": TRAINING_ID
        }

        self.c.ws.send(json.dumps(mental_command, indent=4))

        time.sleep(5)
        time.sleep(10)

        mental_command2 = {
            "jsonrpc": "2.0", 
            "method": "training", 
            "params": {
                "cortexToken":self.c.auth,
                "detection":"mentalCommand",
                # "detection":'facialExpression', # Maybe try this later? May work better?
                "action":request,
                "status":"accept"
            }, 
            "id": TRAINING_ID
        }

        self.c.ws.send(json.dumps(mental_command2, indent=4))

        time.sleep(2)

    def run_move_mouse_training(self):

        while True:
            while True:
                try:
                    startCode = input('\n\nTo train commands, type "1". To begin the game, type "2"\n>>> ')
                    if startCode == "1" or startCode == "2":
                        break
                    else:
                        print("Invalid input")
                except ValueError:
                    print("Invalid input")

            if startCode == "1":
                while True:
                    try:
                        req = input("Which command would you like to train? (Neutral, Left, Right, Lift, Drop, Push)\n>>> ").lower()         

                        if req == "neutral" or req == "lift" or req == "drop" or req == "left" or req == "right" or req == "push":
                            self.train_command(req)
                            break
                        else:
                            print("Invalid input")
                    except:
                        print("Invalid input")
                        
            elif startCode == "2":

                print("Getting USER login...")

                get_user_login = {
                    "jsonrpc": "2.0",
                    "method": "getUserLogin",
                    "id": LOGIN
                }
                print("arrived here 1 ----------------------------")

                self.c.ws.send(json.dumps(get_user_login, indent=4))

                print("arrived here 2 ----------------------------")

                # profile = json.loads(self.c.ws.recv())["result"][0]
                profile = self.c.profile
                print("arrived here 2.5 ----------------------------")
                print(profile)

                print("arrived here 3 ----------------------------")
                
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

                print("arrived here 4 ----------------------------")

                self.c.ws.send(json.dumps(subscribe, indent=4))

                print("arrived here 5 ----------------------------")

                self.c.setup_profile(self, profile, PROFILE_NAME)

                print("arrived here 6 ----------------------------")

                self.c.get_mental_command_brain_map(PROFILE_NAME)
                # print("Mental Command Brain Map:", synapseData)

                print("arrived here 7 ----------------------------")

                # while True:

                #     thought = self.c.thought
                #     print(thought)

                #     maxX, maxY = pyautogui.size()

                #     try:
                #         x, y = pyautogui.position()  
                #         print("x:" + str(x))
                #         print("y:" + str(y))    
                #     except KeyboardInterrupt:
                #         print('\n')

                #     if thought == "left" and x>0:
                #         print("left")
                #         pyautogui.move(-4, None)
                #     elif thought == "right" and x<maxX:
                #         print("right")
                #         pyautogui.move(4, None)
                #     elif thought == "lift" and y<maxY:
                #         print("lift")
                #         pyautogui.move(None, -4)
                #     elif thought == "drop" and y>0:
                #         print("drop")
                #         pyautogui.move(None, 4)
                #     elif thought == "neutral":
                #         print("neutral")
                #         pyautogui.move(None, None)
                #     elif thought == "push":
                #         print("push")
                #         pyautogui.click()
    
    def train_fe_action(self, status):
        if self.action_idx < len(self.actions):
            action = self.actions[self.action_idx]
            print('train_fe_action: -----------------------------------: '+ action + ":" + status)
            self.c.train_request(detection='facialExpression',
                                 action=action,
                                 status=status)
        else:
            # save profile after training
            self.c.setup_profile(self.profile_name, 'save')
            self.action_idx = 0 # reset action_idx

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
            # subscribe sys stream to receive Training Event
            self.subscribe_data(['sys'])
        else:
            print('The profile ' + self.profile_name + ' is unloaded')
            self.profile_name = ''
            # close socket
            self.c.close()

    def on_save_profile_done (self, *args, **kwargs):
        print('Save profile ' + self.profile_name + " successfully")
        self.unload_profile(self.profile_name)

    def on_new_sys_data (self, *args, **kwargs):
        data = kwargs.get('data')
        train_event = data[1]
        # action = self.actions[self.action_idx]
        # print('on_new_sys_data: ' + action +" : " + train_event)
        if train_event == 'FE_Succeeded':
            # train action successful. you can accept the training to complete or reject the training
            # self.train_fe_action('accept')
            self.run_move_mouse_training()

        elif train_event == 'FE_Failed':
            # self.train_fe_action("reject")
            self.run_move_mouse_training()

        elif train_event == 'FE_Completed' or train_event == 'FE_Rejected':
            # training complete. Move to next action
            self.action_idx = self.action_idx + 1
            # self.train_fe_action('start')
            self.run_move_mouse_training()

    def on_new_data_labels(self, *args, **kwargs):
        data = kwargs.get('data')
        print('on_new_data_labels')
        print(data)
        if data['streamName'] == 'sys':
            # subscribe sys event successfully
            # start training
            print('on_new_data_labels: start training ')
            # self.train_fe_action('start')
            self.run_move_mouse_training()

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
    your_app_client_id = 'sZteLJ27aZCq63F2Im8yeKuAk7K1hNRIiOnw3Dm2'
    your_app_client_secret = 'RAaU3dRa8dBMkkvTzCxMheJGuxSrtIVYqvlEV1qd8WXbTPLJRm1dS15j7ZlgzojARuBzMJyPo0kczLnqwMwZ15TSOZPvXNS1ThQUKmOGrY4QQWTzV48lxI8PtOvgDJCC'

    # Init Train
    t = Train(your_app_client_id, your_app_client_secret)
    t.start(PROFILE_NAME)
    print("end start")
    t.get_detection_info()
    t.run_move_mouse_training()

if __name__ =='__main__':
    main()

# -----------------------------------------------------------







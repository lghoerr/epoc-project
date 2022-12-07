from cortex import *

def handle_result(recv_dic):
    if debug:
        print(recv_dic)

    req_id = recv_dic['id']
    result_dic = recv_dic['result']

    if req_id == HAS_ACCESS_RIGHT_ID:
        access_granted = result_dic['accessGranted']
        if access_granted == True:
            # authorize
            authorize()
        else:
            # request access
            request_access()
    elif req_id == REQUEST_ACCESS_ID:
        access_granted = result_dic['accessGranted']

        if access_granted == True:
            # authorize
            authorize()
        else:
            # wait approve from Emotiv Launcher
            msg = result_dic['message']
            warnings.warn(msg)
    elif req_id == AUTHORIZE_ID:
        print("Authorize successfully.")
        auth = result_dic['cortexToken']
        # query headsets
        query_headset()
    elif req_id == QUERY_HEADSET_ID:
        headset_list = result_dic
        found_headset = False
        headset_status = ''
        for ele in headset_list:
            hs_id = ele['id']
            status = ele['status']
            connected_by = ele['connectedBy']
            print('headsetId: {0}, status: {1}, connected_by: {2}'.format(hs_id, status, connected_by))
            if headset_id != '' and headset_id == hs_id:
                found_headset = True
                headset_status = status

        if len(headset_list) == 0:
            warnings.warn("No headset available. Please turn on a headset.")
        elif headset_id == '':
            # set first headset is default headset
            headset_id = headset_list[0]['id']
            # call query headet again
            query_headset()
        elif found_headset == False:
            warnings.warn("Can not found the headset " + headset_id + ". Please make sure the id is correct.")
        elif found_headset == True:
            if headset_status == 'connected':
                # create session with the headset
                create_session()
            elif headset_status == 'discovered':
                connect_headset(headset_id)
            elif headset_status == 'connecting':
                # wait 3 seconds and query headset again
                time.sleep(3)
                query_headset()
            else:
                warnings.warn('query_headset resp: Invalid connection status ' + headset_status)
    elif req_id == CREATE_SESSION_ID:
        session_id = result_dic['id']
        print("The session " + session_id + " is created successfully.")
        emit('create_session_done', data=session_id)
    elif req_id == SUB_REQUEST_ID:
        # handle data label
        for stream in result_dic['success']:
            stream_name = stream['streamName']
            stream_labels = stream['cols']
            print('The data stream '+ stream_name + ' is subscribed successfully.')
            # ignore com, fac and sys data label because they are handled in on_new_data
            if stream_name != 'com' and stream_name != 'fac':
                extract_data_labels(stream_name, stream_labels)

        for stream in result_dic['failure']:
            stream_name = stream['streamName']
            stream_msg = stream['message']
            print('The data stream '+ stream_name + ' is subscribed unsuccessfully. Because: ' + stream_msg)
    elif req_id == UNSUB_REQUEST_ID:
        for stream in result_dic['success']:
            stream_name = stream['streamName']
            print('The data stream '+ stream_name + ' is unsubscribed successfully.')

        for stream in result_dic['failure']:
            stream_name = stream['streamName']
            stream_msg = stream['message']
            print('The data stream '+ stream_name + ' is unsubscribed unsuccessfully. Because: ' + stream_msg)

    elif req_id == QUERY_PROFILE_ID:
        profile_list = []
        for ele in result_dic:
            name = ele['name']
            profile_list.append(name)
        emit('query_profile_done', data=profile_list)
    elif req_id == SETUP_PROFILE_ID:
        action = result_dic['action']
        if action == 'create':
            profile_name = result_dic['name']
            if profile_name == profile_name:
                # load profile
                setup_profile(profile_name, 'load')
        elif action == 'load':
            print('load profile successfully')
            emit('load_unload_profile_done', isLoaded=True)
        elif action == 'unload':
            emit('load_unload_profile_done', isLoaded=False)
        elif action == 'save':
            emit('save_profile_done')
    elif req_id == GET_CURRENT_PROFILE_ID:
        print(result_dic)
        name = result_dic['name']
        if name is None:
            # no profile loaded with the headset
            print('get_current_profile: no profile loaded with the headset ' + headset_id)
            setup_profile(profile_name, 'load')
        else:
            loaded_by_this_app = result_dic['loadedByThisApp']
            print('get current profile rsp: ' + name + ", loadedByThisApp: " + str(loaded_by_this_app))
            if name != profile_name:
                warnings.warn("There is profile " + name + " is loaded for headset " + headset_id)
            elif loaded_by_this_app == True:
                emit('load_unload_profile_done', isLoaded=True)
            else:
                setup_profile(profile_name, 'unload')
                # warnings.warn("The profile " + name + " is loaded by other applications")
    elif req_id == DISCONNECT_HEADSET_ID:
        print("Disconnect headset " + headset_id)
        headset_id = ''
    elif req_id == MENTAL_COMMAND_ACTIVE_ACTION_ID:
        emit('get_mc_active_action_done', data=result_dic)
    elif req_id == MENTAL_COMMAND_TRAINING_THRESHOLD:
        emit('mc_training_threshold_done', data=result_dic)
    elif req_id == MENTAL_COMMAND_BRAIN_MAP_ID:
        emit('mc_brainmap_done', data=result_dic)
    elif req_id == SENSITIVITY_REQUEST_ID:
        emit('mc_action_sensitivity_done', data=result_dic)
    elif req_id == CREATE_RECORD_REQUEST_ID:
        record_id = result_dic['record']['uuid']
        emit('create_record_done', data=result_dic['record'])
    elif req_id == STOP_RECORD_REQUEST_ID:
        emit('stop_record_done', data=result_dic['record'])
    elif req_id == EXPORT_RECORD_ID:
        # handle data lable
        success_export = []
        for record in result_dic['success']:
            record_id = record['recordId']
            success_export.append(record_id)

        for record in result_dic['failure']:
            record_id = record['recordId']
            failure_msg = record['message']
            print('export_record resp failure cases: '+ record_id + ":" + failure_msg)

        emit('export_record_done', data=success_export)
    elif req_id == INJECT_MARKER_REQUEST_ID:
        emit('inject_marker_done', data=result_dic['marker'])
    elif req_id == INJECT_MARKER_REQUEST_ID:
        emit('update_marker_done', data=result_dic['marker'])
    else:
        print('No handling for response of request ' + str(req_id))

def handle_error(recv_dic):
    req_id = recv_dic['id']
    print('handle_error: request Id ' + str(req_id))
    emit('inform_error', error_data=recv_dic['error'])

def handle_warning(warning_dic):

    if debug:
        print(warning_dic)
    warning_code = warning_dic['code']
    warning_msg = warning_dic['message']
    if warning_code == ACCESS_RIGHT_GRANTED:
        # call authorize again
        authorize()
    elif warning_code == HEADSET_CONNECTED:
        # query headset again then create session
        query_headset()
    elif warning_code == CORTEX_AUTO_UNLOAD_PROFILE:
        profile_name = ''
    elif  warning_code == CORTEX_STOP_ALL_STREAMS:
        # print(warning_msg['behavior'])
        session_id = warning_msg['sessionId']
        if session_id == session_id:
            emit('warn_cortex_stop_all_sub', data=session_id)
            session_id = ''

def handle_stream_data(result_dic):
    if result_dic.get('com') != None:
        com_data = {}
        com_data['action'] = result_dic['com'][0]
        com_data['power'] = result_dic['com'][1]
        com_data['time'] = result_dic['time']
        emit('new_com_data', data=com_data)
    elif result_dic.get('fac') != None:
        fe_data = {}
        fe_data['eyeAct'] = result_dic['fac'][0]    #eye action
        fe_data['uAct'] = result_dic['fac'][1]      #upper action
        fe_data['uPow'] = result_dic['fac'][2]      #upper action power
        fe_data['lAct'] = result_dic['fac'][3]      #lower action
        fe_data['lPow'] = result_dic['fac'][4]      #lower action power
        fe_data['time'] = result_dic['time']
        emit('new_fe_data', data=fe_data)
    elif result_dic.get('eeg') != None:
        eeg_data = {}
        eeg_data['eeg'] = result_dic['eeg']
        eeg_data['eeg'].pop() # remove markers
        eeg_data['time'] = result_dic['time']
        emit('new_eeg_data', data=eeg_data)
    elif result_dic.get('mot') != None:
        mot_data = {}
        mot_data['mot'] = result_dic['mot']
        mot_data['time'] = result_dic['time']
        emit('new_mot_data', data=mot_data)
    elif result_dic.get('dev') != None:
        dev_data = {}
        dev_data['signal'] = result_dic['dev'][1]
        dev_data['dev'] = result_dic['dev'][2]
        dev_data['batteryPercent'] = result_dic['dev'][3]
        dev_data['time'] = result_dic['time']
        emit('new_dev_data', data=dev_data)
    elif result_dic.get('met') != None:
        met_data = {}
        met_data['met'] = result_dic['met']
        met_data['time'] = result_dic['time']
        emit('new_met_data', data=met_data)
    elif result_dic.get('pow') != None:
        pow_data = {}
        pow_data['pow'] = result_dic['pow']
        pow_data['time'] = result_dic['time']
        emit('new_pow_data', data=pow_data)
    elif result_dic.get('sys') != None:
        sys_data = result_dic['sys']
        emit('new_sys_data', data=sys_data)
    else :
        print(result_dic)
from octorest import OctoRest
from time import sleep
try:
    client = OctoRest(url="http://192.168.40.30", apikey="868940A42CF54D4CB2969F27B8CB4B73")
    status={
        'state':'',                                    # Adding newline for writing in file
        'hotend':'',
        'heatbed':'',
        'progress':'',
        'print_time':'',
        'time_left':'',
    }
    while 1:
        sleep(1)
        status['state'] = client.job_info()['state'].split()[1]     # Getting current state

        with open('/opt/octoprint-api/status_file.txt', 'w') as status_file:
            for string in keys(status):
                status_file.write(status[string],'\n')

        if state in ['Offline', 'Connecting', 'Error']: 
            continue        # If printer can provide temperatures

        temperature=client.printer()['temperature']             # get temperatures
        hotend=int(temperature['tool0']['actual'])
        hotend_target=int(temperature['tool0']['target'])
        heatbed=int(temperature['bed']['actual'])
        heatbed_target=int(temperature['bed']['target'])

        hotend_tmp='{}/{}°C'.format(hotend, hotend_target)      # 100/190°C
        heatbed_tmp='{}/{}°C'.format(heatbed, heatbed_target)

        hotend_str='Hotend:{:>{padding}}\n'.format(hotend_tmp, padding=16-len('Hotend:'))     # Filing strings with spaces so that
        heatbed_str='Heatbed:{:>{padding}}\n'.format(heatbed_tmp, padding=16-len('Heatbed:')) # they have exactly 16 characters

        if state == 'Operational':
            continue                              # If currently printing

        progress = client.job_info()['progress']
        percent=int(progress['completion'])                 # get percentage of completion
        percent_tmp = str(percent) + '%'
        progress_str = 'Progress:{:>{padding}}\n'.format(percent_tmp, padding=16-len('Progress:'))

        print_time = progress['printTime']                  # Get elapsed time in seconds 
        time_left = progress['printTimeLeft']               # Get remaining time in seconds
        if print_time != None:
            print_time_hours = int(print_time/60)//60
            print_time_minutes = int(print_time/60)%60
            print_time_tmp = '{}:{:0>2}'.format(print_time_hours, print_time_minutes)     # Add a zero to minutes if it is one digit, so it's 0:01, not 0:1
            print_time_str = 'Print time:{:>{padding}}\n'.format(print_time_tmp, padding=16-len('Print time:'))
        if time_left != None:                               # If there is a remaining time estimate
            time_left_hours = int(time_left/60)//60
            time_left_minutes = int(time_left/60)%60
            time_left_tmp = '{}:{:0>2}'.format(time_left_hours,time_left_minutes)
            if time_left_hours <= 100:
                time_left_str = 'Time left:{:>{padding}}\n'.format(time_left_tmp, padding=16-len('Time left:'))


except Exception as e:                                            # If can't connect to octoprint
    print(e)
    status_file = open('/opt/octoprint-api/status_file.txt', 'w')
    status_file.write('Lost connection')
    status_file.close()

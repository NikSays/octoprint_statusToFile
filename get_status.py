from octorest import OctoRest
from time import sleep
from dotenv import load_dotenv

load_dotenv()

client = OctoRest(url="http://192.168.40.30", apikey="868940A42CF54D4CB2969F27B8CB4B73")
def format_time(seconds):
    total_minutes = seconds//60
    hours = total_minutes//60
    minutes = total_minutes%60
    return f"{hours}:{minutes:0>2}"

str_len = 18
def generate_string(name, value):
    padding = str_len - len(name) - 1
    return f"{name}:{value:>{padding}}"

def write(data):
    with open('/opt/octoprint-api/status_file.txt', 'w') as status_file:
        for string in data.keys():
            status_file.write(data[string])
            status_file.write('\n')


while 1:
    out_status={
        'state':'',                                    # Adding newline for writing in file
        'hotend':'',
        'heatbed':'',
        'progress':'',
        'print_time':'',
        'time_left':'',
    }
    sleep(1)
    raw_status = client.job_info()
    raw_status['temperature'] = client.printer()['temperature']
    
    state_value = raw_status['state'].split()[0]
    out_status['state'] = generate_string('State', state_value)

    if out_status['state'] in ['Offline', 'Connecting', 'Error']: 
        write(out_status)
        continue        # If printer can provide temperatures
    
    raw_hotend = raw_status['temperature']['tool0']
    raw_heatbed = raw_status['temperature']['bed']

    hotend_value = f"{int(raw_hotend['actual'])}/{int(raw_hotend['target'])}°C"
    out_status['hotend'] = generate_string('Hotend', hotend_value)
    
    heatbed_value = f"{int(raw_heatbed['actual'])}/{int(raw_heatbed['target'])}°C"
    out_status['heatbed'] = generate_string('Heatbed', heatbed_value)

    if state_value == 'Operational':
        write(out_status)
        continue
   
    progress_value = f"{int(raw_status['progress']['completion'])}%"
    out_status['progress'] = generate_string('Progress', progress_value)
    
    print_time = raw_status['progress']['printTime']
    if print_time != None:
        out_status['print_time'] = generate_string('Print time', format_time(print_time))
                
    
    time_left = raw_status['progress']['printTimeLeft']
    if time_left != None:
        out_status['time_left'] = generate_string('Time left', format_time(time_left))
    write(out_status)

import re

def get_screenshot_file_name(scenario_name, step_name):
    instance_id = re.search(r'InstanceId=([\d]+)', scenario_name).group(1)
    print(instance_id)
    base_file_name = '-'.join(step_name.split(' ')) + '.png'
    if re.search(r'@([\d]+).([\d]+)', scenario_name):
        scenario_outline_index = int(re.search(r'@([\d]+).([\d]+)', scenario_name).group(2)) - 1
        file_name = 'reports/' + instance_id + '_' + str(scenario_outline_index) + '_' + base_file_name
    else:
        file_name = 'reports/' + instance_id + '_' + base_file_name

    return file_name

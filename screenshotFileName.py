import re
from os import listdir


def get_screenshot_new_file_name(scenario_name, step_name):
    instance_id = re.search(r'InstanceId=([\d]+)', scenario_name).group(1)
    print(instance_id)
    base_file_name = '-'.join(step_name.split(' '))
    if re.search(r'@([\d]+).([\d]+)', scenario_name):
        # scenario name = 'scenario name.InstanceId=99999 --@1.1' ==> file_name = 99999_0_step name_[1,2,3,...].png
        # scenario name = 'scenario name.InstanceId=99999 --@1.2' ==> file_name = 99999_1_step name_[1,2,3,...].png
        scenario_outline_index = int(re.search(r'@([\d]+).([\d]+)', scenario_name).group(2)) - 1
        file_name_no_intra_step_counter = instance_id + '_' + str(scenario_outline_index) + '_' + base_file_name
    else:
        # scenario name = 'scenario name.InstanceId=99999' ==> file_name = 99999_step name_[1,2,3,...].png
        file_name_no_intra_step_counter = instance_id + '_' + base_file_name

    reports = listdir('reports')
    intra_step_screenshots_list = list(filter(
        lambda screenshot: re.search(file_name_no_intra_step_counter + '_([\d]+).png', screenshot), reports
    ))

    if intra_step_screenshots_list:
        intra_step_counter_list = list(map(
            lambda screenshot: int(re.search(r'.+_([\d]+).png', screenshot).group(1)),
            intra_step_screenshots_list
        ))
    else:
        intra_step_counter_list = [0]

    return 'reports/' + file_name_no_intra_step_counter + '_' + str(max(intra_step_counter_list) + 1) + '.png'

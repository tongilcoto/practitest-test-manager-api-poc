import copy
import os
import argparse
import json
import re
import base64
import requests
from jsonpath_ng.ext import parse
from practitest_urls import *
from screenshotFileName import get_screenshot_file_name

status_mapping = {'passed': 'PASSED', 'failed': 'FAILED', 'skipped': 'NO RUN'}


def get_custom_fields(project_id):
    """

    :param project_id:
    :return:
    """
    url = BASE_URL + CUSTOM_FIELDS_PATH.format(projectId=project_id)
    print(url)
    response = requests.get(url,
                            headers={
                                'content-type': 'application/json',
                                'PTToken': os.environ['TOKEN_practitest']
                            }
                            )
    print(response)
    print(response.json())

    return response.json()


def check_screenshots(instance_id, scenario_name, step):
    file_name = get_screenshot_file_name(scenario_name, step['name'])

    screenshot = open(file_name, "rb")

    file_data = {
        'content_encoded': base64.b64encode(screenshot.read()).decode('utf-8'),
        'filename': file_name.split('/')[1]
    }
    if step.get('files'):
        step['files']['data'].append(file_data)
    else:
        step['files'] = {'data': [file_data]}


def create_practiTest_run(custom_fields, reportDict):
    """

    :param custom_fields:
    :param reportDict:
    :return:
    """

    practitest_run = {
        "data": []
    }

    # for each feature
    for feature in reportDict:

        instance_id = re.search(r'InstanceId=([\d]+)', feature['elements'][0]['name']).group(1)

        instance_run = {
            "type": "instances",
            "attributes": {
                "instance-id": instance_id,
                "custom-fields": {}
            },
            "steps": {
                "data": []
            }
        }

        # open file via location (take care of trailing ':<line number>')
        feature_file = open(re.search(r'(.+):', feature['location']).group(1))
        feature_definition = feature_file.readlines()
        feature_file.close()

        # for each element (scenario: 1 element, scenario outlines: several elements
        for scenario in feature['elements']:

            # for each step
            data = []
            instance_run['attributes']['custom-fields'] = {}
            instance_run['attributes']['exit-code'] = 0
            scenario_duration = 0
            for step in scenario['steps']:

                # add step.name to ptreport (it has the instantiated values)
                # add mapping(step.result.status) to ptreport
                # add step duration to scenario duration
                step_data = {
                    'name': step['keyword'] + ' ' + step['name']
                }
                if step.get('result'):
                    step_data['status'] = status_mapping[step['result']['status']]
                    scenario_duration += step['result']['duration']
                    if step['result'].get('error_message'):
                        instance_run['attributes']['exit-code'] = 1
                        step_data['actual-results'] = '\n'.join(step['result']['error_message'])
                        instance_run['attributes']['automated-execution-output'] = '\n'.join(
                            step['result']['error_message'])[-255:]
                        check_screenshots(instance_id, scenario['name'], step_data)
                else:
                    step_data['status'] = 'NO RUN'

                # Looking for step parameters and filling custom field accordingly: for each match.arguments
                # Steps after a failed step got not match key
                if step.get('match'):
                    for argument in step['match']['arguments']:

                        # if not fixed value
                        # (by checking argument.name against report via step.location using trailing ':<line number>')
                        step_definition = feature_definition[int((re.search(r':(.+)', step['location']).group(1))) - 1]
                        if re.search('"<' + argument["name"] + '>"', step_definition):
                            # get custom_field id by using argument.name
                            field_id = [match.value for match in
                                        parse("$.data[?(@.attributes.name=='" + argument['name'] + "')].id").find(
                                            custom_fields)][0]
                            # add custom_field to ptreport
                            field_id_name = '---f-' + str(field_id)
                            instance_run['attributes']['custom-fields'][field_id_name] = argument['value']

                data.append(copy.deepcopy(step_data))

            # adding test duration as steps duration sum
            instance_run['attributes']['run-duration'] = scenario_duration

            # add steps data to instance
            instance_run['steps']['data'] = copy.deepcopy(data)

            # add run for the scenario to Practi Test report
            practitest_run['data'].append(copy.deepcopy(instance_run))

    print(practitest_run)

    return practitest_run


def get_request_instances(practitest_run):
    # Array of three arrays
    # Each element contains a create-run request
    # first array contains instances ids,
    # second array contains scenario outline index for that instance_id
    # third array contains exit-code for the scenario.
    # If any scenario outline is failed, should be at the final element/s
    # Use cases
    # a. current scenario is failed
    #   1. list is empty   -> failed
    #   i. list got 1 element
    #       2. list element is passed -> passed | failed(new)
    #       3. list element is failed -> failed | failed(new)
    #   ii. list got 2 elements
    #       4. list elements is passed | passed -> passed | passed | failed(new)
    #       5. list elements is passed | failed -> passed | failed | failed(new)
    #       6. list elements is failed | failed -> failed | failed | failed(new)
    # b. current scenario is passed
    #   7. list is empty   -> passed(new)
    #   i. list got 1 element
    #       8. list element is passed -> passed | passed(new)
    #       9. list element is failed -> passed(new) | failed
    #   ii. list got 2 elements
    #       10. list elements is passed | passed -> passed | passed | passed(new)
    #       11. list elements is passed | failed -> passed | passed(new) | failed
    #       12. list elements is failed | failed -> passed(new) | failed | failed
    requests_instances = []

    for i, instance in enumerate([match.value for match in parse("$..instance-id").find(practitest_run)]):
        j = 0

        if practitest_run['data'][i]['attributes']['exit-code'] == 1:  # Scenario Failed
            # Failed scenarios are added at the first run without the instance
            while j < len(requests_instances) and instance in requests_instances[j][0]:
                j += 1

            if j < len(requests_instances):
                requests_instances[j][0].append(instance)
                requests_instances[j][1].append(i)
                requests_instances[j][2].append(1)
            else:
                requests_instances.append([[instance], [i], [1]])
        else:  # Scenario Passed
            # Passed scenarios are inserted just before first failed one
            # And then all failed ones are shifted one position
            top_index = len(requests_instances) - 1
            # get the last run for the passed instance
            while j < len(requests_instances) \
                    and instance in requests_instances[j][0] \
                    and requests_instances[j][2][requests_instances[j][0].index(instance)] == 0:
                j += 1
            # [[a, b][0, 2][0, 2], [a][1][1]]
            if j == len(requests_instances):  # No Failed scenario for the instance. Just to add this passed one
                requests_instances.append([[instance], [i], [0]])
            else:
                k = j
                # get the last run for the instance
                while k < len(requests_instances) \
                        and instance in requests_instances[k][0] \
                        and requests_instances[k][2][requests_instances[k][0].index(instance)] == 1:
                    k += 1
                if k == len(requests_instances):  # last run where the instance is present, is also the last created one
                    requests_instances.append(
                        [
                            [instance],
                            [requests_instances[top_index][1][requests_instances[top_index][0].index(instance)]],
                            [requests_instances[top_index][2][requests_instances[top_index][0].index(instance)]]
                        ]
                    )
                else:  # fill the next run with the instance last data
                    requests_instances[k][0].append(instance)
                    if k == 0:  # First scenario for the instance (and it is passed)
                        requests_instances[k][1].append(i)
                        requests_instances[k][2].append(0)
                    else:
                        requests_instances[k][1].append(requests_instances[k - 1][1][requests_instances[k - 1][0]
                                                        .index(instance)])
                        requests_instances[k][2].append(1)
                # fill other runs with its previous instance run data
                for l in range(k - 1, j, -1):
                    previous_index = requests_instances[l - 1][0].index(instance)
                    index = requests_instances[l][0].index(instance)
                    requests_instances[l][1][index] = requests_instances[l - 1][1][previous_index]
                # change first failed instance with the current passed instance
                index = requests_instances[j][0].index(instance)
                requests_instances[j][1][index] = i
                requests_instances[j][2][index] = 0

    return requests_instances


def upload_run(project_id, practitest_run):
    """

    :param project_id:
    :param practitest_run:
    :return:
    """
    url = BASE_URL + RUNS_PATH.format(projectId=project_id)
    print(url)
    response = requests.post(url,
                             json=practitest_run,
                             headers={
                                 'content-type': 'application/json',
                                 'PTToken': os.environ['TOKEN_practitest']
                             }
                             )
    print(response)
    print(response.json())


def upload_run_with_several_requests(project_id, practitest_run):
    """

    :param project_id:
    :param practitest_run:
    :return:
    """

    requests_instances = get_request_instances(practitest_run)

    for request_index in requests_instances:
        data = []
        batch = 0
        for i in request_index[1]:
            data.append(practitest_run['data'][i])
            batch += 1
            if batch == 20:
                data = []
                batch = 0
                request_body = {'data': data}
                upload_run(project_id, request_body)
        request_body = {'data': data}
        upload_run(project_id, request_body)


def main():
    parser = argparse.ArgumentParser(description='Upload JSON report to PractiTest')
    parser.add_argument('-p', '--project_id', required=True, type=int,
                        help='Project Id at PractiTest')
    parser.add_argument('-r', '--report', required=True, type=open,
                        help='JSON Behave report file')

    args = parser.parse_args()

    # get custom_fields
    custom_fields = get_custom_fields(args.project_id)

    # load json report as python dict
    reportDict = json.load(args.report)

    practitest_run = create_practiTest_run(custom_fields, reportDict)

    # Since API does nota allow the same instance twice in the body, even if they have different custom field value
    # ... this method is not valid
    # upload_run(args.project_id, practitest_run)
    # a method with several requests, each request containing just one custom field value per instance must be executed
    upload_run_with_several_requests(args.project_id, practitest_run)


if __name__ == "__main__":
    main()

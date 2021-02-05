import copy
import os
import argparse
import json
import re
import requests
from jsonpath_ng.ext import parse

status_mapping = {'passed': 'PASSED', 'failed': 'FAILED', 'skipped': 'NO RUN'}

def get_custom_fields(project_id):
    """

    :param project_id:
    :return:
    """
    url = os.environ['BASEURL_practitest'] + os.environ['CUSTOMFIELDSPATH_practitest'].format(projectId=project_id)
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


def upload_run(project_id, practitest_run):
    """

    :param project_id:
    :param practitest_run:
    :return:
    """
    url = os.environ['BASEURL_practitest'] + os.environ['RUNSPATH_practitest'].format(projectId=project_id)
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

    requests_instances = []
    for i, instance in enumerate([match.value for match in parse("$..instance-id").find(practitest_run)]):
        j = 0
        while (j < len(requests_instances) and instance in requests_instances[j][0]):
                j += 1

        if j < len(requests_instances):
            requests_instances[j][0].append(instance)
            requests_instances[j][1].append(i)
        else:
            requests_instances.append([[instance], [i]])

    for request_index in requests_instances:
        data = []
        for i in request_index[1]:
            data.append(practitest_run['data'][i])
        request_body = {'data': data}
        upload_run(project_id, request_body)


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
            for step in scenario['steps']:

                # add step.name to ptreport (it has the instantiated values)
                # add mapping(step.result.status) to ptreport
                step_data = {
                    'name': step['name'],
                    'status': status_mapping[step['result']['status']]
                }

                # for each match.arguments
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

            # add steps data to instance
            instance_run['steps']['data'] = copy.deepcopy(data)

            # add run for the scenario to Practi Test report
            practitest_run['data'].append(copy.deepcopy(instance_run))

    print(practitest_run)

    return practitest_run


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

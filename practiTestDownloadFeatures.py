import os
import copy
import argparse
import requests
from jsonpath_ng.ext import parse
from practitest_urls import *


def get_instances_ids_of_suite(project_id, test_set_id, max_page_elements):
    """

    :param project_id:
    :param test_set_id:
    :param max_page_elements:
    :return:
    """
    # curl -H "Content-Type: application/json" -H "PTToken: $TOKEN" https://api.practitest.com/api/v2/projects/18098/tests.json
    url = BASE_URL + INSTANCES_PATH.format(projectId=project_id, testSetId=test_set_id) + \
          '&page%5Bsize%5D=' + str(max_page_elements)

    instances = {'data': []}
    response = {}
    page = 1
    while instances['data'] == [] or response.json()['meta']['total-pages'] > response.json()['meta']['current-page']:
        paged_url = url + '&page%5Bnumber%5D=' + str(page)
        print(paged_url)
        response = requests.get(paged_url,
                                headers={
                                    'accept': 'application/json',
                                    'PTToken': os.environ['TOKEN_practitest']
                                })
        print(response)
        print(response.json())
        instances['data'] += copy.deepcopy(response.json()['data'])
        page = response.json()['meta']['next-page']

    return instances


def get_steps(project_id, test_ids):
    """

    :param project_id:
    :param test_ids:
    :return:
    """
    test_ids_list = ','.join(map(str, test_ids))
    url = BASE_URL + STEPS_PATH.format(projectId=project_id, testIds=test_ids_list)
    print(url)
    response = requests.get(url, headers={
        'accept': 'application/json',
        'PTToken': os.environ['TOKEN_practitest']
    })
    print(response)
    print(response.json())

    return list(map(lambda test_id: ['\t' + match.value.replace('{{', '<').replace('}}', '>') + '\n'
                                     for match in
                                     parse('$.data[?(@.attributes.test-id==' + test_id + ')].attributes.name').find(
                                         response.json())],
                    test_ids))


def write_feature_files(features_name, features_description, steps, examples, instances_ids):
    """

    :param features_name:
    :param features_description:
    :param steps:
    :param examples:
    :param instances_ids:
    :return:
    """
    for i, feature in enumerate(features_name):
        feature_info = [features_description[i] + '. InstanceId=' + instances_ids[i] + '\n'] + steps[i]
        if examples:
            feature_info += ['\nExamples:\n'] + [examples[i]]
        print('----- Feature File: -----')
        print(feature_info)
        print('----- -----')
        file1 = open('features/' + feature + '.feature', "w")
        file1.writelines(feature_info)
        file1.close()


def create_feature_files(projectId, instances_ids, test_display_ids):
    """

    :param projectId:
    :param instances_ids:
    :param test_display_ids:
    :return:
    """
    test_display_ids_list = ','.join(map(str, test_display_ids))
    url = BASE_URL + TESTS_PATH.format(projectId=projectId, testDisplayIds=test_display_ids_list)
    print(url)
    response = requests.get(url,
                            headers={
                                'accept': 'application/json',
                                'PTToken': os.environ['TOKEN_practitest']
                            })
    print(response)
    print(response.json())

    features_name = [match.value for match in parse("$..name").find(response.json())]
    features_description = [match.value for match in parse("$..description").find(response.json())]
    all_custom_fields = [match.value for match in parse("$..custom-fields").find(response.json())]
    examples = list(map(lambda x: x.get(os.environ['EXAMPLESCUSTOMFIELD_practitest']), all_custom_fields))
    test_ids = [match.value for match in parse('$..id').find(response.json())]
    steps = get_steps(projectId, test_ids)

    write_feature_files(features_name, features_description, steps, examples, instances_ids)


def main():
    parser = argparse.ArgumentParser(description='Download feature files from PractiTest')
    parser.add_argument('-p', '--project_id', required=True, type=int,
                        help='Project Id at PractiTest')
    parser.add_argument('-s', '--test_set_id', required=True, type=int,
                        help='Test Set Id at PractiTest')
    parser.add_argument('-m', '--max_page_elements', type=int, default=100,
                        help='Maximum number of elements by page')

    args = parser.parse_args()

    suite_instances = get_instances_ids_of_suite(args.project_id, args.test_set_id, args.max_page_elements)

    instances_ids = [match.value for match in parse('$.data[*].id').find(suite_instances)]
    print(instances_ids)
    test_display_ids = [match.value for match in parse('$..test-display-id').find(suite_instances)]
    print(test_display_ids)

    create_feature_files(args.project_id, instances_ids, test_display_ids)


if __name__ == "__main__":
    main()

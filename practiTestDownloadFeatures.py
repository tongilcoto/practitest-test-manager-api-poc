import os
import argparse
import requests
from jsonpath_ng.ext import parse


def get_instances_ids_of_suite(projectId, testSetId):
    """

    :param projectId:
    :param testSetId:
    :return:
    """
    # curl -H "Content-Type: application/json" -H "PTToken: $TOKEN" https://api.practitest.com/api/v2/projects/18098/tests.json
    url = os.environ['BASEURL_practitest'] + os.environ['INSTANCESPATH_practitest'].format(projectId=projectId,
                                                                                           testSetId=testSetId)
    print(url)
    response = requests.get(url,
                            headers={
                                'accept': 'application/json',
                                'PTToken': os.environ['TOKEN_practitest']
                            })

    print(response)
    print(response.json())

    return response.json()


def get_feature_definition(projectId, testId):
    """

    :param projectId:
    :param testId:
    :return:
    """
    url = os.environ['BASEURL_practitest'] + os.environ['TESTPATH_practitest'].format(projectId=projectId,
                                                                                      testId=testId)
    print(url)
    response = requests.get(url,
                            headers={
                                'accept': 'application/json',
                                'PTToken': os.environ['TOKEN_practitest']
                            })
    print(response)
    print(response.json())
    attributes = response.json()['data']['attributes']
    examples = attributes['custom-fields'].get(os.environ['EXAMPLESCUSTOMFIELD_practitest'], '')
    return attributes['name'], \
           attributes['description'], \
           examples


def get_steps(project_id, test_ids):
    """

    :param project_id:
    :param test_ids:
    :return:
    """
    test_ids_list = ','.join(map(str, test_ids))
    url = os.environ['BASEURL_practitest'] + os.environ['STEPSPATH_practitest'].format(projectId=project_id,
                                                                                       testIds=test_ids_list)
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
    url = os.environ['BASEURL_practitest'] + os.environ['TESTSPATH_practitest']. \
        format(projectId=projectId,
               testDisplayIds=test_display_ids_list)
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

    args = parser.parse_args()

    suite_instances = get_instances_ids_of_suite(args.project_id, args.test_set_id)

    instances_ids = [match.value for match in parse('$.data[*].id').find(suite_instances)]
    print(instances_ids)
    test_display_ids = [match.value for match in parse('$..test-display-id').find(suite_instances)]
    print(test_display_ids)

    create_feature_files(args.project_id, instances_ids, test_display_ids)


if __name__ == "__main__":
    main()

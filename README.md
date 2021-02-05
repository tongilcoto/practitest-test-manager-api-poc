# PYTHON PIPELINE with BEHAVE BDD framework
## Downloads info from Practi Test and creates feature files from scratch
## Executes, with a JSON report as output, a few tests on GoRest Public API https://gorest.co.in
## Parses the report and creates new "runs" for instances (test cases) at Practi Test

## Pre-requisites

1. Python version 3 and pip
2. pipenv (pip install pipenv)

## Deployment

1. pipenv install --ignore-pipfile
2. pipenv shell

## Execution

1. export BASEURL_practitest=https://api.practitest.com
2. export TESTSPATH_practitest=/api/v2/projects/{projectId}/tests.json?display-ids={testDisplayIds}
3. export STEPSPATH_practitest=/api/v2/projects/{projectId}/steps.json?test-ids={testIds}
4. export INSTANCESPATH_practitest=/api/v2/projects/{projectId}/instances.json?set-ids={testSetId}
5. export TOKEN_practitest=<your token>
6. export EXAMPLESCUSTOMFIELD_practitest=<the field name is made with '---f-' + id field>
7. export RUNSPATH_practitest=/api/v2/projects/{projectId}/runs.json
8. python3 practiTestDownloadFeatures.py -h
9. python3 practiTestDownloadFeatures.py -p --project_id <project_id> -s --test_set_id <testSuiteId>
10. behave --json -o reports/report.json
11. python3 practiTestUploadRun.py -h
12. python3 practiTestUploadRun.py -p --projec_id <project_id> -r --report <path_to_json_report_file>

## Exiting virtual env

1. exit

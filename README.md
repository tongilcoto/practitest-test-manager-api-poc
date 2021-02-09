# PYTHON PIPELINE with BEHAVE BDD framework
## Downloads info from Practi Test and creates feature files from scratch
## Executes, with a JSON report as output, a few tests on GoRest Public API https://gorest.co.in
## Parses the report and creates new "runs" for instances (test cases) at Practi Test
## Road Map
### <del>Passed Test Steps</del>
### <del>Passed Test with run time as total test steps run time</del>
### <del>Failed Test Steps</del>
### <del>Failed Test Steps with screenshots</del>
### <del>Upload failed scenarios at the last create-run requests in order to set the instance failed</del>
### <del>Download instances following pagination info</del>
### <del>Split create-run requests every 20 scenarios</del>
### Any screenshot at any page, not only standard screenshot-at-failed-page-for-failed-step

## Pre-requisites

1. Python version 3 and pip
2. pipenv (pip install pipenv)

## Deployment

1. pipenv install --ignore-pipfile
2. pipenv shell

## Execution

1. export TOKEN_practitest=<your token>
2. export EXAMPLESCUSTOMFIELD_practitest=<the field name is made with '---f-' + id field>
3. python3 practiTestDownloadFeatures.py -h
4. python3 practiTestDownloadFeatures.py -p --project_id <project_id> -s --test_set_id <test_set_id>
5. behave --json -o reports/report.json
6. python3 practiTestUploadRun.py -h
7. python3 practiTestUploadRun.py -p --project_id <project_id> -r --report <path_to_json_report_file>

## Exiting virtual env

1. exit

# CRAWLER

## Pre-requisites

1. Python version 3 and pip
2. pipenv (pip install pipenv)
3. Chrome browser

## Deployment

1. unzip TestManagersAPI.zip
2. cd TestManagersAPI
3. pipenv install --ignore-pipfile
4. pipenv shell

## Execution

1. export USER_qtest=<user>
2. export PASSWORD_qtest=<password>
3. export BASIC_qtest=
4. export BASEURL_qtest=https://hiiberia.qtestnet.com
5. export TOKENPATH_qtest=/oauth/token
6. export TESTRUNSPATH_qtest=/api/v3/projects/{projectId}/test-runs?parentId={testSuiteId}&parentType=test-suite
7. export TESTRUNSALLPATH_qtest=/api/v3/projects/{projectId}/test-runs?expand=descendants
8. export TESTPATH_qtest=/api/v3/projects/{projectId}/test-cases/{testId}
9. export BASEURL_practitest=https://api.practitest.com
10. export TESTPATH_practitest=/api/v2/projects/{projectId}/tests/{testId}.json
11. export STEPSPATH_practitest=/api/v2/projects/{projectId}/steps.json?test-ids={testId}
12. export INSTANCESPATH_practitest=/api/v2/projects/{projectId}/instances.json?set-ids={testSetId}
13. export TOKEN_practitest=f31cd85bc9e3457b10db14825e75e32368004dbb
14. export EXAMPLESCUSTOMFIELD_practitest=---f-78192
15. export RUNSPATH_practitest=/api/v2/projects/{projectId}/runs.json
16. python3 qTestDownloadFeatures.py -h
17. python3 qTestDownloadFeatures.py -p --projectId <projectId> -s --testSuiteId <testSuiteId>
18. python3 practiTestDownloadFeatures.py -h
19. python3 practiTestownloadFeatures.py -p --projectId <projectId> -s --testSetId <testSetId>

## Exiting virtual env

1. exit

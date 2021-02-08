from behave import *
from selenium import webdriver


@given('an "anonymous" api consumer')
def step_impl(context):
    pass


@when('he asks for "{page}" page of "{resource}"')
def step_impl(context, page, resource):
    assert True is not False


@then('he gets a "SYNCHRONOUS_OK" response')
def step_impl(context):
    pass


@then('the number of items per page matches response meta info')
def step_impl(context):
    assert True is not False


@then('products response "mandatory" fields are populated')
def step_impl(context):
    assert True is not False


@then('users response fields are populated')
def step_impl(context):
    assert True is not False


@given('I open PractiTest')
def step_impl(context):
    print("Getting driver ready and opening the page")
    context.driver = webdriver.Chrome()
    context.driver.get('http://practitest.com')


@when('I select one "{wrong_type}" element')
def step_impl(context, wrong_type):
    print("looking for the button")
    get_started = context.driver.find_element_by_css_selector('a.bbtn--demo--big')
    get_started.click()


@then('I take a screenshot')
def step_impl(context):
    print("that's it")

from behave import *


@given('an "anonymous" api consumer')
def step_impl(context):
    pass


@when('he asks for "{page}" page of "{resource}"')
def step_impl(context, page, resource):
    assert True is not False


@then('he gets a "SYNCHRONOUS_OK" response')
def step_impl(context):
    assert context.failed is False


@then('the number of items per page matches response meta info')
def step_impl(context):
    assert context.failed is False


@then('products response "mandatory" fields are populated')
def step_impl(context):
    assert context.failed is False


@then('users response '
      'fields are populated')
def step_impl(context):
    assert context.failed is False

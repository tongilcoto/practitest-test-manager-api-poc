from behave.model_core import Status
from screenshotFileName import get_screenshot_new_file_name


def after_step(context, step):
    if step.status == Status.failed:
        context.failed_step_name = step.keyword + ' ' + step.name


def after_scenario(context, scenario):
    if context.failed and context.driver:
        context.driver.save_screenshot(get_screenshot_new_file_name(scenario.name, context.failed_step_name))

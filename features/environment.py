from behave import *
from behave.model_core import Status
from selenium import webdriver
import re
from screenshotFileName import get_screenshot_file_name


def after_step(context, step):
    if step.status == Status.failed:
        context.failed_step_name = step.keyword + ' ' + step.name


def after_scenario(context, scenario):
    if context.failed and context.driver:
        context.driver.save_screenshot(get_screenshot_file_name(scenario.name, context.failed_step_name))

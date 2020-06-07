__author__ = 'Russel'
import httpretty


def pytest_configure(config):
    httpretty.HTTPretty.allow_net_connect = False

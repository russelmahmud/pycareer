from mapping import PARSERS


def get_parser(parser_name):
    return PARSERS.get(parser_name)()
import json
from prance import ResolvingParser


def test_load_spec():
    with open("swagger.json") as stream:
        spec = json.load(stream)
        pass


def test_load_api_spec_with_prance():
    parser = ResolvingParser("swagger.json")
    spec = parser.specification  # contains fully resolved specs as a dict
    pass

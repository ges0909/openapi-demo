import json
import os
from typing import Optional

import jmespath
import pytest
import yaml
from jsonschema import validate, ValidationError
from prance import ResolvingParser


@pytest.mark.parametrize(
    ("path", "method", "status"),
    (
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/wps",
            "get",
            "200",
        ),
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/wps",
            "get",
            "400",
        ),
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/wps",
            "get",
            "404",
        ),
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/wps",
            "get",
            "500",
        ),
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/wps",
            "put",
            "200",
        ),
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/wps",
            "put",
            "400",
        ),
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/wps",
            "put",
            "404",
        ),
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/wps",
            "put",
            "500",
        ),
        # --
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/cpe",
            "get",
            "200",
        ),
        (
            "/resources/tenants/{tenantId}/accounts/{accountNumber}/cpe-ids",
            "get",
            "200",
        ),
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/ip-address/{ipAddress}/active",
            "get",
            "200",
        ),
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/wifi/schedules",
            "get",
            "200",
        ),
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/devices",
            "get",
            "200",
        ),
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/leds",
            "get",
            "200",
        ),
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/network",
            "get",
            "200",
        ),
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/wifi",
            "get",
            "200",
        ),
        (
            "/resources/tenants/{tenantId}/cpes/{cpeId}/management/super-wifi",
            "get",
            "200",
        ),
    ),
)
def test_get_responses_from_api_spec(
    path: str,
    method: str,
    status: str,
    suffix: str = "yml",
):
    # with open("../swagger.json") as stream:
    #     spec = json.load(stream)
    parser = ResolvingParser("../swagger.json")
    spec = parser.specification  # contains fully resolved spec as dict
    schema = jmespath.search(
        expression=f'paths."{path}".{method}.responses."{status}".schema',
        data=spec,
    )
    os.makedirs("../generated", exist_ok=True)
    parts = path.split("/")
    with open(f"../generated/{method}_{status}_{parts[-1]}.{suffix}", "w") as stream:
        if suffix in ("json",):
            stream.write(json.dumps(schema, indent=4, sort_keys=True))
        elif suffix in ("yml", "yaml"):
            yaml.dump(data=schema, stream=stream)


# --


def get_normalized_path_parts(path: str) -> list[str]:
    """splits path and removes empty parts resulting from leading/trailing and multiple slashes"""
    parts = path.split("/")
    return [part for part in parts if part]


def path_matches(spec_path_parts: list[str], path_parts: list[str]) -> bool:
    """checks each path part on equality; parts containing a template are ingnored"""
    for spec_path_part, path_part in zip(spec_path_parts, path_parts):
        is_template = spec_path_part.startswith("{") and spec_path_part.endswith("}")
        if not is_template:
            if spec_path_part != path_part:
                return False
    return True


def find_spec_path(spec_paths: list[str], path: str) -> Optional[str]:
    path_parts = get_normalized_path_parts(path)
    for spec_path in spec_paths:
        spec_path_parts = get_normalized_path_parts(spec_path)
        if len(spec_path_parts) == len(path_parts):
            if path_matches(spec_path_parts=spec_path_parts, path_parts=path_parts):
                return spec_path
    return None


def test_find_matching_spec_path():
    parser = ResolvingParser("../swagger.json")
    spec = parser.specification
    spec_paths = jmespath.search(
        expression="paths | keys(@)",
        data=spec,
    )
    matching_spec_path = find_spec_path(spec_paths=spec_paths, path="/resources/tenants/123/cpes/456/management/wps")
    assert matching_spec_path == "/resources/tenants/{tenantId}/cpes/{cpeId}/management/wps"


# --


def test_schema_validation():
    method = "get"
    status = "200"
    parser = ResolvingParser("../swagger.json")
    spec = parser.specification
    spec_paths = list(spec["paths"].keys()) if "paths" in spec else []
    matching_spec_path = find_spec_path(spec_paths=spec_paths, path="/resources/tenants/123/cpes/456/management/wps")
    path_definition = spec["paths"][matching_spec_path]
    method_definition = path_definition[method] if method in path_definition else {}
    schema = method_definition["responses"][status]["schema"] if status in method_definition["responses"] else {}
    try:
        validate(instance={}, schema=schema)
    except ValidationError as error:
        error = ", ".join([arg for arg in error.args if isinstance(arg, str)])
        pass

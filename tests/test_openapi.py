import json
import os

import jmespath
import pytest
import yaml
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

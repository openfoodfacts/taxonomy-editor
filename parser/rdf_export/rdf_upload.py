"""Uploads a taxonomy to ShowVoc"""

import json
import os
import sys

import requests

from rdf_export.rdf_config import OFF, addTaxonomyNamespace

# --- CONFIGURATION SETTINGS ---
ST_NS = "it.uniroma2.art.semanticturkey"
CONFIG_NS = f"{ST_NS}.extension.impl.repositoryimplconfigurer.predefined"
ST_URL = os.environ.get("ST_URL", "http://localhost:1983/semanticturkey")
API_BASE = f"{ST_URL}/{ST_NS}"
CORE_SERVICES_API_BASE = f"{API_BASE}/st-core-services"

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


def get_authenticated_session():
    """Helper to spin up a completely fresh, isolated connection context session."""
    new_session = requests.Session()
    url = f"{CORE_SERVICES_API_BASE}/Auth/login"
    payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}

    response = new_session.post(url, data=payload)
    if response.status_code == 200 and "result" in response.text:
        return new_session
    return None


def is_response_ok(operation, response_obj):
    """Safely extracts and verifies the doubly-nested 'stresponse -> reply -> status' JSON path."""
    try:
        data = response_obj.json()
        response = data.get("stresponse", data)
        ok = response.get("reply", {}).get("status") == "ok" or data.get("result") or "already in use" in response.get("msg")
        if not ok:
            print(f'{operation}: {response.get("msg", response)}')
        return ok
    except Exception:
        return '"status":"ok"' in response_obj.text or 'status="ok"' in response_obj.text


if __name__ == "__main__":
    # Dataset Settings
    taxonomy_name = sys.argv[1]
    BASE_URI = str(addTaxonomyNamespace(taxonomy_name))

    session = get_authenticated_session()
    res = session.post(
        f"{API_BASE}/st-metadata-registry-services/MetadataRegistry/createDatasetAbstraction",
        data={
            "shortName": taxonomy_name,
            "uriSpace": BASE_URI,
            "title": f'"{taxonomy_name}"@en',
        },
    )
    is_response_ok("Create Dataset:", res)

    res = session.post(
        f"{CORE_SERVICES_API_BASE}/Projects/createProject",
        data={
            "consumer": "SYSTEM",
            "projectName": taxonomy_name,
            "baseURI": BASE_URI,
            "model": "<http://www.w3.org/2004/02/skos/core>",
            "lexicalizationModel": "<http://www.w3.org/2004/02/skos/core>",
            "repositoryAccess": '{"@type":"CreateLocal"}',
            "supportRepoID": "countries_support",
            "coreRepoSailConfigurerSpecification": json.dumps(
                {
                    "factoryId": f"{CONFIG_NS}.RDF4JRepositoryConfigurer",
                    "configType": f"{CONFIG_NS}.RDF4JPersistentInMemorySailConfiguration",
                    "configuration": {
                        "@type": f"{CONFIG_NS}.RDF4JPersistentInMemorySailConfiguration",
                        "syncDelay": 1000,
                        "directTypeInference": False,
                        "inferencer": "none",
                    },
                }
            ),
            "historyEnabled": "false",
            "validationEnabled": "false",
            "mdrRegistration": json.dumps(
                {
                    "datasetAbstraction": f"{ST_URL}/mdr/dataset-{taxonomy_name}-abs",
                    "version": "1.0.0",
                    "currentVersion": True,
                }
            ),
            "openAtStartup": "true",
            # facets
            # {"@type":"it.uniroma2.art.semanticturkey.settings.facets.ProjectFacets"}
            # createMainShard
            # false
            # appCtx
            # SHOWVOC
            # blacklistingEnabled
            # false
        },
    )
    is_response_ok("Create Project", res)

    res = session.post(
        f"{CORE_SERVICES_API_BASE}/Projects/makePublic?ctx_project={taxonomy_name}"
    )
    if is_response_ok("Make Public", res):
        res = session.post(
            f"{CORE_SERVICES_API_BASE}/InputOutput/clearData?ctx_project={taxonomy_name}"
        )
        if is_response_ok("Clear Data", res):
            with open(f"{taxonomy_name}.ttl", "rb") as f:
                res = session.post(
                    f"{CORE_SERVICES_API_BASE}/InputOutput/loadRDF?ctx_project={taxonomy_name}",
                    # /st-core-services/InputOutput/loadRDF?ctx_project=countries&ctx_forceEditable=true&ctx_shard=main
                    data={
                        "baseURI": BASE_URI,
                        "format": "Turtle",
                        "consumer": "SYSTEM",
                        "transitiveImportAllowance": "web",
                        # validateImplicitly
                        # false
                    },
                    files={"inputFile": f},
                )
                # Load service just returns a result object which is empty on success
                res_json = res.json()
                if res_json.get("result", res_json):
                    print(f"Load RDF: result: {res_json}")

            res = session.post(
                f"{API_BASE}/st-core-services/Settings/storeSettingDefault?ctx_project={taxonomy_name}",
                data={
                    "componentID": f"{ST_NS}.settings.core.SemanticTurkeyCoreSettingsManager",
                    "scope": "PROJECT_USER",
                    "defaultScope": "PROJECT",
                    "propertyName": "activeSchemes",
                    "propertyValue": f'["<{str(OFF[taxonomy_name])}>"]',
                },
            )
            is_response_ok("Set active scheme", res)

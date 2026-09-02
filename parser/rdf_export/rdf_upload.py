"""Uploads a taxonomy to ShowVoc"""

import json
import os
import sys

import requests

# --- CONFIGURATION SETTINGS ---
ST_NS = "it.uniroma2.art.semanticturkey"
CONFIG_NS = f"{ST_NS}.extension.impl.repositoryimplconfigurer.predefined"
ST_URL = os.environ.get("ADMIN_EMAIL", "http://localhost:1983/semanticturkey")
API_BASE = f"{ST_URL}/{ST_NS}"
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


def get_authenticated_session():
    """Helper to spin up a completely fresh, isolated connection context session."""
    new_session = requests.Session()
    url = f"{API_BASE}/st-core-services/Auth/login"
    payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}

    response = new_session.post(url, data=payload)
    if response.status_code == 200 and "result" in response.text:
        return new_session
    return None


def is_response_ok(response_obj):
    """Safely extracts and verifies the doubly-nested 'stresponse -> reply -> status' JSON path."""
    try:
        data = response_obj.json()
        ok = data.get("stresponse", {}).get("reply", {}).get("status") == "ok"
        if not ok:
            print(f'Error: {data.get("stresponse", {}).get("msg")}')
        return ok
    except Exception:
        return '"status":"ok"' in response_obj.text or 'status="ok"' in response_obj.text


if __name__ == "__main__":
    # Dataset Settings
    DATASET_NAME = sys.argv[1]
    BASE_URI = f"https://openfoodfacts.org/data/taxonomies/{DATASET_NAME}#"

    session = get_authenticated_session()
    res = session.post(
        f"{API_BASE}/st-metadata-registry-services/MetadataRegistry/createDatasetAbstraction",
        data={
            "shortName": DATASET_NAME,
            "uriSpace": BASE_URI,
            "title": f'"{DATASET_NAME}"@en',
        },
    )
    is_response_ok(res)
    # Ignore already exists error

    res = session.post(
        f"{API_BASE}/st-core-services/Projects/createProject",
        data={
            "consumer": "SYSTEM",
            "projectName": DATASET_NAME,
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
                    "datasetAbstraction": f"{ST_URL}/mdr/dataset-{DATASET_NAME}-abs",
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
    is_response_ok(res)

    res = session.post(
        f"{API_BASE}/st-core-services/Projects/makePublic?ctx_project={DATASET_NAME}"
    )
    is_response_ok(res)

    res = session.post(
        f"{API_BASE}/st-core-services/InputOutput/clearData?ctx_project={DATASET_NAME}"
    )
    is_response_ok(res)

    with open(f"{DATASET_NAME}.ttl", "rb") as f:
        res = session.post(
            f"{API_BASE}/st-core-services/InputOutput/loadRDF?ctx_project={DATASET_NAME}",
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
        is_response_ok(res)

    res = session.post(
        f"{API_BASE}/st-core-services/Settings/storeSettingDefault?ctx_project={DATASET_NAME}",
        data={
            "componentID": f"{ST_NS}.settings.core.SemanticTurkeyCoreSettingsManager",
            "scope": "PROJECT_USER",
            "defaultScope": "PROJECT",
            "propertyName": "activeSchemes",
            "propertyValue": f'["<https://openfoodfacts.org/data/taxonomies/core#{DATASET_NAME}>"]',
        },
    )
    is_response_ok(res)

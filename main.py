import os
import json
import time
import requests
import functions_framework
from flask import jsonify, Request

# change to env variables
DATABRICKS_HOST = 'https://adb-3958142316394698.18.azuredatabricks.net'
DATABRICKS_TOKEN = 'dapi4b32c1635276b087ccbcad250df140b6-2'
WAREHOUSE_ID = 'ee573a2ee0634df8'

# change as parameter
QUERY = '''
SELECT * FROM ai_dbr_eu_west.40_breaks_placement.break_segments
'''

def run_query(query):
    url = f"{DATABRICKS_HOST}/api/2.0/sql/statements/"
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "statement": query,
        "warehouse_id": WAREHOUSE_ID,
        "disposition": "EXTERNAL_LINKS",
        "wait_timeout": "30s"
    }

    # Send query request
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    statement_id = response.json()["statement_id"]
    status_url = f"{DATABRICKS_HOST}/api/2.0/sql/statements/{statement_id}"

    # Poll until query completes
    while True:
        status_resp = requests.get(status_url, headers=headers)
        status_resp.raise_for_status()

        state = status_resp.json()["status"]["state"]
        if state in ["SUCCEEDED", "FAILED", "CANCELED"]:
            break
        time.sleep(2)

    if state != "SUCCEEDED":
        raise Exception(f"Query failed: {status_resp.text}")

    return status_resp.json()["result"]["data_array"]

@functions_framework.http
def read_databricks_table(request: Request):
    try:
        # Run query and get flat list of rows
        data_rows = run_query(QUERY)

        # Expected format for BQ function
        return jsonify({
            "replies": [data_rows]  # One item in replies: the full table
        })
    except Exception as e:
        return jsonify({"errorMessage": str(e)}), 500
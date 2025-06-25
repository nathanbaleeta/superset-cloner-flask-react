
import json
import random
import string
from flask import Flask, request, jsonify

import urllib.parse

from flask_cors import CORS
from api_request_handler import APIRequestHandler
from endpoints import DASHBOARD_ENDPOINT, DATASET_ENDPOINT, CHART_ENDPOINT
import os

SUPERSET_INSTANCE_URL = os.environ['SUPERSET_INSTANCE_URL']
SUPERSET_USERNAME = os.environ['SUPERSET_USERNAME']
SUPERSET_PASSWORD = os.environ['SUPERSET_PASSWORD']

app = Flask(__name__)
CORS(app)
    
@app.route('/api/v1/dashboards', methods=['GET'])
def get_dashboards():
    # Initialize the API request handler with Superset credentials
    request_handler = APIRequestHandler(SUPERSET_INSTANCE_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD)

    dashboard_query_params = {
        "page_size": 100
    }

    # 1. Convert the dictionary to a JSON string
    json_string = json.dumps(dashboard_query_params)

    # 2. URL-encode the JSON string
    encoded_q_param = urllib.parse.quote(json_string)

    final_endpoint_url = f"{DASHBOARD_ENDPOINT}?q={encoded_q_param}"

    # Execute the GET request to the dashboard endpoint
    dashboard_get_response = request_handler.get_request(final_endpoint_url, verify=False)

    # Parse the JSON response and extract the 'result' key which contains dashboard data
    dashboards = json.loads(dashboard_get_response.text)['result']

    # Return the extracted dashboard list as a JSON response
    return jsonify(dashboards)

@app.route('/api/v1/datasets', methods=['GET'])
def get_datasets():
    # Initialize the API request handler with Superset credentials
    request_handler = APIRequestHandler(SUPERSET_INSTANCE_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD)

    dataset_query_params = {
        "page_size": 100
    }

    # 1. Convert the dictionary to a JSON string
    json_string = json.dumps(dataset_query_params)

    # 2. URL-encode the JSON string
    encoded_q_param = urllib.parse.quote(json_string)

    final_endpoint_url = f"{DATASET_ENDPOINT}?q={encoded_q_param}"
    print(final_endpoint_url)

    # Execute the GET request to the dataset endpoint
    dataset_get_response = request_handler.get_request(final_endpoint_url, verify=False)

    # Parse the JSON response and extract the 'result' key which contains dataset data
    datasets = json.loads(dataset_get_response.text)['result'] 

    # Return the extracted dataset list as a JSON response   
    return jsonify(datasets)


@app.route('/api/v1/load_slice_details', methods=['POST'])
def load_slice_details():
    data = request.get_json() # Get JSON data from the request body
    dashboard_id = data.get('dashboard_id')

    request_handler = APIRequestHandler(SUPERSET_INSTANCE_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD)
    chart_definitions_response = request_handler.get_request(f"{DASHBOARD_ENDPOINT}/{dashboard_id}/charts", verify=False)

    data = json.loads(chart_definitions_response.text)['result']
 
    # Create an empty dictionary to store the results
    slice_info = []

    # Iterate through each dictionary in the list
    for item in data:
        slice_id = item['form_data']['slice_id'] 
        slice_name = item['slice_name']
        datasource = extract_table_id(item['form_data']['datasource'])
        
        if slice_id is not None and slice_name is not None:
            slice_info.append({"slice_id": slice_id, \
                            "sourceChart": slice_name, \
                            "destinationChart": "", \
                            "dataset": datasource
            }) 
    get_dashboards()
    return slice_info

def extract_table_id(text):
    #text = "95__table"
    before_separator, separator, after_separator = text.partition('__')
    extracted_number = before_separator
    return extracted_number

@app.route('/api/v1/copy_dashboard', methods=['POST'])
def copy_dashboard():
    data = request.get_json() # Get JSON data from the request body
    dashboard_id = data.get('dashboard_id')
    new_dashboard_title = data.get('new_dashboard_title')

    #if dashboard_id and new_dashboard_title:
    #    print(f"Received data: id: {id}, name: {new_dashboard_title}")
   
    request_handler = APIRequestHandler(SUPERSET_INSTANCE_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD)
    dashboard_details_response = request_handler.get_request(f"{DASHBOARD_ENDPOINT}/{dashboard_id}", verify=False)

    # Single-liner to generate a random string to append to dashboard name to uniquely identify new dashboard
    random_string = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(5))

    # get the dashboard_title, metadata and positions
    dashboard_title = dashboard_details_response.json().get("result", {}).get("dashboard_title")
    dashboard_metadata_json = dashboard_details_response.json().get("result", {}).get("json_metadata")
    dashboard_positions = dashboard_details_response.json().get("result", {}).get("position_json")
    print("\n")

    # Update the metadata with positions - it needs to be a dict
    metadata_dict = json.loads(dashboard_metadata_json)
    metadata_dict["positions"] = json.loads(dashboard_positions)
 
    # Copy the dashboard using the API
    copy_payload = {
        "dashboard_title": new_dashboard_title or f"{dashboard_title} {random_string}",
        "duplicate_slices": True,
        "json_metadata": json.dumps(metadata_dict)
    }

    copy_response = request_handler.post_request(f"{DASHBOARD_ENDPOINT}/{dashboard_id}/copy/", 
                                            verify=False, 
                                            json=copy_payload)
    

    copy_response_output = copy_response.json()

    # sample copy_response_output - {'result': {'id': 1803, 'last_modified_time': 1748530693.0}}

    get_dashboards()
    return copy_response_output

@app.route('/api/v1/update_chart_datasource', methods=['POST'])
def update_chart_datasource():
    data = request.get_json() # Get JSON data from the request body
    print("#" * 50)
    print(data)
    print("#" * 50)

    new_dashboard_id = data.get('newDashboardId')
    old_dataset_id = data.get('oldDatasetId')
    new_dataset_id = data.get('newDatasetId')
    
    return data

@app.route('/api/v1/update_charts', methods=['POST'])
def update_charts():
    DATASET_ID = 141
    data = request.get_json() # Get JSON data from the request body
  

    request_handler = APIRequestHandler(SUPERSET_INSTANCE_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD)
    # {'slice_name': 'Employee Counter List sa', 'datasource_id': 141, 'description': 'Cloned', 'params': '{"datasource": "141__table"}'}       

    chart_data = []
    for item in data:
        if item['destinationChart']:
            slice_id = item['slice_id']

            chart_response = request_handler.get_request(f"{CHART_ENDPOINT}/{slice_id}", verify=False)
            chart_params_json = chart_response.json().get("result", {}).get("params")
    
            # Update the metadata with positions - it needs to be a dict
            params_dict = json.loads(chart_params_json)
            
            """ "params": json.dumps({
                    "viz_type": viz_type_from_params,
                   "datasource": f"{DATASET_ID}__table"
                }), """


            chart_data = {
                "slice_name":  item['destinationChart'], 
                "datasource_id": DATASET_ID,
                "datasource_type": "table",
                "params": json.dumps(params_dict),
                "description": "Updated by script!"
            }
            print("*" * 50)
            print(chart_data)
            print("*" * 50)

            request_handler.put_request(f"{CHART_ENDPOINT}/{slice_id}", verify=False, json=chart_data)

    return data


if __name__ == '__main__':
   app.run(debug=True, port=5000)
   


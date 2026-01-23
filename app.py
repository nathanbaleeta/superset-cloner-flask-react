
import json
import random
import string
from flask import Flask, request, jsonify
import requests

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
    try:
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
        response = request_handler.get_request(final_endpoint_url, verify=False)

        # Check for HTTP errors (4xx or 500xx)
        response.raise_for_status()

        # Safely parse JSON
        data = response.json()

        # Check if result exists in the response
        if 'result' not in data:
            return jsonify({"error": "Unexpected response format from Superset"}), 502
        
        # Parse the JSON response and extract the 'result' key which contains dashboard data
        dashboards = data['result']

        # Return the extracted dashboard list as a JSON response
        return jsonify(dashboards), 200
    
    except requests.exceptions.HTTPError as http_err:
        # Handles specific HTTP errors (e.g., 401 Unauthorized, 404 Not Found)
        return jsonify({"error": f"HTTP error occurred: {http_err}"}), response.status_code
    
    except json.JSONDecodeError:
        # Handles cases where the response is not valid JSON
        return jsonify({"error": "Failed to decode JSON from Superset"}), 502
    
    except Exception as e:
        # Catches any other unexpected issues (connection, logic, etc.)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/api/v1/datasets', methods=['GET'])
def get_datasets():
    try:
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
        response = request_handler.get_request(final_endpoint_url, verify=False)

        # Check for HTTP errors (4xx or 500xx)
        response.raise_for_status()

        # Safely parse JSON
        data = response.json()

        # Check if result exists in the response
        if 'result' not in data:
            return jsonify({"error": "Unexpected response format from Superset"}), 502
        
        # Parse the JSON response and extract the 'result' key which contains dataset data
        datasets = data['result']

        # Return the extracted dataset list as a JSON response
        return jsonify(datasets), 200
    
    except requests.exceptions.HTTPError as http_err:
        # Handles specific HTTP errors (e.g., 401 Unauthorized, 404 Not Found)
        return jsonify({"error": f"HTTP error occurred: {http_err}"}), response.status_code
    
    except json.JSONDecodeError:
        # Handles cases where the response is not valid JSON
        return jsonify({"error": "Failed to decode JSON from Superset"}), 502
    
    except Exception as e:
        # Catches any other unexpected issues (connection, logic, etc.)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

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
    #dashboard_id = data.get('dashboard_id')
    #new_dashboard_title = data.get('new_dashboard_title')

    # Generator expression and tuple unpacking
    keys = ('dashboard_id', 'new_dashboard_title')
    dashboard_id, new_dashboard_title = (data.get(k) for k in keys)

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

    get_dashboards()
    return copy_response_output

@app.route('/api/v1/update_chart_datasource', methods=['POST'])
def update_chart_datasource():
    data = request.get_json() # Get JSON data from the request body

    # Generator expression and tuple unpacking
    keys = (new_dashboard_id, old_dataset_id, new_dataset_id, slice_id)
    new_dashboard_id, old_dataset_id, new_dataset_id, slice_id = (data.get(k) for k in keys)

    request_handler = APIRequestHandler(SUPERSET_INSTANCE_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD)
    chart_response = request_handler.get_request(f"{CHART_ENDPOINT}/{slice_id}", verify=False)
    slice_name_from_json = chart_response.json().get("result", {}).get("slice_name")
    chart_params_json = chart_response.json().get("result", {}).get("params")
 
    # parses the JSON string 'chart_params_json' into a Python dictionary - deserialization
    params_dict = json.loads(chart_params_json)

    if 'datasource' in params_dict:
        new_datasource_value = f"{new_dataset_id}__table"
        params_dict['datasource'] = new_datasource_value
        print(f"Updated 'datasource' to: {new_datasource_value}")
    else:
        print("'datasource' key not found in params_dict. Adding it.")
        params_dict['datasource'] = new_datasource_value # Add if missing

    chart_data = {
            "slice_name":  slice_name_from_json, 
            "datasource_id": new_dataset_id,
            "datasource_type": "table",
            "params": json.dumps(params_dict),
            "description": "Updated data source!"
            }

    request_handler.put_request(f"{CHART_ENDPOINT}/{slice_id}", verify=False, json=chart_data)
    
    return data

'''
Reference - https://medium.com/@krprakruthiagri/apache-superset-dashboards-ui-vs-python-scripts-rest-api-fb9b99899ea6
'''
@app.route('/api/v1/update_charts', methods=['POST'])
def update_charts():
    DATASET_ID = 141
    data = request.get_json() # Get JSON data from the request body
  
    request_handler = APIRequestHandler(SUPERSET_INSTANCE_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD)

    chart_data = []
    for item in data:
        if item['destinationChart']:
            slice_id = item['slice_id']

            chart_response = request_handler.get_request(f"{CHART_ENDPOINT}/{slice_id}", verify=False)
            chart_params_json = chart_response.json().get("result", {}).get("params")
            datasource_id_from_json = chart_response.json().get("result", {}).get("datasource_id")
            print("*" * 50)
            print(datasource_id_from_json)
            print("*" * 50)
            
            # parses the JSON string 'chart_params_json' into a Python dictionary - deserialization
            params_dict = json.loads(chart_params_json)

            # 3. Update the 'datasource' key
            """ "params": json.dumps({
                    "viz_type": viz_type_from_params,
                   "datasource": f"{DATASET_ID}__table"
                }), """
            """
            if 'datasource' in params_dict:
                new_datasource_value = f"{DATASET_ID}__table"
                params_dict['datasource'] = new_datasource_value
                print(f"Updated 'datasource' to: {new_datasource_value}")
            else:
                print("'datasource' key not found in params_dict. Adding it.")
                params_dict['datasource'] = new_datasource_value # Add if missing
            """
            
            chart_data = {
                "slice_name":  item['destinationChart'], 
                "description": "Updated by cloner!"
            }

            request_handler.put_request(f"{CHART_ENDPOINT}/{slice_id}", verify=False, json=chart_data)

    return data

if __name__ == '__main__':
   app.run(debug=True, port=5000)
   


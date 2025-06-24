import os
import requests
import sys

class APIRequestHandler:
    def __init__(self, superset_instance_url, superset_username, superset_password):
        self.session = requests.Session()
        self.superset_instance_url = superset_instance_url
        self.superset_username = superset_username
        self.superset_password = superset_password
        self.headers_auth = self._get_headers()

    def _get_headers(self):
        if self.superset_username is None or self.superset_password is None:
            raise SystemExit('Both SUPERSET_USERNAME and SUPERSET_PASSWORD should be defined in the environment.')

        payload = {"username": self.superset_username, "password": self.superset_password, "provider": "db", "refresh": True}
    
        login_request = self.session.post(self.superset_instance_url + "api/v1/security/login", json=payload, verify=False)
        access_token = login_request.json().get("access_token")
        if not access_token:
            raise SystemExit("JWT token not found in response. "
                             "Please check the SUPERSET_USERNAME and SUPERSET_PASSWORD credentials.\n"
                             f"Response: {login_request.json()}")

        headers_auth = {"Authorization": "Bearer " + str(access_token)}
    
        csrf_request = self.session.get(self.superset_instance_url + "api/v1/security/csrf_token/", json=payload, \
                                        headers=headers_auth, verify=False)
        csrf_token = csrf_request.json().get('result')
        if not csrf_token:
            raise SystemExit("CSRF token not found in response. "
                             "Please check the SUPERSET_USERNAME and SUPERSET_PASSWORD credentials.\n"
                             f"Response: {csrf_request.json()}")
    
        headers_auth['X-CSRFToken'] = csrf_token
        # Verify caller function prior before setting header - export_dashboard requires 'application/zip'
        # Tip - https://stackoverflow.com/questions/900392/getting-the-caller-function-name-inside-another-function-in-python
        headers_auth['accept'] = ('application/zip' if sys._getframe(1).f_code.co_name == 'export_dashboard' else 'application/json')
        headers_auth['Referer'] = self.superset_instance_url
    
        return headers_auth

    def _execute_http_method(self, http_method, endpoint, **kwargs):
        try:
            response = http_method(self.superset_instance_url + endpoint, headers=self.headers_auth, **kwargs)
            response.raise_for_status()
            print(response.raise_for_status())
            return response
        except requests.exceptions.HTTPError as err:
            raise SystemExit(f"\nHTTP Error: '{err}'\n" + f"Response: {response.text}")
        finally:
            self.session.close()

    def post_request(self, endpoint, **kwargs):
        return self._execute_http_method(self.session.post, endpoint, **kwargs)

    def get_request(self, endpoint, **kwargs):
        return self._execute_http_method(self.session.get, endpoint, **kwargs)

    def put_request(self, endpoint, **kwargs):
        return self._execute_http_method(self.session.put, endpoint, **kwargs)

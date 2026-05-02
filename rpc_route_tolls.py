import time
import polyline
import typing
import requests
import json

from .str_util import str_human_duration, str_http_code

DEFAULT_ROUTE_POINTS_DELTA_SEC = 5

class RpcOptions:
    def __init__(self, log_verbose_req = False, log_service_response = False, log_req_duration = False):
        self.log_verbose_req = log_verbose_req
        self.log_req_duration = log_req_duration
        self.log_service_response = log_service_response

def rpc_call(url_path, http_method, auth_pair, req, rpc_options: RpcOptions):
    if rpc_options and rpc_options.log_verbose_req:
        print(f"Using URL: {url_path}")
        print(f"Using http_method: {http_method}")
        print(f"Using basic auth: {auth_pair}")

    if rpc_options and rpc_options.log_req_duration:
        print(f"Request start: {http_method} : {url_path}")

    req_start_ts = time.time()
    try:
        additional_headers = {
            'accept-encoding': 'gzip,deflate',
            'content-type': 'application/json'
        }
        if http_method == 'POST':
            response = requests.post(url_path, json=req, auth=auth_pair, headers=additional_headers)
        elif http_method == 'GET':
            response = requests.get(url_path, params=req, auth=auth_pair, headers=additional_headers)
        else:
            raise Exception(f"Unsupported http_method: {http_method}")
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise        
    req_sec = time.time() - req_start_ts
    if rpc_options and rpc_options.log_req_duration:
        print(f"Request completed: {str_http_code(response.status_code)}, took: {str_human_duration(req_sec)}")

    resp_obj = response.json()
    if 'data' not in resp_obj:
        print(f"Service error: {resp_obj}")
        return None
    
    return resp_obj['data']

class RouteTollsClient:
    def __init__(self, bolt_env, auth_pair, rpc_options: RpcOptions):
        self.bolt_env = bolt_env # 'live' or 'prelive'
        self.auth_pair = auth_pair # e.g. ('geo', 'secret.password')
        self.rpc_options = rpc_options

    def get_resolve_city_url(self):
        return f"http://node.{self.bolt_env}.boltint.net/route-tolls/databricks/resolveCity"
    
    def get_get_tolls_for_route_url(self):
        return f"http://node.{self.bolt_env}.boltint.net/route-tolls/databricks/getTollsForRoute"
    
    def call_endpoint(self, url_path, http_method, request):
        return rpc_call(url_path, http_method, self.auth_pair, request, self.rpc_options)
   
    def resolve_city(self, point):
        req = {
            "lat": point['lat'],
            "lng": point['lng']
        }

        city_info = self.call_endpoint(self.get_resolve_city_url(), 'GET', req)
        if self.rpc_options and self.rpc_options.log_service_response:
            print(f"Resolved point: {point} => City info: {city_info}")

        return city_info

    @staticmethod
    def decode_polyline_to_locations(polyline_str, start_sec):
        points = polyline.decode(polyline_str)
        locations = []
        for i, point in enumerate(points):
            locations.append({
                "lat": point[0],
                "lng": point[1],
                "acquired": (start_sec + i * DEFAULT_ROUTE_POINTS_DELTA_SEC) * 1000
            })
        return locations

    def get_tolls_for_route_locations(self, city_id, country_code, currency, category_id, locations, start_sec, provider=None):
        simple_route = {
            "route_id": "7",
            "locations": locations
        }

        req = {
            "city_id": city_id,
            "country_code": country_code,
            "price_currency": currency,
            "category_ids": [category_id],
            "requested_by_service": "databricks",
            "downstream_service": "toll-roads",
            "enable_edge_detection": True,
            "routes": [
                simple_route
            ]
        }

        if provider:
            req['downstream_service'] = provider
        
        if req['downstream_service'] == 'toll-roads-edge-detection':
            req['downstream_service'] = 'toll-roads'
            req['enable_edge_detection'] = True

        resp = self.call_endpoint(self.get_get_tolls_for_route_url(), 'POST', req)
        if self.rpc_options and self.rpc_options.log_service_response:
            print(f"Tolls: {resp}")

        return resp
    
    def get_tolls_for_route_polyline(self, city_id, country_code, currency, category_id, polyline_str, start_sec, provider=None):
        locations = RouteTollsClient.decode_polyline_to_locations(polyline_str, start_sec)
        return self.get_tolls_for_route_locations(city_id, country_code, currency, category_id, locations, start_sec, provider)

    def get_tolls_for_route_with_auto_resolve(self, polyline_str, start_sec):
        locations = RouteTollsClient.decode_polyline_to_locations(polyline_str, start_sec)

        city_info = self.resolve_city(locations[0])
        if city_info is None:
            raise Exception(f"Unable to resolve city for point: {locations[0]}")

        return self.get_tolls_for_route_locations(city_id=city_info['city_id'],
                                                  country_code=city_info['country_code'],
                                                  currency=city_info['currency'],
                                                  category_id=city_info['default_search_category']['id'],
                                                  locations=locations,
                                                  start_sec=start_sec)
    

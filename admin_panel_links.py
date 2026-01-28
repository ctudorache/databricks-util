import urllib
import json
from IPython.display import Markdown
from typing import List

def mk_link(text, url):
    return f"[{text}]({url})"

def admin_order_url(city_id, order_id):
    return f"https://admin-panel.bolt.eu/ride-hailing-order/orders/order/{order_id}/{city_id}"

def admin_order_link(city_id, order_id):
    return mk_link(str(order_id), admin_order_url(city_id, order_id))

def str_admin_panel_form_data(query_obj):
    return urllib.parse.quote(json.dumps(query_obj, separators=(',', ':')))

#################################################################################################
### getRoutes

def admin_getroutes_url(from_point: str, from_bearing: int, to_point: str) -> str:
    query = {
        "origin": from_point,
        "destination": to_point,
        "waypoints": "",
        "snap_nearest": False,
        "providers": ["internal"]
    }
    if from_bearing is not None:
        query["bearing"] = from_bearing

    return f"https://admin-panel.bolt.eu/geo/routing/getRoutes?formData={str_admin_panel_form_data(query)}"

def admin_getroutes_link(from_point: str, from_bearing: int, to_point: str) -> str:
    return mk_link("getRoutes", admin_getroutes_url(from_point, from_bearing, to_point))

#################################################################################################
### reverseGeocode

def admin_reversegeocode_url(input_point: str, providers: List[str],  language: str) ->  str:
    query = {
        "language": language,
        "lat_lng": input_point,
        "providers": providers
    }

    return f"https://admin-panel.bolt.eu/geo/geo/reverseGeocode?formData={str_admin_panel_form_data(query)}"

def admin_reversegeocode_link(input_point: str, providers: List[str],  language: str) -> str:
    return mk_link(f"reverseGeocode: {input_point}", admin_reversegeocode_url(input_point, providers, language))

#################################################################################################
### placeDetails

def admin_placedetails_url(place_id: str) ->  str:
    query = {
        "place_id": place_id,
        "language": "en"
    }

    return f"https://admin-panel.bolt.eu/geo/geo/getPlaceDetails?formData={str_admin_panel_form_data(query)}"

def admin_placedetails_link(place_id) -> str:
    return mk_link(f"placeDetails: {place_id}", admin_placedetails_url(place_id))

#################################################################################################
### Google placeDetails

def google_placedetails_url(place_id: str) -> str:
    if place_id.startswith('google|'):
        place_id = place_id[7:]
    query = {
        "place_id": place_id
    }
    return f"https://developers-dot-devsite-v2-prod.appspot.com/maps/documentation/utils/geocoder/#place_id={place_id}"

def google_placedetails_link(place_id) -> str:
    if place_id.startswith('google|'):
        place_id = place_id[7:]
    return mk_link(f"placeDetails: {place_id}", google_placedetails_url(place_id))

#################################################################################################
### OSM

def mk_osm_node_link(node_id):
    return mk_link(node_id, f'https://www.openstreetmap.org/node/{node_id}')

def mk_osm_segment_link(osm_segment_id):
    [from_node, to_node] = osm_segment_id.split('_')
    return mk_osm_node_link(from_node) + '_' + mk_osm_node_link(to_node)

#################################################################################################
### Atlas polyline visualisation

def atlas_polyline_url(polyline1, polyline2 = None, polyline3 = None):
    query_params = []
    if polyline1:
        query_params.append("polyline1=" + urllib.parse.quote(polyline1))
    if polyline2:
        query_params.append("polyline2=" + urllib.parse.quote(polyline2))
    if polyline3:
        query_params.append("polyline3=" + urllib.parse.quote(polyline3))

    str_query_params = '&'.join(query_params)
    return f"https://atlas.bolt.eu/route-similarity/?{str_query_params}"

def atlas_polyline_link(polyline1, polyline2):
    return mk_link("polyline-visualisation", atlas_polyline_url(polyline1, polyline2))
""" Utility functions for creating links in Markdown format, to:
- admin-panel: order
- admin-panel: getRoutes
- Atlas: polyline-visualisation

Usage example:
    mk_print(f" - Atlas: {atlas_polyline_link(live_polyline)}")
    mk_print(ff"- Admin order: {admin_order_link(city_id, order_id)}")
    
"""

import urllib
import json
from IPython.display import Markdown

def mk_print(text):
    display(Markdown(text + "<br>"))

def mk_link(text, url):
    return f"[{text}]({url})"

def str_admin_panel_form_data(query_obj):
    return urllib.parse.quote(json.dumps(query_obj, separators=(',', ':')))

def admin_order_url(city_id, order_id):
    return f"https://admin-panel.bolt.eu/ride-hailing-order/orders/order/{order_id}/{city_id}"

def admin_order_link(city_id, order_id):
    return mk_link(str(order_id), admin_order_url(city_id, order_id))

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

def atlas_polyline_link(polyline1, polyline2 = None, polyline3 = None):
    return mk_link("polyline-visualisation", atlas_polyline_url(polyline1, polyline2, polyline3))
from django.core.management.base import BaseCommand, CommandError
from flask import (Flask,
                   request,
                   Response)
import json

from django.conf import settings

class Command(BaseCommand):
    '''Call update_status on all checks for all services'''
    def handle(self, *args, **options):        
        app = Flask(__name__)

        @app.route("/simple/good/")
        def simple_service_check_good():
            return "Cornstalk Bearclaw"

        @app.route("/simple/bad/")
        def simple_service_check_bad():
            return "Something went wrong",500

        @app.route("/compare/")
        def compare_service_check():
            return Response(json.dumps({'test_field_name' : 1000}),
                            mimetype="application/json")

        @app.route("/compare/unknown/")
        def compare_service_check_unknown():
            return Response(json.dumps({}),
                            mimetype="application/json")

        @app.route("/aggregates/<check_name>")
        def sensu_aggregates(check_name):
            return Response(json.dumps(["111111"]),
                            mimetype="application/json")

        @app.route("/aggregates/<check_name>/<check_timestamp>")
        def sensu_service_check(check_name,check_timestamp):
            payload = {'ok':0,'critical':0,'warning':0}
            if check_name=="bad_check":
                payload['critical']+=1
            elif check_name=="good_check":
                payload['ok']+=1
            else:
                payload['warning']+=1
            
            return Response(json.dumps(payload),mimetype="application/json")

        @app.route("/check")
        def umpire_test():
            metric = request.args.get("metric")
            if metric=="good_metric":
                return json.dumps({'value':100}),200
            elif metric=="bad_metric":
                return json.dumps({'value':100}),500
            elif metric=="unknown_metric":
                return json.dumps({}),500
            else:
                return "wat",404

        @app.route("/render/")
        def graphite_test():
            metric = request.args.get("target")
            if metric=="good_metric":
                return "%s,0,0,60|50.0,50.0,50.0" % metric
            elif metric=="unknown_metric":
                return "wat",500
            else:
                return "%s,0,0,60|2341.0,23423.0,51231.0" % metric
            

        app.run(host=settings.FAKE_APP_HOST,port=settings.FAKE_APP_PORT)

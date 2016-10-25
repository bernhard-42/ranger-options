import sys
import json
import argparse
import requests

parser = argparse.ArgumentParser(description="Activate/Deactivate Rangers Deny Policy capability")
parser.add_argument("-r", dest="ranger",   nargs=1,   help="Ranger host",           required=True)
parser.add_argument("-u", dest="user",     nargs=1,   help="Ranger admin user",     required=True)
parser.add_argument("-p", dest="password", nargs=1,   help="Ranger admin password", required=True)
p_opt = parser.add_mutually_exclusive_group(required=True)
p_opt.add_argument("--list",              action="store_true", help="List status of all services")
p_opt.add_argument("--add_deny_policy",   action="store_true", help="Add Deny Policy to services")
p_opt.add_argument("--del_deny_policy",   action="store_true", help="Delete Deny Policy to services")
p_opt.add_argument("--add_join_cond",     action="store_true", help="Add Join Policy Condition to services")
p_opt.add_argument("--add_location_cond", action="store_true", help="Add Location Policy Condition to services")
p_opt.add_argument("--del_cond",          action="store_true", help="Delete Policy Condition(s) for ids")
parser.add_argument("-s", dest="services", nargs='+',          help="List of services (\"hive hdfs\") or for --del_cond service:id (\"hive:1 hdfs:2\")")
args = parser.parse_args()


url = "http://%s:6080/service/public/v2/api/servicedef/name" % args.ranger[0]
headers = {"Content-Type": "application/json"}
auth = (args.user[0], args.password[0])

denyOption = "enableDenyAndExceptionsInPolicies"

policyConditions = "policyConditions"
joinPolicyCondition = """{
  "itemId": %d,
  "name": "resources-accessed-together",
  "evaluator": "org.apache.ranger.plugin.conditionevaluator.RangerHiveResourcesAccessedTogetherCondition",
  "evaluatorOptions": {},
  "label": "Resources Accessed Together?",
  "description": "Resources Accessed Together?"
}"""

locationAttribute = "org.apache.ranger.plugin.contextenricher.RangerFileBasedGeolocationProvider"
locationPolicyCondition = """{
  "itemId": %d,
  "name": "location-outside",
  "evaluator": "org.apache.ranger.plugin.conditionevaluator.RangerContextAttributeValueNotInCondition",
  "evaluatorOptions": {
    "attributeName": "LOCATION_COUNTRY_CODE"
  },
  "label": "Accessed from outside of location?",
  "description": "Accessed from outside of location?"
}"""
contextEnrichers = "contextEnrichers"
locationEnricher = """{
  "itemId": %d,
  "enricher": "org.apache.ranger.plugin.contextenricher.RangerFileBasedGeolocationProvider",
  "enricherOptions": {
    "FilePath": "/etc/ranger/geo/geo.txt",
    "IPInDotFormat": "true"
  }
}"""

def put(sdef):
  res = requests.put("%s/%s" % (url, sdef["name"]), data=json.dumps(sdef), auth=auth, headers=headers)
  print "%s: %s" % (service, ("OK" if res.status_code == 200 else "Error: %d" % res.status_code))


def listStatus(sdef):
  print "==> %s (%d): " % (sdef["name"], sdef["id"])
  print "Deny Policy       = %s" % (sdef["options"].get(denyOption) or "false")
  print "Policy Conditions = %s" % json.dumps(sdef[policyConditions], indent=2) 
  print "Context Enrichers = %s" % json.dumps(sdef[contextEnrichers], indent=2) 
  print ""


def modifyDenyPolicy(sdef, value):
  sdef["options"][denyOption] = value
  put(sdef)
  

def maxId(conditions):
  itemIds = [c["itemId"] for c in conditions]
  return 1 if len(itemIds) == 0 else max(itemIds) + 1


def addJoinConditions(sdef):
  itemId = maxId(sdef[policyConditions])
  sdef[policyConditions].append(json.loads(joinPolicyCondition % itemId))
  put(sdef)


def addLocationConditions(sdef):
  itemId = maxId(sdef[policyConditions])
  sdef[policyConditions].append(json.loads(locationPolicyCondition % itemId))
  print "Path to geo table is /etc/ranger/geo/geo.txt"
  itemId = maxId(sdef[contextEnrichers])
  enrichers = [e for e in sdef[contextEnrichers] if e["enricher"] != locationAttribute] # remove if exists
  sdef[contextEnrichers] = enrichers + [json.loads(locationEnricher % itemId)]
  put(sdef)


def delCondition(sdef, id):
  conds = sdef[policyConditions]
  conds2 = [c for c in conds if c["itemId"] != id]
  sdef[policyConditions] = conds2
  put(sdef)


for service in args.services:
  if args.del_cond:
    parts = service.split(":")
    if len(parts) != 2:
      print "Error: services need to be of format \"service:id\""
      sys.exit(1)
    else:
      service = parts[0]
      id = int(parts[1])

  result = requests.get("%s/%s" %(url, service), auth=auth)
  if result.status_code != 200:
    print "Error", result.status_code
    sys.exit(2)

  sdef = result.json()

  if args.list:
    if sdef["name"] in args.services:
      listStatus(sdef)

  elif args.add_deny_policy or args.del_deny_policy:
    value = "true" if args.add_deny_policy else "false"
    modifyDenyPolicy(sdef, value)

  elif args.add_join_cond:
    addJoinConditions(sdef)


  elif args.add_location_cond:
    addLocationConditions(sdef)

  elif args.del_cond:
    delCondition(sdef, int(id))

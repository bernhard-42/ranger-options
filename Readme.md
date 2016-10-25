## Overview

Apache Ranger 0.6 (as in HDP 2.5) has a few options that can only be set via the REST API:

- Enable Denx Policies
- Add Policy Conditions (e.g. geolocation or access-together condition)
- Context Enrichers (e.g. geo file for geolocation contdition)

For reference see 

- [Geo location policies](https://cwiki.apache.org/confluence/display/RANGER/Geo-location+based+policies)
- [Deny conditions](https://cwiki.apache.org/confluence/display/RANGER/Deny-conditions+and+excludes+in+Ranger+policies)

This python script is meant to help with it:

## Help

```python
$ python ranger-options.py -h
usage: ranger-options.py [-h] -r RANGER -u USER -p PASSWORD
                         (--list | --add_deny_policy | --del_deny_policy | --add_join_cond | --add_location_cond | --del_cond)
                         [-s SERVICES [SERVICES ...]]

Activate/Deactivate Rangers Deny Policy capability

optional arguments:
  -h, --help            show this help message and exit
  -r RANGER             Ranger host
  -u USER               Ranger admin user
  -p PASSWORD           Ranger admin password
  --list                List status of all services
  --add_deny_policy     Add Deny Policy to services
  --del_deny_policy     Delete Deny Policy to services
  --add_join_cond       Add Join Policy Condition to services
  --add_location_cond   Add Location Policy Condition to services
  --del_cond            Delete Policy Condition(s) for ids
  -s SERVICES [SERVICES ...]
                        List of services ("hive hdfs") or for --del_cond
                        service:id ("hive:1 hdfs:2")
```

## Show settings of Hive:

```python
$ python ranger-options.py -r $RANGER -u admin -p $PASSWORD --list -s hive
==> hive (3):
Deny Policy       = true
Policy Conditions = [
  {
    "itemId": 1,
    "description": "Resources Accessed Together?",
    "label": "Resources Accessed Together?",
    "evaluator": "org.apache.ranger.plugin.conditionevaluator.RangerHiveResourcesAccessedTogetherCondition",
    "evaluatorOptions": {},
    "name": "resources-accessed-together"
  }
]
Context Enrichers = []
```

## Activate Deny Policies for Hive

```python
$ python ranger-options.py -r $RANGER -u admin -p $PASSWORD --add_deny_policy -s hive
hive: OK
Mac-BW:ranger-options bwalter$ python ranger-options.py -r $RANGER -u admin -p $PASSWORD --list -s hive
==> hive (3):
Deny Policy       = true
Policy Conditions = []
Context Enrichers = []
```

## Deactivate Deny policies for Hive

```python
$ python ranger-options.py -r $RANGER -u admin -p $PASSWORD --del_deny_policy -s hive
hive: OK

$ python ranger-options.py -r $RANGER -u admin -p $PASSWORD --list -s hive
==> hive (3):
Deny Policy       = false
Policy Conditions = []
Context Enrichers = []
```


## Add Access-Together policy for Hive

```python
$ python ranger-options.py -r $RANGER -u admin -p $PASSWORD --list -s hive
==> hive (3):
Deny Policy       = true
Policy Conditions = [
  {
    "itemId": 1,
    "description": "Resources Accessed Together?",
    "label": "Resources Accessed Together?",
    "evaluator": "org.apache.ranger.plugin.conditionevaluator.RangerHiveResourcesAccessedTogetherCondition",
    "evaluatorOptions": {},
    "name": "resources-accessed-together"
  }
]
Context Enrichers = []
```

## Add Geo Location Policy for Hive

```python
$ python ranger-options.py -r $RANGER -u admin -p $PASSWORD --list -s hive
==> hive (3):
Deny Policy       = true
Policy Conditions = [
  {
    "itemId": 1,
    "description": "Resources Accessed Together?",
    "label": "Resources Accessed Together?",
    "evaluator": "org.apache.ranger.plugin.conditionevaluator.RangerHiveResourcesAccessedTogetherCondition",
    "evaluatorOptions": {},
    "name": "resources-accessed-together"
  },
  {
    "itemId": 2,
    "description": "Accessed from outside of location?",
    "label": "Accessed from outside of location?",
    "evaluator": "org.apache.ranger.plugin.conditionevaluator.RangerContextAttributeValueNotInCondition",
    "evaluatorOptions": {
      "attributeName": "LOCATION_COUNTRY_CODE"
    },
    "name": "location-outside"
  }
]
Context Enrichers = [
  {
    "itemId": 3,
    "enricher": "org.apache.ranger.plugin.contextenricher.RangerFileBasedGeolocationProvider",
    "enricherOptions": {
      "FilePath": "/etc/ranger/geo/geo.txt",
      "IPInDotFormat": "true"
    }
  }
]
```

Note: this command also adds the context enricher.


## Delete hive policy conditions of Hive

```python
python ranger-options.py -r $RANGER -u admin -p $PASSWORD --list -s hive
==> hive (3):
Deny Policy       = true
Policy Conditions = []
Context Enrichers = [
  {
    "itemId": 3,
    "enricher": "org.apache.ranger.plugin.contextenricher.RangerFileBasedGeolocationProvider",
    "enricherOptions": {
      "FilePath": "/etc/ranger/geo/geo.txt",
      "IPInDotFormat": "true"
    }
  }
]
```

Note: in the current version context enrichers don't get deleted. However by removing and adding Geo-location policy again, the context enabler will be replaced (with new itemId)



# Momonitor

Momonitor was originally developed as a replacement to Nagios. It is currently the primary monitoring / reporting tool used at MoPub, which monitors hundreds of servers and billions of requests everyday. Momonitor was developed by @systemizer.

# Getting Started

Momonitor is a Django app that runs on a PostgreSQL backend and Redis Cache. Check and service configurations are kept in Postgres while application state is kept in Redis. Momonitor is configured to use Google OAuth for authentication via django-social-auth. For regular reporting checks, a crontab template has been provided. A gunicorn configuration file is provided in case you choose to run Momonitor with under a gunicorn process.

To install Momonitor, follow the below steps:

* git clone git@github.com:mopub/momonitor.git
* pip install -r requirements.txt
* cp local_settings_template.py local_settings.py
* Fill out the necessary constants in local_settings.py 
* Start the PostgreSQL server, create the necessary database. 
* python manage.py schemamigration main --initial
* python manage.py syncdb
* python manage.py migrate main
* python manage.py migrate social_auth
* python manage.py runserver

Additionally, to get Momonitor working fully, you'll need to:

* Create a crontab similar to the provided `crontab.template`
* Start redis-server on port 6379
    * This is Redis's default port, so you can do this by simply running `redis-server`

# Overview

## What it is
Momonitor is a simple tool that polls URL endpoints and runs checks on the respective responses. It integrates with several types of responses from multiple services, thus it leaves the check complexity to the process listening on the endpoint.

Essentially two types of things exist in Momonitor: services and checks. Services and checks each have a status (good, bad, or unknown).  Services are a collection checks that test a specific system. Multiple types of checks exist; each tests  different aspects of the target system.

## What it isn't
Momonitor is not a tool for finding errors on single machines. It lacks the functionality at peforming specific checks on specific machines. This is better done using a tool like Sensu. Momonitor integration with sensu is in the works.

### Types of Checks
* Simple Check - check a single URL endpoint and report whether the response was a 200 or 500
* Umpire Check - Umpire Checks allows to put minimum and maximum threholds on Graphite data. This check requires an umpire endpoint to be specified in the settings.py file for momonitor.
* Compare Check - Compare Checks check a single URL endpoint that returns serialized data (i.e. json). You can compare a single data field via dot-notation and compare arithmatically compare it to a given value
* Code Check - checks run arbitrary code on the momonitor server. This allows for the ultimate custom check, but be careful! The uploaded code should be a .py file that has a run function which returns a tuple (value,succeeded).

### Extra Check Options
* Frequency - Cron-like interface to specify how often you would like your check to run
* Failures before alert - Number of consecutive failures to occur before an alert is sent
* Silenced - If a check is silenced, it will not send alerts even if it is failing

### Check Statuses
* Good - The last check was passing
* Bad - The check has failed at least X times (default 1). This value is configurable via the "Failures Before Alert" option
* Unknown - The service / endpoint providing the check either failed or gave a non-valid response

### Types of Alerts
* Email - Email alerts will send an an email to the specified contact upon a check failing
* Pagerduty - Pagerduty alerts will trigger an event to the specified Pagerduty service key upon a check failing
* None - This option will disable alerts for the service

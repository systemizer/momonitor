.. momonitor documentation master file, created by
   sphinx-quickstart on Sat Mar 23 21:56:27 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Momonitor : Monitoring for Developers
=====================================

Release v 0.1

System monitoring shouldn't be scary. Momonitor is here to help. 

Momonitor is a simple `Apache2 License <http://www.apache.org/licenses/LICENSE-2.0.html>`_ monitoring solution built by developers, for developers. It was created out of frustration of configuring and maintaining `Nagios <http://www.nagios.org/>`_.

Why Momonitor?
--------------

* | **Manage your checks via a simple WebUI**
  | Edit, create, and delete system checks with a simple WebUI! No more needing to update foreign configuration files to manage your checks.
* | **Set intervals just like cron**
  | Configure the frequency with which your checks are run just like cron! (\*/5 \* \* \* \* == every 5 minutes!)
* | **Know what, when, and why**
  | Know when your checks run, whether they succeeded or failed, and why! Momonitor gives you an intuitive, human-readable interface for doing so.
* | **Designed for extensibility**
  | Adding new types of health checks is easy as cake. See the Sensu and Umpire checks for good examples.
* | **Alert via** `Pagerduty <http://www.pagerduty.com/>`_ **or generic email**
  | We have implemented builtin support for PagerDuty. Alerts are sent out immediently upon a failed check.
* | **Actively being worked on at** `MoPub <http://mopub.com>`_
  | MoPub uses Momonitor as its centralized monitoring system. We monitor a system that handles over a billion requests everyday.

How it works
============

Momonitor is a simple django app that manages and runs health checks on your systems. If a health check fails, Momonitor will alert you immedietely.

As a developer, you define services and health checks. Services are collections of health checks that share a bunch of defaults (i.e. check frequency, alert type). Several types of health checks have been implemented to help you monitor every aspect of your system. Go to the TODO LINK HEREChecks section to learn more!

When a check fails, momonitor will alert you! It will also highlight your failed checks in red on the WebUI.

See the video tutorial (below) for a more in-depth explanation.

VIDEO HERE

Getting Started
===============

Requirements
------------

* | **PostgreSQL**
  | Momonitor has only been tested with PostgreSQL, however there isn't any reason why it shouldn't work with any Django supported backend. (i.e. MySQL, SQLite)
* | **Python** 
  | Momonitor has been tested with Python2.7. Install the requirements included in the requirements file (pip install -r requirements.txt)
* | **Redis**
  | Momonitor keeps check state in a redis cache. Note that check state is currently not persisent unless you have enabled Redis persistence. This is optional.
* | **Cron**
  | Momonitor depends on Cron to run the management script.

::

     python manage.py service_check_cron
      
* | **Google OAuth**
  | Momonitor currently uses OAuth tied with your google account. A more generic authentication method will be implemented in future versions.
  | You need to set the domain white list to the email address that you use with your gmail account. For example, since we have @mopub.com for MoPub, we use the following configuration:

::

    GOOGLE_WHITE_LISTED_DOMAINS = ['mopub.com']


Setup from Nothing
------------------

First clone the Repo:
::

    git clone git@github.com:mopub/momonitor.git

Next, you will need to setup your database and sync your Django Models. Make sure the database is already running.
::

    psql -U postgres -c "CREATE ROLE <role-name> with password '<password>';"
    psql -U postgres -c "CREATE DATABASE <database-name> with owner <role-name>;"
    python manage.py syncdb
    python manage.py migrate

Add your local settings that is specific to your server
::

    cp local_settings_template.py local_settings.py

**local_settings.py**

::

    ##LOCAL SETTINGS FILE
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG

    DATABASES = {
       'default': {
          'ENGINE': 'django.db.backends.postgresql_psycopg2',
          'NAME': '<database-name>',
          'USER': '<role-name>',
          'PASSWORD': '<password>',
          'HOST': 'localhost',
          'PORT': '5432',
      }
  }

  FAKE_APP_PORT = 5000
  FAKE_APP_HOST = "localhost"

  import sys
  IS_TESTING = sys.argv[1:2] == ['test']

  if IS_TESTING:
      UMPIRE_ENDPOINT = "http://%s:%s/check" % (FAKE_APP_HOST,FAKE_APP_PORT)
      SENSU_API_ENDPOINT = "http://%s:%s" % (FAKE_APP_HOST,FAKE_APP_PORT)
      GRAPHITE_ENDPOINT = "http://%s:%s" % (FAKE_APP_HOST,FAKE_APP_PORT)
  else:
      UMPIRE_ENDPOINT = "http://example.org/check"
      SENSU_API_ENDPOINT = "http://example.org:4567"
      GRAPHITE_ENDPOINT = "http://example.org"

  #OAuth rule. Only allow people with a google email ending in 'example.org' to access the site   
  GOOGLE_WHITE_LISTED_DOMAINS = ['example.org']

  # Set this to the Domain of the site that will be hosting momonitor   
  DOMAIN = "http://localhost"

Start the server
::

   python manage.py runserver

Configure Cron to Run. Cron should **run the service_check_cron every minute** to keep Momonitor up to date. While this is not the most efficient way to keep checks runnning, it has worked for MoPub so far.

**/etc/cron.d/mycron**

::

   * * * * * <user> python <path-to-repo>/momonitor/manage.py service_check_cron

And, you're ready to go!


Overview
========

What it is
----------

Momonitor is a Django app that runs on a PostgreSQL backend and Redis Cache. Check and service configurations are kept in Postgres while application state is kept in Redis. Momonitor is configured to use Google OAuth for authentication via django-social-auth. Momonitor relies on cron to run checks. A crontab template file is provided for convenience.

Momonitor is a simple tool that polls URL endpoints and runs checks on the respective responses. It integrates with several types of responses from multiple services, thus it leaves the check complexity to the process listening on the endpoint.

Essentially two types of things exist in Momonitor: services and checks. Services and checks each have a status (good, bad, or unknown).  Services are a collection checks that test a specific system. Multiple types of checks exist; each tests  different aspects of the target system.

Types of Checks
---------------

* | **Simple Check** 
  | Check a single URL endpoint and report whether the response was a 200 or 500
* | **Umpire Check** 
  | Umpire Checks allows to put minimum and maximum threholds on Graphite data. Umpire checks require an `Umpire <https://github.com/heroku/umpire>`_ Server and `Graphite <http://graphite.wikidot.com/>`_ Server. To integrate with Momonitor...

::

   UMPIRE_ENDPOINT = "http://example.org/check"
   GRAPHITE_ENDPOINT = "http://example.org"

* | **Compare Check** 
  | Compare Checks check a single URL endpoint that returns serialized data (i.e. json). You can compare a single data field via dot-notation and compare arithmatically compare it to a given value
* | **Code Check** 
  | Checks run arbitrary code on the momonitor server. This allows for the ultimate custom check, but be careful! The uploaded code should be a .py file that has a run function which returns a tuple (value,succeeded).
* | **Sensu Check** 
  | Integrates with a Sensu Server, a service which runs checks on **many** machines. Momonitor monitoris sensu by checking the aggregate result.
  | Sensu checks require a `Sensu <https://github.com/sensu/sensu>`_ Server. To integrate with Momonitor...

::

    SENSU_API_ENDPOINT = "http://example.org:4567"

Extra Check Options
-------------------

* | **Frequency** 
  | Cron-like interface to specify how often you would like your check to run
* | **Failures before alert** 
  | Number of consecutive failures to occur before an alert is sent
* | **Silenced** 
  | If a check is silenced, it will not send alerts even if it is failing

Check Statuses
--------------

* | **Good** 
  | The last check was passing
* | **Bad** 
  | The check has failed at least X times (default 1). This value is configurable via the "Failures Before Alert" option
* | **Unknown** 
  | The service / endpoint providing the check either failed or gave a non-valid response

Types of Alerts
---------------

* | **Email** 
  | Email alerts will send an an email to the specified contact upon a check failing
* | **Pagerduty** 
  | Pagerduty alerts will trigger an event to the specified Pagerduty service key upon a check failing
* | **None** 
  | This option will disable alerts for the service


Other Features
==============

Momonitor comes with a couple additional features that make it more fun. These are by no means neccessary, but they continue to help us at MoPub

* | **Mobile UI** 
  | On the go? Enable the momonitor/mobile django app to get access to Momonitor's mobile interface. Currently, the interface allows you to view the health of all checks and silence them if neccessary.
* | **Slideshow** 
  | Have an extra unused TV hanging on the wall? Enable the momonitor/slideshow django app to get access to Momonitor's slideshow feature. Based on all of the checks you add, Momonitor will automatically create a slideshow for each service, which cycles through graphs of all of your checks.  

Testing
=======

For testing, we are using Django's builtin unittest.TestCase and a custom-made Flask http server to mimic external services (like Sensu and Umpire). To run tests, you must start up the flask server before running the test command:

::

    >>> python manage.py start_testing_faux_server

And then, in a separate tab...
::

    >>> python manage test



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
  | Configure the frequency with which your checks are run just like cron! (*/5 * * * * == every 5 minutes!)
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

* PostgresSQL
* Python (pip install -r requirements.txt)
* Redis
* Cron
* Google OAuth

Momonitor is a Django app that runs on a PostgreSQL backend and Redis Cache. Check and service configurations are kept in Postgres while application state is kept in Redis. Momonitor is configured to use Google OAuth for authentication via django-social-auth. Momonitor relies on cron to run checks. A crontab template file is provided for convenience.

Since Momonitor is a basic Django app, we ask that you review the `django documentation <https://docs.djangoproject.com/en/dev/topics/install/>`_ to learn how to setup Momonitor.

We have decided to use Google OAuth for authentication because it worked best for us at MoPub. In django settings, define the GOOGLE_WHITE_LISTED_DOMAINS variable as a list of subdomains that should have access to your Momonitor. For example, at MoPub, we set this value as ["mopub.com"], so anyone with a @mopub.com email can use our Momonitor.

NOTE: Sensu checks require a `Sensu <https://github.com/sensu/sensu>`_ Server. In the django settings file, set the SENSU_API_ENDPOINT variable to the URI of the Sensu Server.

NOTE: Umpire checks require an `Umpire <https://github.com/heroku/umpire>`_ Server and `Graphite <http://graphite.wikidot.com/>`_ Server. In the django settings file, set the UMPIRE_ENDPOINT and GRAPHITE_ENDPOINT variables to the URIs of the respective servers.

Overview
========

What it is
----------

Momonitor is a simple tool that polls URL endpoints and runs checks on the respective responses. It integrates with several types of responses from multiple services, thus it leaves the check complexity to the process listening on the endpoint.

Essentially two types of things exist in Momonitor: services and checks. Services and checks each have a status (good, bad, or unknown).  Services are a collection checks that test a specific system. Multiple types of checks exist; each tests  different aspects of the target system.

Types of Checks
---------------

* | **Simple Check** 
  | Check a single URL endpoint and report whether the response was a 200 or 500
* | **Umpire Check** 
  | Umpire Checks allows to put minimum and maximum threholds on Graphite data. This check requires an umpire endpoint to be specified in the settings.py file for momonitor.
* | **Compare Check** 
  | Compare Checks check a single URL endpoint that returns serialized data (i.e. json). You can compare a single data field via dot-notation and compare arithmatically compare it to a given value
* | **Code Check** 
  | Checks run arbitrary code on the momonitor server. This allows for the ultimate custom check, but be careful! The uploaded code should be a .py file that has a run function which returns a tuple (value,succeeded).
* | **Sensu Check** 
  | Integrates with a Sensu Server, a service which runs checks on **many** machines. Momonitor monitoris sensu by checking the aggregate result.

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

    >>> ./manage.py start_testing_faux_server

::

    >>> ./manage test

.. toctree::
   :maxdepth: 2



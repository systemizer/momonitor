.. momonitor documentation master file, created by
   sphinx-quickstart on Sat Mar 23 21:56:27 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Momonitor : Monitoring for Developers
=====================================

Release v 0.1

System monitoring shouldn't be scary. Momonitor is a simple monitoring tool built by developers, for developers. Linced under the `Apache2 License <http://www.apache.org/licenses/LICENSE-2.0.html>`_, Momonitor aims to make monitoring configuration as simple as clicking buttons on a simple Web UI.

`Nagios <http://www.nagios.org/>`_ is considered by many to be the industry standard for monitoring, however, its dashboard is not intuitive and its configuration tends to be difficult for developers. It was built in a time when developers didn't care about operations, and operations didn't care about development. Times have changed; enter Momonitor.

Why is Momonitor better?

* Edit and Create system checks without changing configuration files. Momonitor gives you a simple Web UI for managing every aspect of your checks.
* Configure the frequency with which each check just like cron! (*/5 * * * *)
* Web UI which shows (1) when the last check ran (2) whether it was successful or not (3) and why it failed or succeeded.
* Gives builtin `Pagerduty <http://www.pagerduty.com/>`_ support. If you prefer not to use pagerduty, Momonitor also offers generic email alerts.
* Builtin support for `Sensu <https://github.com/sensu/sensu>`_ and `Umpire <https://github.com/heroku/umpire>`_
* Designed for extensibility. Adding new types of checks is easy as cake.

How it works
============

Momonitor is a simple tool built with django that allows you to run health checks of your external systems at regular intervals. It supports several types of checks including HTTP Checks, Serialization Checks, and checks that work with other systems like Sensu and Umpire. Momonitor will alert you when any of these checks fail. It is currently the primary monitoring utility used by `MoPub <http://mopub.com>`_ today.

Check out a :ref:`demo`

Getting Started
===============

Momonitor is a Django app that runs on a PostgreSQL backend and Redis Cache. Check and service configurations are kept in Postgres while application state is kept in Redis. Momonitor is configured to use Google OAuth for authentication via django-social-auth. For regular reporting checks, a crontab template has been provided. A gunicorn configuration file is provided in case you choose to run Momonitor with under a gunicorn process.

Since Momonitor is a basic Django app, we ask that you review the django documentation to learn how to setup Momonitor.

Note that Sensu checks require a Sensu Server. In the django settings file, set the SENSU_API_ENDPOINT variable to the URI of the Sensu Server.

Also note that Umpire checks require an Umpire Server and Graphite Server. In the django settings file, set the UMPIRE_ENDPOINT and GRAPHITE_ENDPOINT variables to the URIs of the respective servers.

Overview
========

What it is
----------

Momonitor is a simple tool that polls URL endpoints and runs checks on the respective responses. It integrates with several types of responses from multiple services, thus it leaves the check complexity to the process listening on the endpoint.

Essentially two types of things exist in Momonitor: services and checks. Services and checks each have a status (good, bad, or unknown).  Services are a collection checks that test a specific system. Multiple types of checks exist; each tests  different aspects of the target system.

Types of Checks
---------------

* **Simple Check** - check a single URL endpoint and report whether the response was a 200 or 500
* **Umpire Check** - Umpire Checks allows to put minimum and maximum threholds on Graphite data. This check requires an umpire endpoint to be specified in the settings.py file for momonitor.
* **Compare Check** - Compare Checks check a single URL endpoint that returns serialized data (i.e. json). You can compare a single data field via dot-notation and compare arithmatically compare it to a given value
* **Code Check** - checks run arbitrary code on the momonitor server. This allows for the ultimate custom check, but be careful! The uploaded code should be a .py file that has a run function which returns a tuple (value,succeeded).
* **Sensu Check** - Integrates with a Sensu Server, a service which runs checks on **many** machines. Momonitor monitoris sensu by checking the aggregate result.

Extra Check Options
-------------------

* **Frequency** - Cron-like interface to specify how often you would like your check to run
* **Failures before alert** - Number of consecutive failures to occur before an alert is sent
* **Silenced** - If a check is silenced, it will not send alerts even if it is failing

Check Statuses
--------------

* **Good** - The last check was passing
* **Bad** - The check has failed at least X times (default 1). This value is configurable via the "Failures Before Alert" option
* **Unknown** - The service / endpoint providing the check either failed or gave a non-valid response

Types of Alerts
---------------

* **Email** - Email alerts will send an an email to the specified contact upon a check failing
* **Pagerduty** - Pagerduty alerts will trigger an event to the specified Pagerduty service key upon a check failing
* **None** - This option will disable alerts for the service


Other Features
==============

Momonitor comes with a couple additional features that make it more fun. These are by no means neccessary, but they continue to help us at MoPub

* **Mobile UI** - On the go? Enable the momonitor/mobile django app to get access to Momonitor's mobile interface. Currently, the interface allows you to view the health of all checks and silence them if neccessary.
* **Slideshow** - Have an extra unused TV hanging on the wall? Enable the momonitor/slideshow django app to get access to Momonitor's slideshow feature. Based on all of the checks you add, Momonitor will automatically create a slideshow for each service, which cycles through graphs of all of your checks.  

.. toctree::
   :maxdepth: 2



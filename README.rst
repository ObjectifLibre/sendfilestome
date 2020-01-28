################
Send Files To Me
################

What it is
==========

SendFilesToMe is a very basic file upload service. It has been developed to be
easily deployed and configured for short events (trainings, workshops, ...).

* Pure Django/python implementation (no http server required)
* Only a few settings
* Local storage
* Very basic authorization system
* Poorly tested

By default it authorizes anyone to upload and download files, without any kind
of limitation. But you can enable authentication to limit file access.

You have been warned :)

Roadmap (maybe)
===============

Any kind of modification might happen, without guaranteeing compatibility.

Some features that might land at some point:

* UI improvments
* File expiration

How to run it
=============

First, install the system dependencies required to build python-ldap:

.. code-block:: shell

   # Debian/Ubuntu, as root
   $ apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev

   # CentOS/RHEL, as root
   $ yum install python-devel openldap-devel

.. code-block:: console

   $ git clone https://github.com/gpocentek/sendfilestome
   $ cd sendfilestome/
   $ python3 -m venv venv
   $ . venv/bin/activate
   (venv) $ pip install -r requirements.txt
   (venv) $ cp sendfilestome/settings.py.example sendfilestome/settings.py
   (venv) $ mkdir -p uploads
   (venv) $ ./manage.py createsuperuser  # if you need authentication
   (venv) $ python manage.py migrate # On the first start only
   (venv) $ gunicorn -b 0.0.0.0:8000 sendfilestome.wsgi

How to use it
=============

To upload a file you first need to create a **container**. Containers are
similar to Amazon S3 buckets or OpenStack Swift containers. The container must
have a name and has 2 properties:

* ``listable``: if not set, the container will not be listed on the index page
  by default. It will still be available at ``http://SFTM/c/CONTAINER_NAME``.
* ``requires_auth``: if set the container and its files will only be available
  to authenticated users. This property is only used when authentication is
  enabled (see the :ref:`configuration` section)

You can only upload files in containers, not ouside containers. You cannot
create nested containers. If you have the permission to create the containers
and files, you can also delete them.

If you enable authentication and create a super-user you can access the Django
administration UI at ``http://SFTM/admin``. You can manage users, containers
and files using this interface.

.. _configuration:

Configuration
=============

The application leverages Django features for authentication, database access,
caching and storage. See the `Django 2.0 documentation
<https://docs.djangoproject.com/en/2.0/topics/settings/>`__ for more
information on these settings.

The following settings are specific to SendFilesToMe. You can define these
settings in ``sendfilestome/settings.py`` or in
``sendfilestome/local_settings.py``:

``MEDIA_ROOT``
    Path to the storage directory, where uploaded files will be stored.
    Default: ``uploads/`` at the project root.

``SFTM_UPLOAD_AUTH_ENABLED``
    If ``True`` creating containers and uploading files is only permitted to
    authenticated users. Default: ``False``.

``SFTM_DOWNLOAD_AUTH_ENABLED``
    If ``True`` downloading files is only permitted to authenticated users.
    Default: ``False``.

``SFTM_LIST_ALL_WHEN_AUTHENTICATED``
    If ``True`` authenticated users can list all the containers, including
    those marked as non listable. Default: ``True``.

.. note::

   You can override all the Django settings in
   ``sendfilestome/local_settings.py`` as well.

Contributing
============

Contributions are welcome. you can report issues, ask for new features, and
create pull requests on the `github project
<https://github.com/gpocentek/sendfilestome>`__.

UI contributions are very welcome. The UI is ugly and needs to be improved.

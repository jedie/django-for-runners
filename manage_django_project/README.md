# Manage Django project

A Django App to manage a Django project ;)

* Manage requirements with pip-tool

## install

You should have settings only for local development. Add there, e.g.:
```
INSTALLED_APPS.append('manage_django_project')

# The module name as string, used to import the module via importlib.import_module():
MANAGE_DJANGO_PROJECT_MODULE_NAME = 'your_django_project'
```

## Update requirements

```commandline
~/your_django_project$ ./manage.py update_req
```

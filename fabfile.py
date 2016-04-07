from fabric.api import cd, env, run, sudo, task, execute, local
from fabric.operations import put

from fabtools.vagrant import vagrant
from fabtools import require
import fabtools
import fabric
from StringIO import StringIO



from fabric.contrib.files import exists, append, comment, contains
from fabric.contrib.console import confirm

from fabric.colors import blue, cyan, green, red, blue

import os, sys

from gitric.api import git_seed, git_reset, allow_dirty, force_push, init_bluegreen, swap_bluegreen

@task
def default():
    '''
    Sets up the default env variables
    '''
    env.base_path = '/var/www/blooby/blooby'
    env.virtualenv_path = '/var/www/blooby'
    env.db_name = 'blooby'

default()

@task
def dep_test():
    env.bluegreen_root = '/home/vagrant/deploy_test/'
    env.bluegreen_ports = {'blue':'8888', 'green':'8000'}
    init_bluegreen()

@task
def deploy(commit=None):
    if not commit:
        commit = local('git rev-parse HEAD', capture=True)

    env.repo_path = env.next_path + '/repo'
    git_seed(env.repo_path, commit)
    git_reset(env.repo_path, commit)
    run('kill $(cat %(pidfile)s) || true' % env)


    env.pidfile = env.pidfile.replace("\\", "/")
    env.virtualenv_path = env.virtualenv_path.replace("\\", "/")
    env.repo_path = env.repo_path.replace("\\", "/")
    env.nginx_conf = env.nginx_conf.replace("\\", "/")

    run('virtualenv %(virtualenv_path)s' % env)
    run('source %(virtualenv_path)s/bin/activate && pip install -r %(repo_path)s/requirements.txt' % env)
    with fabtools.python.virtualenv(env.virtualenv_path), cd(env.repo_path):
        run('python manage.py migrate')
        run('python manage.py collectstatic --noinput')


    put(StringIO('proxy_pass http://127.0.0.1:%(bluegreen_port)s/;' % env), env.nginx_conf)

    sudo('cd %(repo_path)s && PYTHONPATH=. BLUEGREEN=%(color)s %(virtualenv_path)s/bin/gunicorn -D -b 0.0.0.0:%(bluegreen_port)s -p %(pidfile)s blooby.wsgi:application' % env)





@task
def staging():
    '''
    Sets up the staging env variables
    '''
    pass

@task
def live():
    '''
    Sets up live env variables
    '''
    pass

@task
def devserver(settings_file="blooby.settings"):
    '''
    Start the development server
    '''
    with fabtools.python.virtualenv(env.virtualenv_path), cd(env.base_path):
        run('python manage.py runserver 0.0.0.0:8000 --settings=%(settings_file)s' % locals())

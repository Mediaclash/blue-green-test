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
    env.bluegreen_ports = {'blue':'8888', 'green':'8889'}
    init_bluegreen()

@task
def deploy(commit=None):
    if not commit:
        commit = local('git rev-parse HEAD', capture=True)

    env.repo_path = env.next_path + '/repo'
    git_seed(env.repo_path, commit)
    git_reset(env.repo_path, commit)


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

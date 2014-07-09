#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Manage Docker containers
========================

`Docker <https://docker.io>`_
is a lightweight, portable, self-sufficient software container
wrapper. The base supported wrapper type is
`LXC <https://en.wikipedia.org/wiki/Linux_Containers>`_,
`cgroups <https://en.wikipedia.org/wiki/Cgroups>`_, and the
`Linux Kernel <https://en.wikipedia.org/wiki/Linux_kernel>`_.

.. warning::

    This state module is beta. The API is subject to change. No promise
    as to performance or functionality is yet present.

.. note::

    This state module requires
    `docker-py <https://github.com/dotcloud/docker-py>`_
    which supports `Docker Remote API version 1.6
    <https://docs.docker.io/en/latest/api/docker_remote_api_v1.6/>`_.

Available Functions
-------------------

- built

  .. code-block:: yaml

      corp/mysuperdocker_img:
          docker.built:
              - path: /path/to/dir/container/Dockerfile

- pulled

  .. code-block:: yaml

      ubuntu:
        docker.pulled

- installed

  .. code-block:: yaml

      mysuperdocker-container:
          docker.installed:
              - name: mysuperdocker
              - hostname: superdocker
              - image: corp/mysuperdocker_img
- running

  .. code-block:: yaml

      my_service:
          docker.running:
              - container: mysuperdocker
              - port_bindings:
                  "5000/tcp":
                      HostIp: ""
                      HostPort: "5000"


- absent

  .. code-block:: yaml

       mys_old_uperdocker:
          docker.absent

- run

  .. code-block:: yaml

       /finish-install.sh:
           docker.run:
               - container: mysuperdocker
               - unless: grep -q something /var/log/foo
               - docker_unless: grep -q done /install_log

.. note::

    The docker modules are named `dockerio` because
    the name 'docker' would conflict with the underlying docker-py library.

    We should add magic to all methods to also match containers by name
    now that the 'naming link' stuff has been merged in docker.
    This applies for exemple to:

        - running
        - absent
        - run
        - script


'''

# Import python libs
import re

# Import salt libs
from salt._compat import string_types

# Import 3rd-party libs
try:
    import docker
    HAS_DOCKER = True
except ImportError:
    HAS_DOCKER = False


# Define the module's virtual name
__virtualname__ = 'docker'


def __virtual__():
    '''
    Only load if the docker libs are available.
    '''
    if HAS_DOCKER:
        return __virtualname__
    return False


INVALID_RESPONSE = 'We did not get an acceptable answer from docker'
VALID_RESPONSE = ''
NOTSET = object()
#Use a proxy mapping to allow queries & updates after the initial grain load
MAPPING_CACHE = {}
FN_CACHE = {}

base_status = {
    'status': None,
    'id': None,
    'comment': '',
    'out': None
}


def __salt(fn):
    if not fn in FN_CACHE:
        FN_CACHE[fn] = __salt__[fn]
    return FN_CACHE[fn]


def _ret_status(exec_status=None,
                name='',
                comment='',
                result=None,
                changes=None):
    if not changes:
        changes = {}
    if exec_status is None:
        exec_status = {}
    if exec_status:
        if result is None:
            result = exec_status['status']
        scomment = exec_status.get('comment', None)
        if scomment:
            comment += '\n' + scomment
        out = exec_status.get('out', None)
        if out:
            if isinstance(out, string_types):
                print "out for name:%s => %s\n"%(name,out)
#                comment += '\n' + out
    return {
        'changes': changes,
        'result': result,
        'name': name,
        'comment': comment,
    }


def _valid(exec_status=None, name='', comment='', changes=None):
    return _ret_status(exec_status=exec_status,
                       comment=comment,
                       name=name,
                       changes=changes,
                       result=True)


def _invalid(exec_status=None, name='', comment='', changes=None):
    return _ret_status(exec_status=exec_status,
                       comment=comment,
                       name=name,
                       changes=changes,
                       result=False)


def mod_watch(name, sfun=None, *args, **kw):
    if sfun == 'built':
        # Needs to refresh the image
        kw['force'] = True
        build_status = built(name, **kw)
        result = build_status['result']
        status = _ret_status(build_status, name, result=result,
                             changes={name: result})
        return status
    elif sfun == 'installed':
        # Throw away the old container and create a new one
        remove_container = __salt__['docker.remove_container']
        remove_status = _ret_status(remove_container(container=name,
                                                     force=True,
                                                     **kw),
                                    name=name)
        installed_status = installed(name=name, **kw)
        result = installed_status['result'] and remove_status['result']
        comment = '\n'.join((remove_status['comment'],
                             installed_status['comment']))
        status = _ret_status(installed_status, name=name,
                             result=result,
                             changes={name: result},
                             comment=comment)
        return status
    elif sfun == 'running':
        # Force a restart against new container
        restarter = __salt__['docker.restart']
        status = _ret_status(restarter(kw['container']), name=name,
                             changes={name: True})
        return status

    return {'name': name,
            'changes': {},
            'result': False,
            'comment': ('watch requisite is not'
                        ' implemented for {0}'.format(sfun))}


def pulled(name, tag=None, force=False, *args, **kwargs):
    '''
    Pull an image from a docker registry. (`docker pull`)

    .. note::

        See first the documentation for `docker login`, `docker pull`,
        `docker push`,
        and `docker.import_image <https://github.com/dotcloud/docker-py#api>`_
        (`docker import
        <http://docs.docker.io/en/latest/commandline/cli/#import>`_).
        NOTE that We added saltack a way to identify yourself via pillar,
        see in the salt.modules.dockerio execution module how to ident yourself
        via the pillar.

    name
        Name of the image

    tag
        Tag of the image

    force
        Pull even if the image is already pulled
    '''
    ins = __salt('docker.inspect_image')
    iinfos = ins(name)
    if iinfos['status'] and not force:
        return _valid(
            name=name,
            comment='Image already pulled: {0}'.format(name))
    previous_id = iinfos['out']['id'] if iinfos['status'] else None
    func = __salt('docker.pull')
    returned = func(name,tag)
    if previous_id != returned['id']:
        changes = {name: True}
    else:
        changes = {}
    return _ret_status(returned, name, changes=changes)


def built(name,
          path=None,
          quiet=False,
          nocache=False,
          rm=True,
          force=False,
          timeout=None,
          *args, **kwargs):
    '''
    Build a docker image from a path or URL to a dockerfile. (`docker build`)

    name
        Tag of the image

    path
        URL (e.g. `url/branch/docker_dir/dockerfile`)
        or filesystem path to the dockerfile

    '''
    ins = __salt('docker.inspect_image')
    iinfos = ins(name)
    if iinfos['status'] and not force:
        return _valid(
            name=name,
            comment='Image already built: {0}, id: {1}'.format(
                name, iinfos['out']['id']))
    previous_id = iinfos['out']['id'] if iinfos['status'] else None
    func = __salt('docker.build')
    kw = dict(tag=name,
              path=path,
              quiet=quiet,
              nocache=nocache,
              rm=rm,
              timeout=timeout,
              )
    returned = func(**kw)
    if previous_id != returned['id']:
        changes = {name: True}
    else:
        changes = {}
    return _ret_status(returned, name, changes=changes)


def installed(name,
              image,
              command=None,
              hostname=None,
              user=None,
              detach=True,
              stdin_open=False,
              tty=False,
              mem_limit=0,
              ports=None,
              environment=None,
              dns=None,
              volumes=None,
              volumes_from=None,
              *args, **kwargs):
    '''
    Ensure that a container with the given name exists;
    if not, build a new container from the specified image.
    (`docker run`)

    name
        Name for the container

    image
        Image from which to build this container

    environment
        Environment variables for the container, either
            - a mapping of key, values
            - a list of mappings of key values
    ports
        List of ports definitions, either:
            - a port to map
            - a mapping of mapping portInHost : PortInContainer
    volumes
        List of volumes

    For other parameters, see absolutely first the salt.modules.dockerio
    execution module and the docker-py python bindings for docker
    documentation
    <https://github.com/dotcloud/docker-py#api>`_ for
    `docker.create_container`.

    .. note::
        This command does not verify that the named container
        is running the specified image.
    '''
    ins_image = __salt('docker.inspect_image')
    ins_container = __salt('docker.inspect_container')
    create = __salt('docker.create_container')
    iinfos = ins_image(image)
    if not iinfos['status']:
#        # try to pull if doesn't exist
#        ret = pulled(image)
#        if ret['result'] == False:
#            return _invalid(name=name,comment='image "{0}" does not exist'.format(image))
#        else:
#            iinfos = ins_image(image)
#            if not iinfos['status']:
#                return _invalid(name=name,comment='image "{0}" does not exist'.format(image))
        return _invalid(name=name,comment='image "{0}" does not exist'.format(image))
    cinfos = ins_container(name)
    already_exists = cinfos['status']
    # if container exists but is not started, try to start it
    if already_exists:
        cid = cinfos.get("out",{}).get("Id", "")
        return _valid(name=name,comment='image {0!r} already exists, container Id: {1!r}'.format(name,str(cid)))
    dports, dvolumes, denvironment = {}, [], {}
    if not ports:
        ports = []
    if not volumes:
        volumes = []
    if isinstance(environment, dict):
        for k in environment:
            denvironment[u'%s' % k] = u'%s' % environment[k]
    if isinstance(environment, list):
        for p in environment:
            if isinstance(p, dict):
                for k in p:
                    denvironment[u'%s' % k] = u'%s' % p[k]
    for p in ports:
        if not isinstance(p, dict):
            dports[str(p)] = {}
        else:
            for k in p:
                dports[str(p)] = {}
    for p in volumes:
        vals = []
        if not isinstance(p, dict):
            vals.append('%s' % p)
        else:
            for k in p:
                vals.append('{0}:{1}'.format(k, p[k]))
        dvolumes.extend(vals)
    a, kw = [image], dict(
        command=command,
        hostname=hostname,
        user=user,
        detach=detach,
        stdin_open=stdin_open,
        tty=tty,
        mem_limit=mem_limit,
        ports=dports,
        environment=denvironment,
        dns=dns,
        volumes=dvolumes,
        volumes_from=volumes_from,
        name=name)
    out = create(*a, **kw)
    # if container has been created, even if not started, we mark
    # it as installed
    try:
        cid = out['out']['info']['id']
    except Exception:
        pass
    else:
        out['comment'] = 'Container {0} created'.format(cid)
    ret = _ret_status(out, name)
    return ret




def absent(name):
    '''
    Ensure that the container is absent; if not, it will
    will be killed and destroyed. (`docker inspect`)

    name:
        Either the container name or id
    '''
    ins_container = __salt__['docker.inspect_container']
    cinfos = ins_container(name)
    if cinfos['status']:
        cid = cinfos['id']
        is_running = __salt__['docker.is_running'](cid)
        # destroy if we found meat to do
        if is_running:
            __salt__['docker.stop'](cid)
            is_running = __salt('docker.is_running')(cid)
            if is_running:
                return _invalid(
                    comment=('Container {0!r}'
                             ' could not be stopped'.format(cid)))
            else:
                return _valid(comment=('Container {0!r}'
                                       ' was stopped,'.format(cid)),
                              changes={name: True})
        else:
            return _valid(comment=('Container {0!r}'
                                   ' is stopped,'.format(cid)))
    else:
        return _valid(comment='Container {0!r} not found'.format(name))


def present(name):
    '''
    If a container with the given name is not present, this state will fail.
    (`docker inspect`)

    name:
        container id
    '''
    ins_container = __salt('docker.inspect_container')
    cinfos = ins_container(name)
    if cinfos['status']:
        cid = cinfos['id']
        return _valid(comment='Container {0} exists'.format(cid))
    else:
        return _invalid(comment='Container {0} not found'.format(cid or name))


def run(name,
        cid=None,
        hostname=None,
        stateful=False,
        onlyif=None,
        unless=None,
        docked_onlyif=None,
        docked_unless=None,
        *args, **kwargs):
    '''Run a command in a specific container


    You can match by either name or hostname

    name
        command to run in the container

    cid
        Container id

    state_id
        state_id

    stateful
        stateful mode

    onlyif
        Only execute cmd if statement on the host returns 0

    unless
        Do not execute cmd if statement on the host returns 0

    docked_onlyif
        Only execute cmd if statement in the container returns 0

    docked_unless
        Do not execute cmd if statement in the container returns 0

    '''
    if not hostname:
        hostname = cid
    retcode = __salt__['docker.retcode']
    drun = __salt__['docker.run']
    cmd_kwargs = ''
    if onlyif is not None:
        if not isinstance(onlyif, string_types):
            if not onlyif:
                return {'comment': 'onlyif execution failed',
                        'result': True}
        elif isinstance(onlyif, string_types):
            if retcode(onlyif, **cmd_kwargs) != 0:
                return {'comment': 'onlyif execution failed',
                        'result': True}

    if unless is not None:
        if not isinstance(unless, string_types):
            if unless:
                return {'comment': 'unless execution succeeded',
                        'result': True}
        elif isinstance(unless, string_types):
            if retcode(unless, **cmd_kwargs) == 0:
                return {'comment': 'unless execution succeeded',
                        'result': True}

    if docked_onlyif is not None:
        if not isinstance(docked_onlyif, string_types):
            if not docked_onlyif:
                return {'comment': 'docked_onlyif execution failed',
                        'result': True}
        elif isinstance(docked_onlyif, string_types):
            if drun(docked_onlyif, **cmd_kwargs) != 0:
                return {'comment': 'docked_onlyif execution failed',
                        'result': True}

    if docked_unless is not None:
        if not isinstance(docked_unless, string_types):
            if docked_unless:
                return {'comment': 'docked_unless execution succeeded',
                        'result': True}
        elif isinstance(docked_unless, string_types):
            if drun(docked_unless, **cmd_kwargs) == 0:
                return {'comment': 'docked_unless execution succeeded',
                        'result': True}
    return drun(**cmd_kwargs)


def running(name, container=None, port_bindings=None, binds=None,
            publish_all_ports=False, links=None, lxc_conf=None,
            privileged=False):
    '''
    Ensure that a container is running. (`docker inspect`)

    name
        name of the service

    container
        name of the container to start

    binds
        like -v of docker run command

        .. code-block:: yaml

            - binds:
                - /var/log/service: /var/log/service

    publish_all_ports

    links
        Link several container together

        .. code-block:: yaml

            - links:
                name_other_container: alias_for_other_container

    port_bindings
        List of ports to expose on host system
            - a mapping port's guest, hostname's host and port's host.

        .. code-block:: yaml

            - port_bindings:
                "5000/tcp":
                    HostIp: ""
                    HostPort: "5000"
    '''
    is_running = __salt('docker.is_running')(container)
    if is_running:
        return _valid(
            comment='Container {0!r} is started'.format(container))
    else:
        started = __salt__['docker.start'](
            container, binds=binds, port_bindings=port_bindings,
            lxc_conf=lxc_conf, publish_all_ports=publish_all_ports,
            links=links, privileged=privileged)
        is_running = __salt__['docker.is_running'](container)
        if is_running:
            return _valid(
                comment=('Container {0!r} started.\n').format(container),
                changes={name: True})
        else:
            return _invalid(
                comment=('Container {0!r}'
                         ' cannot be started\n{1!s}').format(container,
                                                            started['out']))


def script(name,
           cid=None,
           hostname=None,
           state_id=None,
           stateful=False,
           onlyif=None,
           unless=None,
           docked_onlyif=None,
           docked_unless=None,
           *args, **kwargs):
    '''
    Run a command in a specific container

    XXX: TODO: IMPLEMENT

    Matching can be done by either name or hostname

    name
        command to run in the docker

    cid
        Container id

    state_id
        State Id

    stateful
        stateful mode

    onlyif
        Only execute cmd if statement on the host return 0

    unless
        Do not execute cmd if statement on the host return 0

    docked_onlyif
        Only execute cmd if statement in the container returns 0

    docked_unless
        Do not execute cmd if statement in the container returns 0

    '''
    if not hostname:
        hostname = cid
    retcode = __salt__['docker.retcode']
    drun = __salt__['docker.run']
    cmd_kwargs = ''
    if onlyif is not None:
        if not isinstance(onlyif, string_types):
            if not onlyif:
                return {'comment': 'onlyif execution failed',
                        'result': True}
        elif isinstance(onlyif, string_types):
            if retcode(onlyif, **cmd_kwargs) != 0:
                return {'comment': 'onlyif execution failed',
                        'result': True}

    if unless is not None:
        if not isinstance(unless, string_types):
            if unless:
                return {'comment': 'unless execution succeeded',
                        'result': True}
        elif isinstance(unless, string_types):
            if retcode(unless, **cmd_kwargs) == 0:
                return {'comment': 'unless execution succeeded',
                        'result': True}

    if docked_onlyif is not None:
        if not isinstance(docked_onlyif, string_types):
            if not docked_onlyif:
                return {'comment': 'docked_onlyif execution failed',
                        'result': True}
        elif isinstance(docked_onlyif, string_types):
            if drun(docked_onlyif, **cmd_kwargs) != 0:
                return {'comment': 'docked_onlyif execution failed',
                        'result': True}

    if docked_unless is not None:
        if not isinstance(docked_unless, string_types):
            if docked_unless:
                return {'comment': 'docked_unless execution succeeded',
                        'result': True}
        elif isinstance(docked_unless, string_types):
            if drun(docked_unless, **cmd_kwargs) == 0:
                return {'comment': 'docked_unless execution succeeded',
                        'result': True}
    return drun(**cmd_kwargs)






##
## VisualOps States
##

def logged(url,
           username=None,
           password=None,
           email=None,
           *args, **kwargs):
    '''
    Login to a Docker repository. (`docker login`)

    url
        repo uri
    username
        username
    password
        password
    email
        email
    '''

    docker_loggin = __salt__['docker.login']
    ret = docker_loggin(url,username,password,email)

    status = base_status.copy()
    status["comment"] = ret["comment"]
    status["status"] = ret["result"]
    status["id"] = url

    return _ret_status(status, name=url)


# states aggregation
def full(name,
         image,
         bootstrap_cmd=None,
         repo=None,
         tag=None,
         username=None,
         password=None,
         email=None,
         force_pull=False,
         path=None,
         force_build=False,
         environment=None,
         ports=None,
         volumes=None,
         mem_limit=0,
         cpu_shares=None,
         # running
         service=None,
         binds=None,
         publish_all_ports=False,
         links=None,
         port_bindings=None,
         # run
         command=None,
         stateful=False,
         onlyif=None,
         unless=None,
         docked_onlyif=None,
         docked_unless=None,
         *args, **kwargs):
    out_text = ""
    force_install = False
    if repo:
        if username:
            lg = logged(repo,username,password,email)
            print "######### LOGGED #####"
            print lg
            print "######### /LOGGED #####"
            if lg.get('comment'):
                out_text += "%s\n"%(lg['comment'])
        ret = pulled(repo,tag,force=force_pull)
        print "######### PULLED #####"
        print ret
        print "######### /PULLED #####"
        if ret.get('comment'):
            out_text += "%s\n"%(ret['comment'])
        if not ret.get('result'):
            ret['comment'] = out_text
            return ret
        elif ret['changes']:
            force_install = True
    elif path:
        ret = built(image,path,force=force_build)
        print "######### BUILT #####"
        print ret
        print "######### /BUILT #####"
        if ret.get('comment'):
            out_text += "%s\n"%(ret['comment'])
        if ret['result'] == False:
            ret['comment'] = out_text
            return ret
        elif ret['changes']:
            force_install = True
    ret = installed(
        name,image,command=bootstrap_cmd,environment=environment,ports=ports,volumes=volumes,mem_limit=mem_limit,cpu_shares=cpu_shares)
    print "######### INSTALLED #####"
    print ret
    print "######### /INSTALLED #####"
    if ret.get('comment'):
        out_text += "%s\n"%(ret['comment'])
    if ret['result'] == False:
        ret['comment'] = out_text
        return ret
    s = re.search("already exists, container Id: '(.*)'",ret['comment'])
    if not s:
        s = re.search("Container (.*) created",ret['comment'])
    container = (s.group(1) if s else None)
    print "########## CONTAINER ID ##########"
    print container
    print "########## /CONTAINER ID ##########"
    if service:
        ret = running(
            service,container=container,port_bindings=port_bindings,binds=binds,publish_all_ports=publish_all_ports,links=links)
        print "######### RUNNING #####"
        print ret
        print "######### /RUNNING #####"
        if ret.get('comment'):
            out_text += "%s\n"%(ret['comment'])
        if ret['result'] == False:
            ret['comment'] = out_text
            return ret
    if command:
        ret = run(
            command,cid=container,stateful=stateful,onlyif=onlyif,unless=unless,docked_onlyif=docked_onlyif,docked_unless=docked_unless)
        print "######### RUN #####"
        print ret
        print "######### RUN #####"
        if ret.get('comment'):
            out_text += "%s\n"%(ret['comment'])
        if ret['result'] == False:
            ret['comment'] = out_text
            return ret

    status = base_status.copy()
    status["comment"] = "%s\nDocker done."%out_text
    status["status"] = True
    status["id"] = name

    #TODO: changes
    return _ret_status(status,name,changes={})



#TODO
def pushed(container,
           repository=None,
           tag=None,
           message=None,
           author=None,
           conf=None,
           *args, **kwargs):
    '''
    Push an image to a docker registry. (`docker push`)

    .. note::

        See first the documentation for `docker login`, `docker pull`,
        `docker push`,
        and `docker.import_image <https://github.com/dotcloud/docker-py#api>`_
        (`docker import
        <http://docs.docker.io/en/latest/reference/commandline/cli/#import>`_).
        NOTE that We added saltack a way to identify yourself via pillar,
        see in the salt.modules.dockerio execution module how to ident yourself
        via the pillar.

    container
        container id
    repository
        repository/imageName to commit to
    tag
        optional tag
    message
        optional commit message
    author
        optional author
    conf
        optional conf
    '''

    commit = __salt__['docker.commit']
    returned = commit(container,repository,tag,message,author,conf)

    #base_status = {
    #    'status': None,
    #    'id': None,
    #    'comment': '',
    #    'out': None
    #}

    print returned #debug
    if True:#has not changed TODO
        return _valid(
            name=container,
            comment='Countainer {0} up-to-date on repo {1}'.format(container,repository))
    push = __salt__['docker.push']
    returned = push(repository)
    changes = 'Countainer {0} pushed on repo {1}'.format(container,repository)
    return _ret_status(returned, container, changes=changes)


##




# pulled image
def _pulled(repo,
            tag=None,
            username=None,
            password=None,
            email=None,
            force_pull=False,
            containers=None,
            *args, **kwargs):
    out_text = ""
    force_install = False
    if repo:
        if username:
            lg = logged(repo,username,password,email)
            print "######### LOGGED #####"
            print lg
            print "######### /LOGGED #####"
            if lg.get('comment'):
                out_text += "%s\n"%(lg['comment'])
        ret = pulled(repo,tag,force=force_pull)
        print "######### PULLED #####"
        print ret
        print "######### /PULLED #####"
        if ret.get('comment'):
            out_text += "%s\n"%(ret['comment'])
        if not ret.get('result'):
            ret['comment'] = out_text
            return ret
        elif ret['changes']:
            force_install = True

    if force_install and containers:
        for container in containers:
            a = absent(container)
            if a.get('comment'):
                out_text += "%s\n"%(a['comment'])
            if not a.get('result'):
                a['comment'] = out_text
                return a

    status = base_status.copy()
    status["comment"] = out_text
    status["status"] = True
    status["id"] = name

    #TODO: changes
    return _ret_status(status,name,changes={})



# built image
def _built(image,
           path=None,
           containers=None,
           force_build=False,
           *args, **kwargs):
    out_text = ""
    force_install = False

    if image and path:
        ret = built(image,path,force=force_build)
        print "######### BUILT #####"
        print ret
        print "######### /BUILT #####"
        if ret.get('comment'):
            out_text += "%s\n"%(ret['comment'])
        if ret['result'] == False:
            ret['comment'] = out_text
            return ret
        elif ret['changes']:
            force_install = True

    if force_install and containers:
        for container in containers:
            a = absent(container)
            if a.get('comment'):
                out_text += "%s\n"%(a['comment'])
            if not a.get('result'):
                a['comment'] = out_text
                return a

    status = base_status.copy()
    status["comment"] = out_text
    status["status"] = True
    status["id"] = name

    #TODO: changes
    return _ret_status(status,name,changes={})



# running container
def _running(name,
             image,
             bootstrap_cmd=None,
             environment=None,
             ports=None,
             volumes=None,
             mem_limit=0,
             cpu_shares=None,
             # running
             binds=None,
             publish_all_ports=False,
             links=None,
             port_bindings=None,
             *args, **kwargs):

    out_text = ""
    ret = installed(
        name,image,command=bootstrap_cmd,
        environment=environment,ports=ports,volumes=volumes,mem_limit=mem_limit,cpu_shares=cpu_shares)
    print "######### INSTALLED #####"
    print ret
    print "######### /INSTALLED #####"
    if ret.get('comment'):
        out_text += "%s\n"%(ret['comment'])
    if ret['result'] == False:
        ret['comment'] = out_text
        return ret
    s = re.search("already exists, container Id: '(.*)'",ret['comment'])
    if not s:
        s = re.search("Container (.*) created",ret['comment'])
    container = (s.group(1) if s else None)
    print "########## CONTAINER ID ##########"
    print container
    print "########## /CONTAINER ID ##########"
    if service:
        ret = running(
            name,container=name,port_bindings=port_bindings,binds=binds,publish_all_ports=publish_all_ports,links=links)
        print "######### RUNNING #####"
        print ret
        print "######### /RUNNING #####"
        if ret.get('comment'):
            out_text += "%s\n"%(ret['comment'])
        if ret['result'] == False:
            ret['comment'] = out_text
            return ret


    status = base_status.copy()
    status["comment"] = "%s\nDocker done."%out_text
    status["status"] = True
    status["id"] = name

    #TODO: changes
    return _ret_status(status,name,changes={})

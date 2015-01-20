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
import hashlib
import json

# Import salt libs
from salt._compat import string_types
import salt.utils
from salt.utils.vops import *

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


CONFIG_PATH="/var/lib/visualops/opsagent"


INVALID_RESPONSE = 'We did not get an acceptable answer from docker'
VALID_RESPONSE = ''
NOTSET = object()
#Use a proxy mapping to allow queries & updates after the initial grain load
MAPPING_CACHE = {}
FN_CACHE = {}

base_status = {
    'status': None,
    'id': None,
    'name': None,
    'comment': '',
    'out': '',
    'state_stdout': '',
}


def __salt(fn):
    if not fn in FN_CACHE:
        FN_CACHE[fn] = __salt__[fn]
    return FN_CACHE[fn]


def _ret_status(exec_status=None,
                name='',
                comment='',
                result=None,
                changes=None,
                state_stdout=None):
    if not changes:
        changes = {}
    if exec_status is None:
        exec_status = {}
    if exec_status:
        if not name:
            name = exec_status.get('name','')
            if not name:
                name = exec_status.get('id','')
        if result is None:
            result = exec_status.get('status',None)
            if result is None:
                result = exec_status.get('result',False)
        scomment = exec_status.get('comment', None)
        if scomment:
            comment += '\n' + scomment
        stdout = exec_status.get('state_stdout', None)
        if stdout:
            if isinstance(stdout, string_types):
                state_stdout = stdout
        out = exec_status.get('out', None)
        if out:
            if isinstance(out, string_types):
#                # Debug
#                print "out for name:%s => %s\n"%(name,out)
                if not state_stdout:
                    state_stdout = out
    return {
        'id': name,
        'name': name,
        'result': result,
        'status': result,
        'comment': comment,
        'state_stdout': state_stdout,
        'changes': changes,
    }


def _valid(exec_status=None, name='', comment='', changes=None, state_stdout=None):
    return _ret_status(exec_status=exec_status,
                       comment=comment,
                       name=name,
                       changes=changes,
                       state_stdout=state_stdout,
                       result=True)


def _invalid(exec_status=None, name='', comment='', changes=None, state_stdout=None):
    return _ret_status(exec_status=exec_status,
                       comment=comment,
                       name=name,
                       changes=changes,
                       state_stdout=state_stdout,
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
        res = True
        if "containers" not in kw:
            return _invalid(comment='Container name missing')
        if "ports" in kw and "port_bindings" in kw:
            (ports,port_bindings) = gen_ports(kw["ports"],kw["port_bindings"],len(kw["containers"]))
            if not ports or not port_bindings:
                return _invalid(comment="Error generating port bindings (is there enough space between each allocation required?)")
        comment = ""
        for container in kw['containers']:
            status = _ret_status(restarter(container), name=name,
                                 changes={name: True})
            comment += "%s\n"%status.get("comment")
            if not status.get("result"):
                kw["ports"] = (ports.pop() if ports else None)
                kw["port_bindings"] = (port_bindings.pop() if port_bindings else None)
                kw["image"] = kw.get("image",None)
                status = vops_running_one(container,**kw)
                comment += "%s\n"%status.get("comment")
            if not status.get("result"):
                res = False
        status["result"] = res
        status["comment"] = comment
        return status

    return {'name': name,
            'changes': {},
            'result': False,
            'comment': ('watch requisite is not'
                        ' implemented for {0}'.format(sfun))}


def pulled(repo, tag=None, username=None, password=None, email=None, force=False, *args, **kwargs):
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

    repo
        Repo on which download the image

    tag
        Tag of the image

    force
        Pull even if the image is already pulled
    '''
    repo_base = repo
    repo = ("%s:%s"%(repo,tag) if tag else repo)
    ins = __salt('docker.inspect_image')
    iinfos = ins(repo)
    if iinfos['status'] and not force:
        return _valid(
            name=repo,
            comment='Image already pulled: {0}'.format(repo))
    previous_id = iinfos['out']['id'] if iinfos['status'] else None
    func = __salt('docker.pull')
    returned = func(repo_base, tag, username=username, password=password,email=email)
    if previous_id != returned['id']:
        changes = {repo: True}
    else:
        changes = {}
    return _ret_status(returned, repo, changes=changes)


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
    return _ret_status(returned, name, changes=changes,state_stdout=returned.get('out',''))


def installed(name,
              image,
              entrypoint=None,
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
#              devices=None,
#              port_bindings=None,
#              binds=None,
              force=False,
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
#    repo, image = docker.auth.auth.resolve_repository_name(image)
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
        if cinfos.get("out",{}).get("State", {}).get("Running", False) and not force:
            cid = cinfos.get("out",{}).get("Id", "")
            return _valid(name=name,comment='Container {0!r} already exists, container Id: {1!r}'.format(name,str(cid)))
        else:
            # Throw away the old container
            remove_container = __salt__['docker.remove_container']
            remove_status = _ret_status(remove_container(container=name,
                                                         force=True),
                                        name=name)
    dports, dvolumes, denvironment, de = {}, [], {}, {}
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
        entrypoint=entrypoint,
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
#        devices=devices,
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
            privileged=False, devices=None, *args, **kwargs):
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
            links=links, privileged=privileged, devices=devices)
        is_running = __salt__['docker.is_running'](container)
        if is_running:
            return _valid(
                comment=('Container {0!r} started.\n').format(container),
                changes={name: True})
        else:
            return _invalid(
                comment=('Container {0!r}'
                         ' cannot be started\n').format(container),
                state_stdout=started['out'])


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

# push image on repo
def vops_pushed(repository,
                container=None,
                tag=None,
                message=None,
                author=None,
                username=None,
                password=None,
                email=None,
                conf=None,
                dep_containers=None,
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

    repository
        namespace/repository to push in
    container
        container id (if commit container to image)
    tag
        optional tag
    message
        optional commit message
    author
        optional author
    username
        username
    password
        password
    email
        email
    conf
        optional conf
    dep_containers
        containers to stop
    '''

    out_text = ""

    if container:
        commit = __salt__['docker.commit']
        ret = commit(container,repository,tag,message,author,conf)

#        # DEBUG
#        print "######### COMMIT #####"
#        print ret
#        print "######### /COMMIT #####"

        if ret.get("comment"):
            out_text += "%s\n"%ret["comment"]

        if not ret.get('status'):
            ret['comment'] = out_text
            return _invalid(
                exec_status=ret,
                name=container)
        else:
            out_text += "Container %s commited.\n"%(container)
#    else:
#        return _invalid(comment="container name missing")

    push = __salt__['docker.push']
    ret = push(repository,tag=tag,username=username,password=password,email=email)

#    # DEBUG
#    print "######### PUSH #####"
#    print ret
#    print "######### /PUSH #####"

    if ret.get("comment"):
        out_text += "%s\n"%ret["comment"]

    ret["state_stdout"] = ret.get("out")

    if not ret.get('status'):
        ret['comment'] = out_text
        return _invalid(
            exec_status=ret,
            name=container)

    if dep_containers and ret.get('changes'):
        for container in dep_containers:
            a = absent(container)
            if a.get('changes') and a.get('comment'):
                out_text += "%s\n"%(a['comment'])
            if not a.get('result'):
                a['comment'] = out_text
                return _ret_status(a)

    status = base_status.copy()
    status["comment"] = "%sRepo %s pushed."%(out_text,repository)
    status["status"] = True
    status["id"] = repository
#    status["state_stdout"] = ret["state_stdout"]

    return _ret_status(status,repository,changes={repository:ret.get('changes',False)})


# pulled image
def vops_pulled(repo,
                tag=None,
                username=None,
                password=None,
                email=None,
                containers=None,
                *args, **kwargs):
    out_text = ""
    force_install = False


    if repo:
        ret = pulled(repo,tag,force=True,username=username,password=password,email=email)
#        # PUSHED
#        print "######### PULLED #####"
#        print ret
#        print "######### /PULLED #####"
        if ret.get('comment'):
            out_text += "%s\n"%(ret['comment'])
        if not ret.get('status'):
            ret['comment'] = out_text
            return _ret_status(ret)
        elif ret['changes']:
            force_install = True
            out_text += "New image version pulled."
    else:
        return _invalid(comment="repo missing")

    if force_install and containers:
        if type(containers) is not list:
            containers = [containers]
        for container in containers:
            a = absent(container)
            if a.get('comment') and re.search(a['comment'],"not found"):
                for i in range(1000):
                    a = absent("%s_%s"%(container,i+1))
                    if a.get('comment') and re.search(a['comment'],"not found"):
                        break
                    if a.get('changes') and a.get('comment'):
                        out_text += "%s\n"%(a['comment'])
                    if not a.get('result'):
                        a['comment'] = out_text
                        return _ret_status(a)
            else:
                if a.get('changes') and a.get('comment'):
                    out_text += "%s\n"%(a['comment'])
                if not a.get('result'):
                    a['comment'] = out_text
                    return _ret_status(a)


    status = base_status.copy()
    status["comment"] = out_text
    status["status"] = True
    status["id"] = repo

    #TODO: changes
    return _ret_status(status,repo,changes={})



# built image
def vops_built(tag,
               path=None,
               containers=None,
               force=False,
               *args, **kwargs):
    out_text = ""
    state_stdout = ""
    force_install = False


    if tag and path and force:
        ret = built(tag,path,force=force)
#        # DEBUG
#        print "######### BUILT #####"
#        print ret
#        print "######### /BUILT #####"
        if ret.get('state_stdout'):
            state_stdout += stream_to_print(ret.get('state_stdout',''))
        if ret.get('status'):
            if ret.get('changes'):
                out_text += "Image %s built from Dockerfile in %s\n"%(tag,path)
            else:
                out_text += "Image %s from Dockerfile in %s already built\n"%(tag,path)
        else:
            ret['comment'] = "%s%s\nBuilt failed."%(out_text,ret['comment'])
            return _ret_status(ret)
        if ret.get('changes'):
            force_install = True
    elif not force:
        out_text += "Image %s from Dockerfile in %s already built\n"%(tag,path)
    elif not tag:
        return _invalid(comment="tag name missing")
    elif not path:
        return _invalid(comment="path name missing")

    if force_install and containers:
        for container in containers:
            a = absent(container)
            if a.get('changes') and a.get('comment'):
                out_text += "%s\n"%(a['comment'])
            if not a.get('result'):
                a['result'] = False
                a['comment'] = out_text
                return _ret_status(a)

    status = base_status.copy()
    status["comment"] = out_text
    status["status"] = True
    status["id"] = tag

    #TODO: changes
    return _ret_status(status,tag,changes={})#,state_stdout=state_stdout)



# running container
def vops_running_one(container,
                     image,
                     entrypoint=None,
                     command=None,
                     environment=None,
                     ports=None,
                     volumes=None,
                     devices=None,
                     mem_limit=0,
                     cpu_shares=None,
                     # running
                     binds=None,
                     publish_all_ports=False,
                     links=None,
                     port_bindings=None,
                     force=False,
                     *args, **kwargs):

    out_text = ""
    ret = installed(
        container,image,entrypoint=entrypoint,command=command,environment=environment,#binds=binds,port_bindings=port_bindings,
        ports=ports,volumes=volumes,mem_limit=mem_limit,cpu_shares=cpu_shares,force=force,hostname=container)#,devices=devices)
#    # DEBUG
#    print "######### INSTALLED #####"
#    print ret
#    print "######### /INSTALLED #####"
    if ret.get('comment'):
        out_text += "%s\n"%(ret['comment'])
    if ret['result'] == False:
        ret['comment'] = out_text
        return _ret_status(ret)
    s = re.search("already exists, container Id: '(.*)'",ret['comment'])
    if not s:
        s = re.search("Container (.*) created",ret['comment'])
#    container = (s.group(1) if s else container)
#    # DEBUG
#    print "########## CONTAINER ID ##########"
#    print container
#    print "########## /CONTAINER ID ##########"

    ret = running(
        container,container=container,port_bindings=port_bindings,
        binds=binds,devices=devices)
#    # DEBUG
#    print "######### RUNNING #####"
#    print ret
#    print "######### /RUNNING #####"
    if ret.get('comment'):
        out_text += "%s\n"%(ret['comment'])
    if ret['result'] == False:
        ret['comment'] = out_text
        return _ret_status(ret)

    status = base_status.copy()
    status["comment"] = "%s\nContainer %s running."%(out_text,container)
    status["status"] = True
    status["id"] = container

    #TODO: changes
    return _ret_status(status,container,changes={})


def get_port(port):
    p = port.split("/")
    return int(p[0])

def test_ports(pb,length):
    hosts = sorted([int(pb[guest].get("HostPort",0)) for guest in pb])
    if not hosts:
        return False
    previous = hosts[0]
    for port in hosts[1:]:
        if (port - previous < length):
            return False
    return True

def gen_ports(ports,port_bindings,length):
    out_ports = []
    out_port_bindings = []

    if test_ports(port_bindings,length) is False:
        return (None,None)

    i = 0
    while i < length:
        cur_port = []
        for p in ports:
            port = p.split("/")
            protocol = ("tcp" if len(port) != 2 else port[1])
            port = int(port[0])
            cur_port.append("%s/%s"%(port,protocol))
        out_ports.append(cur_port)
        i += 1

    i = 0
    while i < length:
        cur_pb = {}
        for p in port_bindings:
            port = p.split("/")
            protocol = ("tcp" if len(port) != 2 else port[1])
            port = int(port[0])
            cur_pb["%s/%s"%(port,protocol)] = {
                "HostIp": port_bindings[p].get("HostIp"),
                "HostPort": int(port_bindings[p].get("HostPort",0))+i
            }
        out_port_bindings.append(cur_pb)
        i += 1

    return (out_ports[::-1],out_port_bindings[::-1])

def vops_running(containers,
                 image,
                 tag=None,
                 entrypoint=None,
                 command=None,
                 environment=None,
                 ports=None,
                 volumes=None,
                 devices=None,
                 mem_limit=0,
                 cpu_shares=None,
                 # running
                 binds=None,
                 publish_all_ports=False,
                 links=None,
                 port_bindings=None,
                 force=False,
                 count=0,
                 *args, **kwargs):

    if not containers:
        return _invalid(comment='Container name missing')

    if ports and port_bindings:
        (ports,port_bindings) = gen_ports(ports,port_bindings,len(containers))
        if not ports or not port_bindings:
            return _invalid(comment="Error generating port bindings (is there enough space between each allocation required?)")


    # Persist parameters
    directory = os.path.join(CONFIG_PATH,"docker_persist")
    try:
        if not os.path.isdir(directory):
            os.makedirs(directory,0755)
    except Exception as e:
        pass
    filepath = os.path.join(directory,kwargs.get("name","default"))
    cs_old = None
    try:
        with open(filepath,'r') as f:
            cs_old = f.read()
    except Exception as e:
        pass
    d = {
        'containers': containers,
        'image': image,
        'tag': tag,
        'entrypoint': entrypoint,
        'command': command,
        'environment': environment,
        'ports': ports,
        'volumes': volumes,
        'devices': devices,
        'mem_limit': mem_limit,
        'cpu_shares': cpu_shares,
        'binds': binds,
        'publish_all_ports': publish_all_ports,
        'links': links,
        'port_bindings': port_bindings,
        'count': count
    }
    md5 = hashlib.md5()
    md5.update(json.dumps(d))
    cs = md5.hexdigest()
    if cs_old and (cs_old != cs):
        force = True
    try:
        with open(filepath,'w') as f:
            f.write(cs)
    except Exception as e:
        pass


    if tag:
        image = "%s:%s"%(image,tag)
    comment = ""

    count = int(count)

    result = True
    if containers:
        i = count
        container_root = containers[0]
        while True:
            container = ("%s_%s"%(container_root.rsplit("_",1)[0],i+1)
                         if count != 0
                         else "%s_%s"%(container_root,i+1))
            tmp_status = absent(container)
            if re.search("not found",tmp_status.get("comment","")):
                break
            status = tmp_status
            comment += "%s\n"%status.get("comment")
            if status.get("status") is False:
                result = False
                break
            i += 1
        if count != 0:
            container = container_root.rsplit("_",1)[0]
            tmp_status = absent(container)
            if not re.search("not found",tmp_status.get("comment","")):
                status = tmp_status
                comment += "%s\n"%status.get("comment")
                if status.get("status") is False:
                    result = False

    i = 0
    for container in containers:
        if result is False:
            break
        port = (ports.pop() if ports else None)
        port_binding = (port_bindings.pop() if port_bindings else None)
        status = vops_running_one(container,
                                  image=image,
                                  entrypoint=entrypoint,
                                  command=command,
                                  environment=environment,
                                  ports=port,
                                  volumes=volumes,
                                  devices=devices,
                                  mem_limit=mem_limit,
                                  cpu_shares=cpu_shares,
                                  binds=binds,
                                  publish_all_ports=publish_all_ports,
                                  links=links,
                                  port_bindings=port_binding,
                                  force=force)
        comment += "%s\n"%status.get("comment")
        if status.get("status") is False:
            break
        i += 1

    status["comment"] = comment
    return status

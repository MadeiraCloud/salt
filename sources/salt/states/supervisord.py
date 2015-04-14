# -*- coding: utf-8 -*-
'''
Interaction with the Supervisor daemon
======================================

.. code-block:: yaml

    wsgi_server:
      supervisord:
        - running
        - require:
          - pkg: supervisor
        - watch:
          - file.managed: /etc/nginx/sites-enabled/wsgi_server.conf
'''

# Import python libs
import logging
import subprocess

# Import salt libs
import salt.utils

log = logging.getLogger(__name__)


def _check_error(result, success_message):
    ret = {}

    if 'ERROR' in result.upper():
        ret['comment'] = result
        ret['result'] = False
    else:
        ret['comment'] = success_message

    return ret


def _is_stopped_state(state):
    return state in ('STOPPED', 'STOPPING', 'EXITED', 'FATAL')

def _is_running_state(state):
    return state == 'RUNNING'


def running(name,
            restart=False,
            update=False,
            user=None,
            runas=None,
            conf_file=None,
            bin_env=None):
    '''
    Ensure the named service is running.

    name
        Service name as defined in the supervisor configuration file

    restart
        Whether to force a restart

    update
        Whether to update the supervisor configuration.

    runas
        Name of the user to run the supervisorctl command

        .. deprecated:: 0.17.0

    user
        Name of the user to run the supervisorctl command

        .. versionadded:: 0.17.0

    conf_file
        path to supervisorctl config file

    bin_env
        path to supervisorctl bin or path to virtualenv with supervisor
        installed

    '''
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}, 'state_stdout': ''}

    salt.utils.warn_until(
        'Hydrogen',
        'Please remove \'runas\' support at this stage. \'user\' support was '
        'added in 0.17.0',
        _dont_call_warnings=True
    )
    if runas:
        # Warn users about the deprecation
        ret.setdefault('warnings', []).append(
            'The \'runas\' argument is being deprecated in favor of \'user\', '
            'please update your state files.'
        )
    if user is not None and runas is not None:
        # user wins over runas but let warn about the deprecation.
        ret.setdefault('warnings', []).append(
            'Passed both the \'runas\' and \'user\' arguments. Please don\'t. '
            '\'runas\' is being ignored in favor of \'user\'.'
        )
        runas = None
    elif runas is not None:
        # Support old runas usage
        user = runas
        runas = None

    # start supervisord
    try:
        cmd = 'ps aux|grep supervisord'
        if conf_file:
            cmd = '{0} {1} {2}'.format(cmd, '|grep "\-c"|grep ', conf_file)
        is_supervisord = subprocess.Popen(
            cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE).communicate()[0].strip().find('python')
        if is_supervisord < 0:
            cmd = ['supervisord']
            if conf_file:
                cmd += ['-c', conf_file]
            result = __salt__['cmd.run_stdall'](' '.join(cmd), runas=user)
            if result['retcode'] != 0:
                ret['result'] = False
                ret['comment'] = 'Start supervisord failed.'
                ret['state_stdout'] = result['stdout']
                return ret

            # waiting for all services starting
            import time
            time.sleep(5)
    except Exception, e:
        ret['result'] = False
        ret['comment'] = 'Start up supervisord failed.'
        ret['state_stdout'] = str(e)
        return ret

    all_processes = __salt__['supervisord.status'](
        user=user,
        conf_file=conf_file,
        bin_env=bin_env
    )

    # parse process groups
    process_groups = []
    for proc in all_processes:
        if ':' in proc:
            process_groups.append(proc[:proc.index(':')])
    process_groups = list(set(process_groups))

    # determine if this process/group needs load
    needs_update = name not in all_processes and name not in process_groups

    if __opts__['test']:
        ret['result'] = None
        _msg = 'restarted' if restart else 'started'
        _update = ', but service needs to be added' if needs_update else ''
        ret['comment'] = (
            'Service {0} is set to be {1}{2}'.format(
                name, _msg, _update))
        return ret

    changes = []
    just_updated = False
    if needs_update:
        comment = 'Adding service: {0}'.format(name)
        __salt__['supervisord.reread'](
            user=user,
            conf_file=conf_file,
            bin_env=bin_env
        )
        result = __salt__['supervisord.add'](
            name,
            user=user,
            conf_file=conf_file,
            bin_env=bin_env,
            state_ret=ret
        )

        ret.update(_check_error(result, comment))
        changes.append(comment)
        log.debug(comment)

    elif update:
        comment = 'Updating supervisor'
        result = __salt__['supervisord.update'](
            user=user,
            conf_file=conf_file,
            bin_env=bin_env,
            state_ret=ret
        )
        ret.update(_check_error(result, comment))
        changes.append(comment)
        log.debug(comment)

        if '{0}: updated'.format(name) in result:
            just_updated = True

    # check state
    is_stopped = True
    is_starting = None
    process_type = None
    if name in process_groups:
        process_type = 'group'

        # check if any processes in this group are stopped
        for proc in all_processes:
            if proc.startswith(name):
                if all_processes[proc]['state'].upper() == 'RUNNING':
                    is_stopped = False
                elif all_processes[proc]['state'].upper() == 'STARTING':
                    is_starting = True
                break

    elif name in all_processes:
        process_type = 'service'

        if all_processes[name]['state'].upper() == 'RUNNING':
            is_stopped = False
        elif all_processes[name]['state'].upper() == 'STARTING':
            is_starting = True

    if is_supervisord < 0:
        if is_starting:
            ret['result'] = True
            comment = "Service {0} is starting".format(name)
            ret.update({'comment': comment})
            # remove group flag
            if ':' in name:
                name = name[:name.index(':')]
            ret['changes'][name] = comment
            return ret

    if is_stopped is False:
        if restart and not just_updated:
            comment = 'Restarting{0}: {1}'.format(
                process_type is not None and ' {0}'.format(process_type) or '',
                name
            )
            log.debug(comment)

            # group process
            if process_type == 'group':
                name = '{0}:*'.format(name)

            result = __salt__['supervisord.restart'](
                name,
                user=user,
                conf_file=conf_file,
                bin_env=bin_env,
                state_ret=ret
            )
            ret.update(_check_error(result, comment))
            changes.append(comment)
        elif just_updated:
            comment = 'Not starting updated{0}: {1}'.format(
                process_type is not None and ' {0}'.format(process_type) or '',
                name
            )
            result = comment
            ret.update({'comment': comment})
        else:
            comment = 'Not starting already running{0}: {1}'.format(
                process_type is not None and ' {0}'.format(process_type) or '',
                name
            )
            result = comment
            ret.update({'comment': comment})

    elif not just_updated:
        comment = 'Starting{0}: {1}'.format(
            process_type is not None and ' {0}'.format(process_type) or '',
            name
        )
        changes.append(comment)
        log.debug(comment)

        # group process
        if process_type == 'group':
            name = '{0}:*'.format(name)

        result = __salt__['supervisord.start'](
            name,
            user=runas,
            conf_file=conf_file,
            bin_env=bin_env,
            state_ret=ret
        )

        ret.update(_check_error(result, comment))
        log.debug(unicode(result))

    if ret['result'] and len(changes):
        # remove group flag
        if ':' in name:
            name = name[:name.index(':')]
        ret['changes'][name] = ' '.join(changes)
    return ret


def dead(name,
         user=None,
         runas=None,
         conf_file=None,
         bin_env=None):
    '''
    Ensure the named service is dead (not running).

    name
        Service name as defined in the supervisor configuration file

    runas
        Name of the user to run the supervisorctl command

        .. deprecated:: 0.17.0

    user
        Name of the user to run the supervisorctl command

        .. versionadded:: 0.17.0

    conf_file
        path to supervisorctl config file

    bin_env
        path to supervisorctl bin or path to virtualenv with supervisor
        installed

    '''
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}, 'state_stdout': ''}

    salt.utils.warn_until(
        'Hydrogen',
        'Please remove \'runas\' support at this stage. \'user\' support was '
        'added in 0.17.0',
        _dont_call_warnings=True
    )
    if runas:
        # Warn users about the deprecation
        ret.setdefault('warnings', []).append(
            'The \'runas\' argument is being deprecated in favor of \'user\', '
            'please update your state files.'
        )
    if user is not None and runas is not None:
        # user wins over runas but let warn about the deprecation.
        ret.setdefault('warnings', []).append(
            'Passed both the \'runas\' and \'user\' arguments. Please don\'t. '
            '\'runas\' is being ignored in favor of \'user\'.'
        )
        runas = None
    elif runas is not None:
        # Support old runas usage
        user = runas
        runas = None

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = (
            'Service {0} is set to be stopped'.format(name))
    else:
        comment = 'Stopping service: {0}'.format(name)
        log.debug(comment)

        all_processes = __salt__['supervisord.status'](
            user=runas,
            conf_file=conf_file,
            bin_env=bin_env
        )

        # parse process groups
        process_groups = []
        for proc in all_processes:
            if ':' in proc:
                process_groups.append(proc[:proc.index(':') + 1])
        process_groups = list(set(process_groups))

        is_stopped = None

        if name in process_groups:
            # check if any processes in this group are stopped
            is_stopped = False
            for proc in all_processes:
                if proc.startswith(name) \
                        and _is_stopped_state(all_processes[proc]['state']):
                    is_stopped = True
                    break

        elif name in all_processes:
            if _is_stopped_state(all_processes[name]['state']):
                is_stopped = True
            else:
                is_stopped = False
        else:
            # process name doesn't exist
            ret['comment'] = "Service {0} doesn't exist".format(name)

        if is_stopped is True:
            ret['comment'] = "Service {0} is not running".format(name)
        else:
            result = {name: __salt__['supervisord.stop'](
                name,
                user=user,
                conf_file=conf_file,
                bin_env=bin_env,
                state_ret=ret
            )}
            ret.update(_check_error(result, comment))
            log.debug(unicode(result))
    return ret


def mod_watch(name,
              restart=True,
              update=False,
              user=None,
              runas=None,
              conf_file=None,
              bin_env=None):
    # Always restart on watch
    return running(
        name,
        restart=restart,
        update=update,
        user=user,
        runas=runas,
        conf_file=conf_file,
        bin_env=bin_env
    )

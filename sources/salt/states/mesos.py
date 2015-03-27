# -*- coding: utf-8 -*-
'''
Run a Mesos Instance

@author: Thibault BRONCHAIN
(c) 2014-2015 - MadeiraCloud
'''

import os

from salt.states import service
from opsagent.checksum import Checksum

WATCH_PATH="/var/lib/visualops/opsagent/watch"


# Result object template
def _result(name="",changes={},result=False,comment="",stdout=''):
    return {'name': name,
            'changes': changes,
            'result': result,
            'comment': comment,
            'state_stdout': stdout}
# Valid result object
def _valid(name="",changes={},comment="",stdout=''):
    return _result(name=name,changes=changes,result=True,comment=comment,stdout=stdout)
# Invalid result object
def _invalid(name="",changes={},comment="",stdout=''):
    return _result(name=name,changes=changes,result=False,comment=comment,stdout=stdout)



# ensure host is present
def host_present(name, ip):
    if __salt__['hosts.has_pair'](ip, name):
        return ""
    current_ip = __salt__['hosts.get_ip'](name)
    if current_ip and current_ip != ip:
        __salt__['hosts.rm_host'](current_ip, name)
    if __salt__['hosts.add_host'](ip, name):
        return 'Added host {0}'.format(name)
    return ""

# set hosts
def set_hosts(hosts):
    return "\n".join([ host_present(item.get("value",item["key"]),item["key"]) for item in hosts ])

# set a file
def set_file(name, content, mode):
    if os.path.isdir(name):
        return False, 'Specified target {0} is a directory'.format(name)
    ret = __salt__['file.manage_file'](name,None,None,None,None,'root','root',mode,__env__,None,contents=content)
    return ret["result"], "%s"%ret.get("comment","")

# run a command
def run_cmd(cmd, if_absent):
    if os.path.exists(if_absent):
        return _valid()
    act = __salt__['cmd.run_stdall']
    try:
        ret = act(cmd)
    except Exception as e:
        result = False
        comment = "failed to run command: %s"%cmd
        ret['stderr'] = "%s"%e
    else:
        result = (True if ret['retcode'] == 0 else False)
        comment = ("" if result else "failed to run command: %s"%cmd)
    return _result(result=result,
                   comment=comment,
                   stdout="%s"%(ret['stderr'] if ret.get('stderr') else ret.get('stdout','')))

# Run/restart service
def run_service(name, watch_list, state_id):
    comment = ""
    ret = service.running(name,enable=True)
    if not ret.get("result"):
        comment += "Unable to run service %s"%name
        return False,comment
    comment += "Service %s: %s\n"%(name,ret.get("comment","Available"))
    for watch in watch_list:
        cs = Checksum(watch,state_id,WATCH_PATH)
        if cs.update(edit=False,tfirst=True):
            ret = service.mod_watch(name)
            if not ret.get("result"):
                comment += "Unable to restart service %s after change triggered on file %s"%(name,watch)
                return False,comment
            comment += "Service %s: %s\n"%(name,ret.get("comment","Restarted"))
            cs.update(edit=True,tfirst=True)
            return True,comment




# Create Mesos Master
def master(name, cluster_name, server_id, masters_addresses, master_ip, hostname=None, framework=None):
    if not hostname:
        hostname = master_ip
    if not framework:
        framework = []
    return _valid(comment=name)


# Create Mesos Slave
def slave(name, masters_addresses, attributes, slave_ip):
    comment = set_hosts(masters_addresses)
    attributes_line = ";".join([ "%s:%s"%(item["key"],item.get("value","")) for item in attributes ])
    return _valid(comment=name)

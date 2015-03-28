# -*- coding: utf-8 -*-
'''
Run a Mesos Instance

@author: Thibault BRONCHAIN
(c) 2014-2015 - MadeiraCloud
'''

import os
import re
import urllib2

from salt.states import service
service.__salt__ = __salt__
from opsagent.checksum import Checksum

WATCH_PATH="/var/lib/visualops/opsagent/watch"
AZ_URI="http://169.254.169.254/latest/meta-data/placement/availability-zone"


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


# Get data
def get_cloud_data(url):
    req = urllib2.Request(url)
    f = urllib2.urlopen(req, timeout=2)
    res = f.read()
    if re.search('404 - Not Found', res):
        return None
    return res

# Get availability zone (if available)
def get_az():
    try:
        az = get_cloud_data(AZ_URI)
    except Exception:
        return None
    return az

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
def set_files(files):
    comment = ""
    res = True
    for f in files:
        name = f.get("name")
        content = f.get("content","")
        if not name: continue
        mode = f.get("mode","0644")
        if os.path.isdir(name):
            comment += 'Specified target {0} is a directory'.format(name)
            res = False
        ret = __salt__['file.manage_file'](name,'',None,None,None,'root','root',mode,__env__,None,contents="%s"%content)
        res = ret["result"]
        comment += "%s"%ret.get("comment","")
        if not res:
            break
    return res,comment

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
    if not watch_list: watch_list = []
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
    gl_comment = set_hosts(masters_addresses)

    # Zookeeper conf
    zcfg = "tickTime=2000\ninitLimit=10\nsyncLimit=5\ndataDir=/var/lib/zookeeper\nclientPort=2181\n"
    me_zk = "zk://"
    ma_zk = "zk://"
    i = 1
    for item in masters_addresses:
        zcfg += "server.%s=%s:2888:3888\n"%(i,item["key"])
        if i > 1:
            me_zk += ","
            ma_zk += ","
        me_zk += "%s:2181"%(item["key"])
        ma_zk += "%s:2181"%(item.get("value",item["key"]))
        i += 1

    # set files
    res,comment = set_files([{
        "name":"/var/lib/zookeeper/myid",
        "content":server_id,
    },{
        "name":"/etc/zookeeper/conf/zoo.cfg",
        "content":zcfg,
    },{
        "name":"/etc/mesos/zk",
        "content":me_zk+"/mesos",
    },{
        "name":"/etc/mesos-master/quorum",
        "content":(i/2)+1,
    },{
        "name":"/etc/mesos-master/ip",
        "content":master_ip,
    },{
        "name":"/etc/mesos-master/hostname",
        "content":hostname,
    },{
        "name":"/etc/mesos-master/cluster",
        "content":cluster_name,
    },{
        "name":"/etc/marathon/conf/hostname",
        "content":hostname,
    },{
        "name":"/etc/marathon/conf/master",
        "content":ma_zk+"/mesos",
    },{
        "name":"/etc/marathon/conf/zk",
        "content":ma_zk+"/marathon",
    },{
        "name":"/etc/hostname",
        "content":hostname,
    },{
        "name":"/etc/init/mesos-slave.override",
        "content":"manual",
    },{
        "name":"/etc/init/chronos.override",
        "content":"manual",
    }])
    gl_comment += comment
    if not res: return _invalid(comment=gl_comment)

    res, comment = run_service("zookeeper", [
        "/var/lib/zookeeper/myid",
        "/etc/zookeeper/conf/zoo.cfg",
    ], name)
    gl_comment += comment
    if not res: return _invalid(comment=gl_comment)

    res, comment = run_service("mesos-master", [
        "/etc/mesos/zk",
        "/etc/mesos-master/quorum",
        "/etc/mesos-master/ip",
        "/etc/mesos-master/hostname",
        "/etc/mesos-master/cluster",
    ], name)
    gl_comment += comment
    if not res: return _invalid(comment=gl_comment)

    if "marathon" in framework:
        res, comment = run_service("marathon", [
            "/etc/marathon/conf/hostname",
            "/etc/marathon/conf/master",
            "/etc/marathon/conf/zk",
        ], name)
        gl_comment += comment
        if not res: return _invalid(comment=gl_comment)

    return _valid(comment=gl_comment)


# Create Mesos Slave
def slave(name, masters_addresses, attributes, slave_ip):
    if not attributes:
        attributes = {}
        az = get_az()
        if az:
            attributes.append({"key":"az","value":az})
    attributes_line = ";".join([ "%s:%s"%(item["key"],item.get("value","")) for item in attributes ])
    gl_comment = set_hosts(masters_addresses)

    # set files
    ma_cfg = ""
    me_zk = "zk://"
    i = 1
    for item in masters_addresses:
        ma_cfg += "%s:8080\n"%(item.get("value",item["key"]))
        if i > 1:
            me_zk += ","
        me_zk += "%s:2181"%(item["key"])
        i += 1

    # HA proxy
    res,comment = set_files([{
        "name":"/etc/haproxy-marathon-bridge/marathons",
        "content":ma_cfg,
    }])
    gl_comment += comment
    if not res: return _invalid(comment=gl_comment)
    ret = run_cmd(
        "/usr/local/bin/haproxy-marathon-bridge install_cronjob && touch /etc/haproxy-marathon-bridge/setup",
        "/etc/haproxy-marathon-bridge/setup"
    )
    gl_comment += ret.get("comment","")
    if not ret.get("result"): return _invalid(comment=gl_comment)
    res, comment = run_service("haproxy", None, name)
    gl_comment += comment
    if not res: return _invalid(comment=gl_comment)

    # Mesos
    # set files
    res,comment = set_files([{
        "name":"/etc/mesos/zk",
        "content":me_zk+"/mesos",
    },{
        "name":"/etc/mesos-slave/ip",
        "content":slave_ip,
    },{
        "name":"/etc/mesos-slave/hostname",
        "content":slave_ip,
    },{
        "name":"/etc/mesos-slave/containerizers",
        "content":"docker,mesos",
    },{
        "name":"/etc/mesos-slave/executor_registration_timeout",
        "content":"5mins",
    },{
        "name":"/etc/mesos-slave/attributes",
        "content":attributes_line,
    },{
        "name":"/etc/init/mesos-master.override",
        "content":"manual",
    },{
        "name":"/etc/init/zookeeper.override",
        "content":"manual",
    },{
        "name":"/etc/init/chronos.override",
        "content":"manual",
    }])
    gl_comment += comment
    if not res: return _invalid(comment=gl_comment)

    res, comment = run_service("mesos-slave", [
        "/etc/mesos/zk",
        "/etc/mesos-slave/ip",
        "/etc/mesos-master/hostname",
        "/etc/mesos-master/containerizers",
        "/etc/mesos-master/executor_registration_timeout",
        "/etc/mesos-master/attributes",
    ], name)
    gl_comment += comment
    if not res: return _invalid(comment=gl_comment)

    return _valid(comment=gl_comment)

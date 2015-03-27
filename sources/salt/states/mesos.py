# -*- coding: utf-8 -*-
'''
Run a Mesos Instance

@author: Thibault BRONCHAIN
(c) 2014-2015 - MadeiraCloud
'''

import os

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
        return 'Added host {0}\n'.format(name)
    return ""

# set hosts
def set_hosts(hosts):
    return "".join([ host_present(item.get("value",item["key"]),item["key"]) for item in hosts ])

# set a file
def set_file(name, content, mode):
    if os.path.isdir(name):
        return False, 'Specified target {0} is a directory\n'.format(name)
    ret = __salt__['file.manage_file'](name,None,None,None,None,'root','root',mode,__env__,None,contents=content)
    return ret["result"], "%s\n"%ret.get("comment","")

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





























# TODO: delete
# Apply recipe manifest
def apply(manifests, arguments=[]):
    if not manifests:
        return _invalid(comment="No file specified")
    comment = ""
    out = ""
    for manifest in manifests:
        ags = ["apply",manifest]
        for a in arguments:
            if ("key" not in a) or ("value" not in a): continue
            ags.append("%s=%s"%(a["key"],a["value"]))
            try:
                ret = __salt__['puppet.run'](*ags)
            except Exception as e:
                comment += "Error processing file %s.\n"%(manifest)
                return _invalid(name=manifest,
                                comment=comment)
            else:
                out += "%s\n"%ret["stdout"]
                out += "%s\n"%ret["stderr"]
    if ret.get("retcode"):
        comment += "Manifest %s processed with error(s) (code %s).\n"%(manifest,ret["retcode"])
        return _invalid(name=manifest,
                        comment=comment,
                        stdout=out)
    else:
        comment += "Manifest %s processed without error.\n"%(manifest)
    return _valid(name=manifest,
                  comment=comment,
                  stdout=out)


# make filesystem
def mkfs(device, fstype="ext4", label=None, block_size=None):
    extfs=["ext2","ext3","ext4"]
    xfs=["xfs"]
    if not device:
        return {'name': device,
                'changes': {},
                'result': False,
                'comment': 'No device specified',
                'state_stdout': ''}
    if (fstype not in extfs) and (fstype not in xfs):
        return {'name': device,
                'changes': {},
                'result': False,
                'comment': 'Wrong fstype: "%s"'%(fstype),
                'state_stdout': ''}

    act = __salt__['cmd.retcode']
    status = act("blkid | grep -i '^%s:' | grep -i 'TYPE=\"%s\"'"%(device,fstype))
    if status == 0:
        return {'name': device,
                'changes': {},
                'result': True,
                'comment': 'Device is %s already a %s partitions.'%(device,fstype),
                'state_stdout': ''}

    opts = ("-L %s"%label if label else "")
    if fstype in extfs:
        if block_size:
            opts += " -b %s"%label
        cmd = 'mke2fs -F -t {0} {1} {2}'.format(fstype, opts, device)
    elif fstype in xfs:
        if block_size:
            opts += " -b size=%s"%label
        cmd = 'mkfs.xfs -f {0} {1}'.format(opts, device)

    act = __salt__['cmd.run_stdall']
    try:
        ret = act(cmd)
    except Exception as e:
        return {'name': device,
                'changes': {},
                'result': False,
                'comment': 'Error creating file system',
                'state_stdout': "%s"%e}

    result = (True if ret['retcode'] == 0 else False)
    comment = ("Device %s formated (type=%s)"%(device,fstype) if result else "Error while formating %s (type=%s)"%(device,fstype))
    # TODO: changes
    return {'name': device,
            'changes': {},
            'result': result,
            'comment': comment,
            'state_stdout': "%s"%(ret['stderr'] if ret.get('stderr') else ret.get('stdout',''))}

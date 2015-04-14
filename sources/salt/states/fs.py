# -*- coding: utf-8 -*-
'''
Create filesystems

@author: Thibault BRONCHAIN
(c) 2014 - MadeiraCloud
'''


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

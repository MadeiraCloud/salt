# -*- coding: utf-8 -*-

"""
Archive states.
"""

import logging
import os

# Import salt libs
import salt.utils

log = logging.getLogger(__name__)


def extracted(name,
              source,
              archive_format,
              tar_options=None,
              source_hash=None,
              if_missing=None,
              if_absent=None):
    '''
    State that make sure an archive is extracted in a directory.
    The downloaded archive is erased if succesfully extracted.
    The archive is downloaded only if necessary.

    .. code-block:: yaml

        graylog2-server:
          archive:
            - extracted
            - name: /opt/
            - source: https://github.com/downloads/Graylog2/graylog2-server/graylog2-server-0.9.6p1.tar.gz
            - source_hash: md5=499ae16dcae71eeb7c3a30c75ea7a1a6
            - archive_format: tar
            - tar_options: z
            - if_missing: /opt/graylog2-server-0.9.6p1/

    name
        Directory name where to extract the archive

    source
        Archive source, same syntax as file.managed source argument.

    archive_format
        tar, zip or rar

    if_missing
        Some archive, such as tar, extract themself in a subfolder.
        This directive can be used to validate if the archive had been
        previously extracted.

    if_absent
        Extract the archive only if none of the specified paths exist.

    tar_options
        Only used for tar format, it need to be the tar argument specific to
        this archive, such as 'j' for bzip2, 'z' for gzip, '' for uncompressed
        tar, 'J' for LZMA.
    '''
    ret = {'name': name, 'result': None, 'changes': {}, 'comment': ''}
    valid_archives = ('tar', 'rar', 'zip')

    if archive_format not in valid_archives:
        ret['result'] = False
        ret['comment'] = '{0} is not supported, valids: {1}'.format(
            name, ','.join(valid_archives))
        return ret

    if archive_format == 'tar' and tar_options is None:
        ret['result'] = False
        ret['comment'] = 'tar archive need argument tar_options'
        return ret

    if if_missing is None:
        if_missing = name
    # if (__salt__['file.directory_exists'](if_missing) or
    #     __salt__['file.file_exists'](if_missing)):
    #     ret['result'] = True
    #     ret['comment'] = '{0} already exists'.format(if_missing)
    #     return ret

    log.debug("Input seem valid so far")
    filename = os.path.join(__opts__['cachedir'],
                            '{0}.{1}'.format(if_missing.replace('/', '_'),
                                             archive_format))

    #########################################################################
    re_fetched = False
    sfn = None
    ## check whether special paths are absent
    if if_absent and isinstance(if_absent, list):
        re_fetched = all( [ os.path.isdir(path) for path in if_absent ] )

    ## get source hash file
    if source_hash:
        try:
            tmp, source_hash, comment_ = __salt__['file.get_managed'](filename,
                None, source, source_hash, None, None, None, __env__, None, None)
            if comment_:
                ret['result'] = False
                ret['comment'] = comment_
                return ret
        except Exception, e:
            ret['result'] = False
            ret['comment'] = 'Parse source hash %s failed' % str(source_hash)
            ret['state_stdout'] = str(e)
            return ret

    ## check source_hash
    if not re_fetched:
        ## check cached file
        sfn = __salt__['cp.is_cached'](source, __env__)

        if source_hash and os.path.isfile(sfn):
            hash_value = '{0}={1}'.format(source_hash['hash_type'], source_hash['hsum']).lower()
            re_fetched = not __salt__['file.check_hash'](sfn, hash_value)

            # the same hash code and existed target directory
            if not re_fetched and __salt__['file.directory_exists'](name):
                ret['result'] = True
                ret['comment'] = ('Any special path is existed or file sum set for file {0} of {1} is unchanged.'
                    ).format(filename, source_hash['hsum'])
                return ret

        else:
            re_fetched = True

    ## fetch the source file
    if re_fetched:
        try:
            sfn = __salt__['cp.cache_file'](source, __env__)
        except Exception, e:
            ret['result'] = False
            ret['comment'] = 'Download source file %s failed.' % source
            ret['state_stdout'] = str(e)
            return ret

    # check source hash
    if source_hash:
        try:
            hash_value = '{0}={1}'.format(source_hash['hash_type'], source_hash['hsum']).lower()
            if not __salt__['file.check_hash'](sfn, hash_value):
                dl_sum = __salt__['file.get_hash'](sfn, source_hash['hash_type'])
                if sfn:
                    __salt__['file.remove'](sfn)
                ret['result'] = False
                ret['comment'] = ('File sum set for file {0} of {1} does '
                                    'not match real sum of {2}'
                                    ).format(sfn,
                                            source_hash['hsum'],
                                            dl_sum)
                return ret
        except Exception, e:
            ret['result'] = False
            ret['comment'] = 'Check file sum set for file %s exception.' % sfn
            ret['state_stdout'] = str(e)
            return ret

    ## prepare tmp file
    try:
        salt.utils.copyfile(sfn,
                            filename,
                            __salt__['config.backup_mode'](''),
                            __opts__['cachedir'])
    except IOError:
        ret['result'] = False
        ret['comment'] = 'Failed to commit change, permission error'
        return ret

    if not os.path.isfile(filename):
        ret['result'] = False
        ret['comment'] = 'Source file {0} not found'.format(source)
        return ret
    ########################################################################################

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Archive {0} would have been extracted in {1}'.format(
            source, name)
        return ret

    try:
        __salt__['file.makedirs'](name)
        # check dir
        if not os.path.isdir(name):
            # remove cached file
            if sfn:
                __salt__['file.remove'](sfn)
            ret['result'] = False
            ret['comment'] = 'Make directory {0} failed.'.format(name)
            return ret

        if archive_format in ('zip', 'rar'):
            log.debug("Extract %s in %s", filename, name)
            files = __salt__['archive.un{0}'.format(archive_format)](filename, name)
        else:
            # this is needed until merging PR 2651
            log.debug("Untar %s in %s", filename, name)
            results = __salt__['cmd.run_all']('tar -xv{0}f {1}'.format(tar_options,filename),cwd=name)
            if results['retcode'] != 0:
                ret['result'] = False
                ret['comment'] = 'Extract file %s failed' % filename
                ret['state_stdout'] = results['stderr']
                return results
            files = results['stdout']
        if len(files) > 0:
            ret['result'] = True
            ret['changes']['directories_created'] = [name]
            if if_missing != name:
                ret['changes']['directories_created'].append(if_missing)
            ret['changes']['extracted_files'] = files
            ret['comment'] = "{0} extracted in {1}".format(source, name)
            os.unlink(filename)
        else:
            __salt__['file.remove'](if_missing)
            ret['result'] = False
            ret['comment'] = "Can't extract content of {0}".format(source)
        return ret
    except Exception, e:
        ret['result'] = False
        ret['comment'] = 'Extract file {0} to directory {1} failed'.format(filename, name)
        ret['state_stdout'] = str(e)
        return ret

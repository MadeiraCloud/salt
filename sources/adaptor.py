'''
Madeira OpsAgent states adaptor

@author: Michael (michael@mc2.io)
'''


# System imports
import os

# Internal imports
from opsagent.exception import StateException
from opsagent import utils

class StateAdaptor(object):

	ssh_key_type = ['ssh-rsa', 'ecdsa', 'ssh-dss']
	supported_os = ['centos', 'redhat', 'debian', 'ubuntu', 'amazon']

	mod_map = {
		## package
		'linux.apt.package'	: {
			'attributes' : {
				'name'			: 'pkgs',
				'repo'			: 'fromrepo',
				'deb conf file'	: 'debconf',
				'verify gpg'	: 'verify_gpg',
			},
			'states' : [
				'installed', 'latest', 'removed', 'purged'
			],
			'type'	: 'pkg',
		},
		'linux.yum.package'	: {
			'attributes' : {
				'name'			: 'pkgs',
				'repo'			: 'fromrepo',
				# 'enablerepo'	: 'enablerepo',
				# 'disablerepo'	: 'disablerepo',
				'verify gpg'	: 'verify_gpg',
			},
			'states' : [
				'installed', 'latest', 'removed', 'purged'
			],
			'type'	: 'pkg',
		},
		'common.gem.package'	: {
			'attributes' : {
				'name'	: 'names',
			},
			'states' : [
				'installed', 'removed'
			],
			'type'	: 'gem',
			'require'	: {
				'linux.apt.package' : { 'name' : ['rubygems'] },
				'linux.yum.package' : { 'name' : ['rubygems'] }
			},
		},
		'common.npm.package'	: {
			'attributes' : {
				'name'		: 'names',
				#'path'		: '',
				#'index_url' : '',
			},
			'states' : [
				'installed', 'removed', 'bootstrap'
			],
			'type'	: 'npm',
			'require'	: {
				'linux.apt.package' : { 'name' : ['npm'] },
				'linux.yum.package' : { 'name' : ['npm'] }
			}
		},
		# 'common.pecl.package'	: {
		# 	'attributes' : {
		# 		'name' : 'names'
		# 	},
		# 	'states' : [
		# 		'installed', 'removed'
		# 	],
		# 	'type'	: 'pecl',
		# 	'require'	: {
		# 		'linux.apt.package' : { 'name' : ['php-pear'] },
		# 	}
		# },
		'common.pip.package'	: {
			'attributes' : {
				'name' : 'names'
			},
			'states' : [
				'installed', 'removed'
			],
			'type'	: 'pip',
			'require' : {
				'linux.apt.package' : { 'name' : ['python-pip'] },
				'linux.yum.package' : { 'name' : ['python-pip'] }
			}
		},

		## repo
		'linux.apt.repo'	: {
			'attributes' : {
				'name' 		: 'name',
				'content' 	: 'contents'
			},
			'states' : [
				'managed'
			],
			'type' : 'file',
		},
		'linux.yum.repo' : {
			'attributes' : {
				'name' 		: 'name',
				'content' 	: 'contents'
			},
			'states' : [
				'managed'
			],
			'type' : 'file',
			'require_in' : {
				'linux.cmd' : {
					'yum-config-manager --enable $name' : 'name'
				}
			}
		},
		'common.gem.source' : {
			'attributes' : {
				'url' : 'name'
			},
			'state' : [
				'run'
			],
			'type' : 'cmd'
		},

		## scm
		'common.git' : {
			'attributes' : {
				'path'		: 'target',
				'repo'		: 'name',
				# 'branch'	: 'branch',
				'revision'	: 'rev',
				'ssh key'	: 'identity',
				# 'user'		: 'user',
				'force'		: 'force',
			},
			'states' : [
				'latest', 'present',
			],
			'type' : 'git',
			'require' : {
				'linux.apt.package' : { 'name' : ['git'] },
				'linux.yum.package' : { 'name' : ['git'] }
			},
			# 'require_in' : {
			# 	'linux.dir' : {
			# 		'path' 	: 'name',
			# 		'user' 	: 'user',
			# 		'group' : 'group',
			# 		'mode' 	: 'mode',
			# 	}
			# }
		},
		'common.svn' : {
			'attributes' : {
				'path'		: 'target',
				'repo'		: 'name',
				# 'branch'	: 'branch',
				'revision'	: 'rev',
				'username'	: 'username',
				'password'	: 'password',
				# 'user'		: 'user',
				'force'		: 'force',
			},
			'states' : [
				'latest', 'export'
			],
			'type' : 'svn',
			'require' : {
				'linux.apt.package' : { 'name' : ['subversion'] },
				'linux.yum.package' : { 'name' : ['subversion'] }
			},
			# 'require_in' : {
			# 	'linux.dir' : {
			# 		'path' 	: 'name',
			# 		'user' 	: 'user',
			# 		'group' : 'group',
			# 		'mode' 	: 'mode'
			# 	}
			# },
		},
		'common.hg' : {
			'attributes' : {
				'repo'		: 'name',
				'branch'	: 'branch',
				'revision'	: 'rev',
				# 'ssh key'	: '',
				'path'		: 'target',
				# 'user'		: 'user',
				'force'		: 'force',
			},
			'states' : [
				'latest'
			],
			'type' : 'hg',
			'require' : {
				'linux.apt.package' : { 'name' : ['mercurial'] },
				'linux.yum.package' : { 'name' : ['mercurial'] }
			},
			# 'require_in' : {
			# 	'linux.dir' : {
			# 		'path' 	: 'name',
			# 		'user' 	: 'user',
			# 		'group' : 'group',
			# 		'mode' 	: 'mode'
			# 	}
			# },
		},

		## path
		'linux.dir' : {
			'attributes' : {
				'path' 		: 'name',
				'user' 		: 'user',
				'group' 	: 'group',
				'mode' 		: 'mode',
				'recursive' : 'recurse',
				'absent' 	: 'absent',
			},
			'states' : [
				'directory', 'absent'
			],
			'type' : 'file'
		},
		'linux.file' : {
			'attributes' : {
				'path' 		: 'name',
				'user' 		: 'user',
				'group' 	: 'group',
				'mode' 		: 'mode',
				'content' 	: 'contents',
				'absent'	: 'absent',
			},
			'states' : [
				'managed', 'absent'
			],
			'type' : 'file'
		},
		'linux.symlink' : {
			'attributes' : {
				'source' : 'name',
				'target' : 'target',
				'user'	 : 'user',
				'group'	 : 'group',
				'mode'	 : 'mode',
				'absent' : 'absent'
			},
			'states' : [
				'symlink', 'absent'
			],
			'type' : 'file'
		},

		## service
		'linux.supervisord' : {
			'attributes' : {
				'name'	:	'name',
				'config':	'conf_file',
				#'watch'	:	'',
			},
			'states' : ['running'],
			'type' : 'supervisord',
			'require' : {
				'common.pip.package' : {
					'name' : {
						'supervisor' : ''
					}
				}
			}
		},
		'linux.service' : {
			'attributes' : {
				'name' : 'names',
				# 'watch' : ''
			},
			'states' : ['running'],
			'type' : 'service',
		},
		# 'linux.systemd' : {
		# 	'attributes' : {
		# 		'name' : 'names',
		# 		# 'watch' : ''
		# 	},
		# 	'states' : ['running'],
		# 	'type' : 'service',
		# },
		# 'linux.sysvinit' : {
		# 	'attributes' : {
		# 		'name' : 'name',
		# 		# 'watch' : ''
		# 	},
		# 	'states' : ['running'],
		# 	'type' : 'service',
		# },
		# 'linux.upstart' : {
		# 	'attributes' : {
		# 		'name' : 'name',
		# 		# 'watch' : 'watch',
		# 	},
		# 	'states' : ['running'],
		# 	'type' : 'service',
		# },

		## cmd
		'linux.cmd' : {
			'attributes' : {
				'bin'			: 'shell',
				'cmd'			: 'name',
				'cwd'			: 'cwd',
				'user'			: 'user',
				'group'			: 'group',
				'timeout'		: 'timeout',
				'env'			: 'env',
				'if path present'	: 'onlyif',
				'if path absent'	: 'unless',
			},
			'states' : [
				'run', 'call', 'wait', 'script'
			],
			'type' : 'cmd',
		},

		## cron
		'linux.cron' : {
			'attributes' : {
				'minute'		:	'minute',
				'hour'			:	'hour',
				'day of month'	:	'daymonth',
				'month'			:	'month',
				'day of week'	:	'dayweek',
				'user'			:	'user',
				'cmd'			:	'name'
			},
			'states' : [
				'present', 'absent'
			],
			'type' : 'cron',
		},

		## user
		'linux.user' : {
			'attributes' : {
				'username'	: 'name',
				'password'	: 'password',
				'fullname'	: 'fullname',
				'uid'		: 'uid',
				'gid'		: 'gid',
				'shell'		: 'shell',
				'home'		: 'home',
				'nologin'	: 'nologin',
				'groups'	: 'groups',
			},
			'states' : [ 'present', 'absent' ],
			'type' : 'user'
		},

		## group
		'linux.group' : {
			'attributes' : {
				'groupname' : 'name',
				'gid' 		: 'gid',
				'system' 	: 'system'
			},
			'states' : ['present', 'absent'],
			'type' : 'group'
		},

		## hostname

		## hosts
		# 'linux.hosts' : {
		# 	'attributes' : {
		# 		'content' : 'contents'
		# 	},
		# 	'states' : ['managed'],
		# 	'type' : 'file',
		# },

		## mount
		'linux.mount' : {
			'attributes' : {
				'path'		:	'name',
				'device'	:	'device',
				'filesystem':	'fstype',
				'dump'		:	'dump',
				'passno'	:	'pass_num',
				'opts'		:	'opts'
			},
			'states' : ['mounted', 'unmounted'],
			'type' : 'mount'
		},

		## selinux
		'linux.selinux' : {
			'attributes' : {
			},
			'states' : ['boolean', 'mode'],
			'type' : 'selinux',
			'linux.yum.package' : {
				'name' : ['libsemanage', 'setools-console', 'policycoreutils-python']
			}
		},

		## timezone
		'common.timezone' : {
			'attributes' : {
				'name' : 'name',
				'use utc' : 'utc'
			},
			'states' : ['system'],
			'type' : 'timezone'
		},

		## lvm
		'linux.lvm.pv'	: {
			'attributes' : {
				'path'					: 'names',
				'force'					: 'force',
				'uuid'					: 'uuid',
				'zero'					: 'zero',
				'data alignment'		: 'dataalignment',
				'data alignment offset'	: 'dataalignmentoffset',
				'metadata size'			: 'metadatasize',
				'metadata type'			: 'metadatatype',
				'metadata copies'		: 'metadatacopies',
				'metadata ignore'		: 'metadataignore',
				'restorefile'			: 'restorefile',
				'norestorefile'			: 'norestorefile',
				'label sector'			: 'labelsector',
				'PV size'				: 'setphysicalvolumesize',
			},
			'states' : ['pv_present'],
			'type' : 'lvm'
		},
		'linux.lvm.vg'	: {
			'attributes' : {
				'name'				: 'name',
				'path' 				: 'devices',
				'clustered'			: 'clustered',
				'max LV number'		: 'maxlogicalvolumes',
				'max PV number'		: 'maxphysicalvolumes',
				'metadata type'		: 'metadatatype',
				'metadata copies'	: 'metadatacopies',
				'PE size'			: 'physicalextentsize',
				'autobackup'		: 'autobackup',
				'tag'				: 'addtag',
				'allocation policy'	: 'alloc',
			},
			'states' : ['vg_present', 'vg_absent'],
			'type' : 'lvm'
		},
		'linux.lvm.lv'	: {
			'attributes'	: {
				'name'				: 'name',
				'VG name'			: 'vgname',
				'path'				: 'pv',
				'chunk size'		: 'chunksize',
				'contiguous'		: 'contiguous',
				# 'discards'			: 'discards',
				'stripe number'		: 'stripes',
				'stripe size'		: 'stripesize',
				'LE number'			: 'extents',
				'LV size'			: 'size',
				'minor number'		: 'minor',
				'persistent'		: 'persistent',
				'mirror number'		: 'mirrors',
				'no udev sync'		: 'noudevsync',
				'monitor'			: 'monitor',
				'ignore monitoring' : 'ignoremonitoring',
				'permission' 		: 'permission',
				# 'pool metadata size': 'poolmetadatasize',
				'region size'		: 'regionsize',
				'readahead'			: 'readahead',
				# 'thinpool'			: 'thinpool',
				'type'				: 'type',
				'virtual size'		: 'virtualsize',
				'zero'				: 'zero',
				'available'			: 'available',
				'snapshot'			: 'snapshot',
				'autobackup'		: 'autobackup',
				'tag'				: 'addtag',
				'allocation policy'	: 'alloc',
			},
			'states' : ['lv_present', 'lv_absent'],
			'type' : 'lvm',
		},

		## virtual env
		'common.virtualenv' : {
			'attributes' : {
				'path'					: 'name',
				'python'				: 'python',
				'system site packages'	: 'system_site_packages',
				# 'always-copy'			: '',
				# 'unzip setuptools'		: '',
				# 'no setuptools'			: '',
				# 'no pip'				: '',
				'extra search dir'		: 'extra-search-dir',
				# always copy				: '',
				'requirements'			: 'requirements',
			},
			'states' : ['managed'],
			'type' : 'virtualenv',
			'require' : {
				'common.pip.package' : {
					'name' : {
						'virtualenv' : ''
					}
				}
			}
		},

		## ssh
		'common.ssh.auth' : {
			'attributes' : {
				'authname'	:	'name',
				'username'	:	'user',
				'filename'	:	'config',
				'content'	:	'content',
				'encrypt_algorithm' : 'enc',
			},
			'states' : ['present', 'absent'],
			'type' : 'ssh_auth'
		},

		'common.ssh.known_host' : {
			'attributes' : {
				'hostname'	:	'name',
				'username'	:	'user',
				'filename'	:	'config',
				'fingerprint'		: 'fingerprint',
				'encrypt_algorithm'	: 'enc',
			},
			'states' : ['present', 'absent'],
			'type' : 'ssh_known_hosts'
		},
	}

	def __init__(self):

		self.states = None

	def convert(self, step, module, parameter, os_type):
		"""
			convert the module json data to salt states.
		"""

		utils.log("INFO", "Begin to convert module json data ...", ("convert", self))

		if not isinstance(module, basestring):	raise StateException("Invalid input parameter: %s, %s" % (module, parameter))
		if not isinstance(parameter, dict):		raise StateException("Invalid input parameter: %s, %s" % (module, parameter))
		if module not in self.mod_map:			raise StateException("Unsupported module %s" % module)
		if not os_type or not isinstance(os_type, basestring) or os_type not in self.supported_os:
			raise	StateException("Invalid input parameter: %s" % os_type)

		# distro check and package manger check
		if (os_type in ['centos', 'redhat', 'debian'] and module in ['linux.apt.package', 'linux.apt.repo']) \
			or (os_type in ['debian', 'ubuntu'] and module in ['linux.yum.package', 'linux.yum.repo']):
			raise StateException("Cnflict on os type %s and module %s" % (os_type, module))

		# filter unhandler module
		if module in ['meta.comment']:
			return None

		# get agent package module
		self.__agent_pkg_module = 'linux.apt.package' if os_type in ['debian', 'ubuntu'] else 'linux.yum.package'

		# convert from unicode to string
		utils.log("INFO", "Begin to convert unicode parameter to string ...", ("convert", self))
		parameter = utils.uni2str(parameter)

		# convert to salt states
		try:
			utils.log("INFO", "Begin to convert to salt state...", ("convert", self))
			self.states = self.__salt(step, module, parameter)

			# expand salt state
			utils.log("INFO", "Begin to expand salt state...", ("convert", self))
			self.__expand()
		except StateException, e:
			import json
			utils.log("ERROR", "Generate salt states of id %s, module %s, parameter %s, os type %s exception: %s" % \
				(step, module, json.dumps(parameter), os_type, str(e)), ("convert", self))
			return None
		except Exception, e:
			utils.log("ERROR", "Generate salt states exception: %s." % str(e), ("convert", self))
			return None

		return self.states

	def __salt(self, step, module, parameter):
		salt_state = {}

		utils.log("DEBUG", "Begin to generate addin of step %s, module %s..." % (step, module), ("__salt", self))
		addin = self.__init_addin(module, parameter)

		utils.log("DEBUG", "Begin to build up of step %s, module %s..." % (step, module), ("__salt", self))
		module_states = self.__build_up(module, addin)

		try:
			for state, addin in module_states.iteritems():
				# add require
				utils.log("DEBUG", "Begin to generate requirity ...", ("_convert", self))
				require = []
				if 'require' in self.mod_map[module]:
					req_state = self.__get_require(self.mod_map[module]['require'])
					if req_state:
						for req_tag, req_value in req_state.iteritems():
							salt_state[req_tag] = req_value
							require.append({ next(iter(req_value)) : req_tag })

				# add require in
				utils.log("DEBUG", "Begin to generate require-in ...", ("_convert", self))
				require_in = []
				if 'require_in' in self.mod_map[module]:
					req_in_state = self.__get_require_in(self.mod_map[module]['require_in'], parameter)
					if req_in_state:
						for req_in_tag, req_in_value in req_in_state.iteritems():
							salt_state[req_in_tag] = req_in_value
							require_in.append({ next(iter(req_in_value)) : req_in_tag })

				## add watch, todo
				utils.log("DEBUG", "Begin to generate watch ...",("_convert", self))
				watch = []
				# if 'watch' in parameter and isinstance(parameter['watch'], list):
				# 	watch_state = self.__add_watch(parameter['watch'], step)
				# 	if watch_state:
				# 		for watch_tag, watch_value in watch_state.iteritems():
				# 			salt_state[watch_tag] = watch_value
				# 			watch.append({file:watch_tag})

				# build up module state
				module_state = [
					state,
					addin
				]

				if require:		module_state.append({ 'require' : require })
				if require_in:	module_state.append({ 'require_in' : require_in })
				if watch:		module_state.append({ 'watch' : watch })

				# tag
				#name = addin['names'] if 'names' in addin else addin['name']
				tag = self.__get_tag(module, None, step, None, state)
				utils.log("DEBUG", "Generated tag is %s" % tag, ("_convert", self))
				salt_state[tag] = {
					self.mod_map[module]['type'] : module_state
				}

				# add env and sls
				if 'require_in' in self.mod_map[module]:
					salt_state[tag]['__env__'] = 'base'
					salt_state[tag]['__sls__'] = 'madeira'
		except Exception, e:
			utils.log("DEBUG", "Generate salt states of id %s module %s exception:%s" % (step, module, str(e)), ("__salt", self))
			raise StateException("Generate salt states exception")

		if not salt_state:	raise StateException("conver state failed: %s %s" % (module, parameter))
		return salt_state

	def __init_addin(self, module, parameter):
		addin = {}

		try:
			for attr, value in parameter.iteritems():
				if value is None:	continue

				if attr in self.mod_map[module]['attributes'].keys():
					key = self.mod_map[module]['attributes'][attr]
					if isinstance(value, dict):
						addin[key] = [k if not v else {k:v} for k, v in value.iteritems()]
					else:
						addin[key] = value
		except Exception, e:
			utils.log("DEBUG", "Init module %s addin exception: %s" % (module, str(e)))
			raise StateException(str(e))

		if not addin:	raise StateException("No addin founded: %s, %s" % (module, parameter), ("__init_addin", self))
		return addin

	def __build_up(self, module, addin):
		default_state = self.mod_map[module]['states'][0]
		module_state = {
			default_state : addin
		}

		try:
			if module in ['linux.apt.package', 'linux.yum.package']:
				module_state = {}

				for item in addin['pkgs']:
					pkg_name = None
					pkg_state = None
					if isinstance(item, dict):
						for k, v in item.iteritems():
							pkg_name 	= k
							pkg_state 	= default_state

							if v in self.mod_map[module]['states']:
								pkg_state = v

							if pkg_state not in module_state:			module_state[pkg_state] = {}
							if 'pkgs' not in module_state[pkg_state]:	module_state[pkg_state]['pkgs'] = []

							if pkg_state == default_state:
								module_state[pkg_state]['pkgs'].append(item)
							else:
								module_state[pkg_state]['pkgs'].append(pkg_name)

					else:	# insert into default state
						pkg_state	= default_state

						if pkg_state not in module_state:			module_state[pkg_state] = {}
						if 'pkgs' not in module_state[pkg_state]:	module_state[pkg_state]['pkgs'] = []

						module_state[pkg_state]['pkgs'].append(item)

			elif module in ['common.npm.package', 'common.pip.package', 'common.gem.package']:
				module_state = {}

				for item in addin['names']:
					pkg_name = None
					pkg_state = None

					if isinstance(item, basestring):	# insert into default state
						pkg_state	= default_state

						if pkg_state not in module_state:			module_state[pkg_state] = {}
						if 'names' not in module_state[pkg_state]:	module_state[pkg_state]['names'] = []

						module_state[pkg_state]['names'].append(item)

					elif isinstance(item, dict):
						for k, v in item.iteritems():
							pkg_name 	= k
							pkg_state 	= default_state

							if v in self.mod_map[module]['states']:		pkg_state = v
							if pkg_state not in module_state:			module_state[pkg_state] = {}
							if 'names' not in module_state[pkg_state]:	module_state[pkg_state]['names'] = []

							if pkg_state == default_state:
								if module == 'common.npm.package':
									module_state[pkg_state]['names'].append(
										'{0}@{1}'.format(k, v)
										)
								elif module in ['common.pip.package', 'common.gem.package']:
									module_state[pkg_state]['names'].append(
									'{0}=={1}'.format(k, v)
									)
							else:
								module_state[pkg_state]['names'].append(pkg_name)

					else:	# invalid
						continue

			elif module in ['common.git', 'common.svn', 'common.hg']:
				# if 'name' in addin:
				# 	module_state[default_state]['name'] = addin['name'].split('-')[1].strip()

				# svn target path(remove the last prefix)
				if 'target' in addin and addin['target'][len(addin['target'])-1] == '/':
					addin['target'] = os.path.split(addin['target'])[0]

				# set revision
				if 'branch' in addin:
					if module in ['common.git', 'common.hg']:
						addin['rev'] = addin['branch']
					addin.pop('branch')

				#
				if module == 'common.git' and 'force' in addin and addin['force']:
					addin['force_checkout'] = True

			elif module in ['linux.apt.repo', 'linux.yum.repo']:
				if 'name' in addin:
					filename = addin['name']
					obj_dir =  None

					if module == 'linux.apt.repo':
						obj_dir = '/etc/apt/sources.list.d/'
						if not filename.endswith('.list'):
							filename += '.list'
					elif module == 'linux.yum.repo':
						obj_dir = '/etc/yum.repos.d/'
						if not filename.endswith('repo'):
							filename += '.repo'

					if filename and obj_dir:
						addin['name'] = obj_dir + filename

			elif module in ['common.gem.source']:
				addin.update(
					{
						'name'	: 'gem source --add ' + addin['name'],
						'shell'	: '/bin/bash',
						'user'	: 'root',
						'group'	: 'root',
					}
				)

			elif module in ['common.ssh.auth', 'common.ssh.known_host']:
				auth = []

				if 'enc' in addin and addin['enc'] not in self.ssh_key_type:
					addin['enc'] = self.ssh_key_type[0]

				if module == 'common.ssh.auth' and 'content' in addin:
					for line in addin['content'].split('\n'):
						if not line: continue

						auth.append(line)

					addin['names'] = auth

					# remove name attribute
					addin.pop('name')

			elif module in ['linux.dir', 'linux.file', 'linux.symlink']:
				if module == 'linux.dir':
					addin['makedirs'] = True

				# set absent
				if 'absent' in addin and addin['absent']:
					module_state = {}
					module_state['absent'] = {
						'name' : addin['name']
					}

				else:
					# set mode
					if 'mode' in addin and addin['mode']:
						addin['mode'] = int(addin['mode'])

					# set recurse
					if 'recurse' in addin and addin['recurse']:
						addin['recurse'] = []
						if 'user' in addin and addin['user']:
							addin['recurse'].append('user')
						if 'group' in addin and addin['group']:
							addin['recurse'].append('group')
						if 'mode' in addin and addin['mode']:
							addin['recurse'].append('mode')

					# set user
					if 'user' not in addin:
						addin['user'] = 'root'

			elif module in ['linux.cmd']:
				if 'onlyif' in addin:
					addin['onlyif'] = "[ -d " + addin['onlyif'] + " ]"

				if 'unless' in addin:
					addin['unless'] = "[ -d " + addin['unless'] + " ]"

				if 'timeout' in addin:
					addin['timeout'] = int(addin['timeout'])

			elif module in ['linux.group', 'linux.user']:
				if 'gid' in addin and addin['gid']:
					addin['gid'] = int(addin['gid'])
				if 'uid' in addin and addin['uid']:
					addin['uid'] = int(addin['uid'])

				# set nologin shell
				if 'nologin' in addin and addin['nologin']:
					addin['shell'] = '/sbin/nologin'
					addin.pop('nologin')

			elif module in ['linux.mount']:
				for attr in ['dump', 'pass_num']:
					if attr in addin:
						try:
							addin[attr] = int(addin[attr])
						except Exception:
							addin[attr] = 0

			# elif module in ['linux.hosts']:

			# 	module_state[default_state] = {
			# 		'name' 		: '/etc/hosts',
			# 		'user' 		: 'root',
			# 		'group' 	: 'root',
			# 		'mode' 		: '0644',
			# 		'contents' 	: addin['contents']
			# 	}

			elif module in ['linux.lvm.vg', 'linux.lvm.lv']:
				if 'devices' in addin and isinstance(addin['devices'], list):
					addin['devices'] = ','.join(addin['devices'])
				if 'pv' in addin and isinstance(addin['pv'], list):
					addin['pv'] = ','.join(addin['pv'])
		except Exception, e:
			utils.log("DEBUG", "Build up module %s exception: %s" % (module, str(e)), ("__build_up", self))

		if not module_state:	raise StateException("Build up module state failed: %s" % module)
		return module_state

	def __expand(self):
		"""
			Expand state's requirity and require-in when special module(gem).
		"""
		if not self.states:
			utils.log("DEBUG", "No states to expand and return...", ("__expand", self))
			raise StateException("No states to expand and return")

		state_list = []

		try:
			for tag, state in self.states.iteritems():
				for module, chunk in state.iteritems():

					if module == 'gem':
						name_list = None
						for item in chunk:
							if isinstance(item, dict) and 'names' in item:	name_list = item['names']

						if not name_list:	continue
						for name in name_list:
							if '==' in name:
								the_build_up = [ i for i in chunk if 'names' not in i ]

								# remove the name from origin
								name_list.remove(name)

								pkg_name, pkg_version = name.split('==')

								the_build_up.append({
									"name" 		: pkg_name,
									"version"	: pkg_version
								})

								# build up the special package state
								the_state = {
									tag + '_' + name : {
										"gem" : the_build_up
									}
								}

								# get the state's require and require-in
								req_list = [ item[next(iter(item))] for item in chunk if isinstance(item, dict) and any(['require' in item, 'require_in' in item]) ]

								for req in req_list:
									if isinstance(req, list):
										for r in req:
											for r_tag in r.values():
												if r_tag in self.states:
													the_state[r_tag] = self.states[r_tag]

								if the_state:
									state_list.append(the_state)
		except Exception, e:
			utils.log("DEBUG", "Expand states exception: %s" % str(e), ("__expand", self))
			raise StateException(str(e))

		state_list.append(self.states)
		self.states = state_list

	def __get_tag(self, module, uid=None, step=None, name=None, state=None):
		"""
			generate state identify tag.
		"""
		tag = module.replace('.', '_')
		if step:	tag = step + '_' + tag
		if uid:		tag = uid + '_' + tag
		if name:	tag += '_' + name
		if state:	tag += '_' + state
		return '_' + tag

	def __get_require(self, require):
		"""
			Generate require state.
		"""

		require_state = {}

		try:
			for module, parameter in require.items():
				if module not in self.mod_map.keys():	continue

				# filter not current platform's package module
				if module in ['linux.apt.package', 'linux.yum.package'] and module != self.__agent_pkg_module:	continue

				the_require_state = self.__salt('require', module, parameter)

				if the_require_state:
					require_state.update(the_require_state)
		except Exception, e:
			utils.log("DEBUG", "Generate salt requisities exception: %s" % str(e), ("__get_require", self))
			raise StateException(str(e))

		return require_state

	def __get_require_in(self, require_in, parameter):
		"""
			Generate require in state.
		"""

		require_in_state = {}

		try:
			for module, attrs in require_in.iteritems():

				# filter not current platform's package module
				if module in ['linux.apt.package', 'linux.yum.package'] and module != self.__agent_pkg_module:	continue

				req_addin = {}
				for k, v in attrs.iteritems():
					if not v:	continue

					if k in parameter:
						req_addin[v] = parameter[k]
					elif k.find('$')>=0:
						str_list = k.split()
						for idx, w in enumerate(str_list):
							if w.startswith('$'):
								str_list[idx] = parameter[w[1:]]

						req_addin[v] = ' '.join(str_list)

				if req_addin:
					state = self.mod_map[module]['states'][0]
					stype = self.mod_map[module]['type']

					tag = self.__get_tag(module, None, None, 'require_in', state)

					require_in_state[tag] = {
						stype : [
							state,
							req_addin
						]
					}
		except Exception, e:
			utils.log("DEBUG", "Generate salt require in exception: %s" % str(e), ("__get_require_in", self))
			raise StateException(str(e))

		return require_in_state

	def __add_watch(self, watch, step):
		"""
			Generate watch state.
		"""
		if not watch or not isinstance(watch, list):
			raise StateException("Invalid watch format %s" % str(watch))

		watch_state = {}

		try:
			for f in watch:
				watch_module = 'path.dir' if os.path.isdir(file) else 'path.file'
				state = 'directory' if watch_module == 'path.dir' else 'managed'

				watch_tag = self.__get_tag(watch_module, None, step, f, state)

				watch_state[watch_tag] = {
					'file' : [
						state,
						{
							'name' : f
						},
					]
				}
		except Exception, e:
			utils.log("DEBUG", "Add watch %s exception: %s" % ('|'.join(watch), str(e)), ("__add_watch", self))
			raise StateException(str(e))

		return watch_state

	# def __check_module(self, module):
	# 	"""
	# 		Check format of module.
	# 	"""

	# 	module_map = {
	# 		'package'		: ['pkg', 'apt', 'yum', 'gem', 'npm', 'pecl', 'pip'],
	# 		'repo'			: ['apt', 'yum', 'zypper'],
	# 		'source'		: ['gem'],
	# 		'path'			: ['file', 'dir', 'symlink'],
	# 		'scm' 			: ['git', 'svn', 'hg'],
	# 		'service'		: ['supervisord', 'sysvinit', 'upstart'],
	# 		'sys'			: ['cmd', 'cron', 'group', 'host', 'mount', 'ntp', 'selinux', 'user', 'timezone'],
	# 		'system'		: ['ssh_auth', 'ssh_known_host']
	# 	}

	# 	m_list = module.split('.')

	# 	if len(m_list) <= 1:
	# 		print "invalib module format"
	# 		return 1

	# 	p_module = m_list[0]
	# 	s_module = m_list[1]

	# 	if m_list[0] == 'package':
	# 		p_module = m_list[2]

	# 	elif m_list[0] == 'system':
	# 		s_module = module.split('.', 1)[1].replace('.', '_')

	# 	if p_module not in module_map.keys() or s_module not in module_map[p_module]:
	# 		print "not supported module: %s, %s" % (p_module, s_module)
	# 		return 2

	# 	return 0

	# def __check_state(self, module, state):
	# 	"""
	# 		Check supported state.
	# 	"""

	# 	if state not in self.mod_map[module]['states']:
	# 		print "not supported state %s in module %s" % (state, module)
	# 		return 1

	# 	return 0

# ===================== UT =====================
def ut():
	import json
	pre_states = json.loads(open('/opt/madeira/bootstrap/salt/tests/state.json').read())

	# salt_opts = {
	# 	'file_client':       'local',
	# 	'renderer':          'yaml_jinja',
	# 	'failhard':          False,
	# 	'state_top':         'salt://top.sls',
	# 	'nodegroups':        {},
	# 	'file_roots':        {'base': ['/srv/salt']},
	# 	'state_auto_order':  False,
	# 	'extension_modules': '/var/cache/salt/minion/extmods',
	# 	'id':                '',
	# 	'pillar_roots':      '',
	# 	'cachedir':          '/code/OpsAgent/cache',
	# 	'test':              False,
	# }

	config = {
		'srv_root' : '/srv/salt',
		'extension_modules' : '/var/cache/salt/minion/extmods',
		'cachedir' : '/code/OpsAgent/cache'
	}

	from opsagent.state.runner import StateRunner
	adaptor = StateAdaptor()
	runner = StateRunner(config)

	# print json.dumps(adaptor._salt_opts, sort_keys=True,
	# 	indent=4, separators=(',', ': '))

	err_log = None
	out_log = None
	for uid, com in pre_states['component'].iteritems():
		states = {}

		for p_state in com['state']:
			step = p_state['id']
			states = adaptor.convert(step, p_state['module'], p_state['parameter'], runner.os_type)
			print json.dumps(states)

			if not states or not isinstance(states, list):
				err_log = "convert salt state failed"
				print err_log
				result = (False, err_log, out_log)
			else:
				result = runner.exec_salt(states)
			print result

	# out_states = [salt_opts] + states
	# with open('states.json', 'w') as f:
	# 	json.dump(out_states, f)

if __name__ == '__main__':
	ut()

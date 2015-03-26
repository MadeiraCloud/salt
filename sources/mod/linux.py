linux = {
	'linux'		:	{
		# apt packages
		'apt pkg'	:	{
			'module'	:	'linux.apt.package',
			'distro'	:	['debian', 'ubuntu'],
			'reference'	:	{
				'en'	:	'''
### Description
manage apt packages

### Parameters

*   *`name`** (*required*): the package names and versions. You can specify multiple pakages. The following values can be used for package version:
	- ***`<null>`*** *`default`*: ensure the package is installed. If not, it will install the latest version available of all APT repos activated
	- ***`<version>`***: ensure the package is installed, at the version specified. If the version in unavailable of all APT repos activated on the host, the state will fail
	- **`<uri>`**: ensure the package will be fetched from the following uri. Warning: if one uri is specified, only packages with uri specified will be installed. *uri* can be a remote or local path to a rpm package.
	- **`latest`**: ensure the package is installed at the latest version. If a newer version is available of all APT repos activated on the host, the package will upgrade automatically
	- **`removed`**: ensure the package is absent
	- **`purged`**: ensure the package is absent, and also delete all related configuration data of the package


* **`repo`** (*optional*): the repo name, which you want to use to install the packages

		example: main

* **`deb-conf-file`** (*optional*): the Deb configuration file path

		example: /etc/apt/deb.conf

* **`verify-gpg`** (*optional*): verify the package's GPG signature, by default ***`true`***
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'name'	:	{
					'type'	:	'dict',
					'option'	:	['latest', 'removed', 'purged'],	# autofill options to show in IDE
					'default'	:	'',			# the default value to show in IDE,
					'required'	:	True,
					'visible'	:	True
				},
				'repo'	:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'deb-conf-file'	:	{
					'type'		:	'line',
					'required'	:	False
				},
				'verify-gpg':	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False
				}
			}
		},

		# apt repo
		'apt repo'	:	{
			'module'	:	'linux.apt.repo',
			'distro'	:	['debian', 'ubuntu'],
			'reference'	:	{
				'en'	:	'''
### Description
manage apt repo

### Parameters

*   **`name`** (*required*): the repository name (`/etc/apt/sources.list.d/$name.list` will be created)

* **`content`** (*required*): the source list file content

		example: deb http://www.rabbitmq.com/debian/ testing main
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'name'		:	{
					'type'	:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'content'	:	{
					'type'	:	'text',
					'required'	:	True
				}
			}
		},

		# apt ppa repo
		'apt ppa'	:	{
			'module'	:	'linux.apt.ppa',
			'distro'	:	['debian', 'ubuntu'],
			'reference'	:	{
				'en'	:	'''
### Description
manage apt ppa

### Parameters

*   **`name`** (*required*): the ppa user/acrhive name, please don't add `ppa:`

		example: chromium-daily/stable

* **`username`** (*optional*): the ppa account's username, for auth only

* **`password`** (*optional*): the ppa account's password, for auth only
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'name'		:	{
					'type'	:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'username'	:	{
					'type'		:	'line',
					'required'	:	False,
				},
				'password'	:	{
					'type'		:	'line',
					'required'	:	False,
				}
			}
		},

		# yum packages
		'yum pkg'	:	{
			'module'	:	'linux.yum.package',
			'distro'	:	['amazon', 'redhat', 'centos'],
			'reference'	:	{
				'en'	:	'''
### Description
manage yum packages

### Parameters

*	**`name`** (*required*): the package names and versions. You can specify multiple pakages. The following values can be used for package version:
	- ***`<null>`*** *`default`*: ensure the package is installed. If not, it will install the latest version available of all YUM repos available
	- ***`<version>`***: ensure the package is installed, at the version specified. If the version in unavailable of all YUM repos available on the host, the state will fail
	- **`<uri>`**: ensure the package will be fetched from the following uri. Warning: if one uri is specified, only packages with uri specified will be installed. *uri* can be a remote or local path to a rpm package.
	- **`latest`**: ensure the package is installed at the latest version. If a newer version is available of all YUM repos available on the host, will do upgrade automatically
	- **`removed`**: ensure the package is absent
	- **`purged`**: ensure the package is absent, and also delete all related configuration data of the package

* **`repo`** (*optional*): the repo name, which you want to use for installing the packages

		example: epel

* **`verify-gpg`** (*optional*): verify the package's GPG siganature, by default ***`true`***
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'name'	:	{
					'type'	:	'dict',
					'value'		:	['latest', 'removed'],	# values to show in IDE
					'default'	:	'',			# the default value of the item
					'required'	:	True,
					'visible'	:	True
				},
				'repo'		:	{
					'type'		:	'line',
					'required'	:	False
				},
				'verify-gpg'	:	{
					'type'		:	'bool',
					'default'	:	True,
					'required'	:	False
				}
			}
		},

		# yum repo
		'yum repo'	:	{
			'module'	:	'linux.yum.repo',
			'distro'	:	['amazon', 'redhat', 'centos'],
			'reference'	:	{
				'en'	:	'''
### Description
manage a yum repo

### Parameters

* **`name`** (*required*): the repo name

		 example: epel

* **`content`** (*optional*): the content of the repo configuration file

		example:
			[10gen]
			name=10gen Repository
			baseurl=http://downloads-distro.mongodb.org/repo/redhat/os/i686
			gpgcheck=0
			enabled=1

* **`rpm-url`** (*optional*): the repo rpm url (if no content specified)

		example: http://mirrors.hustunique.com/epel/6/i386/epel-release-6-8.noarch.rpm
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'name'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'content'	:	{
					'type'		:	'text',
					'required'	:	False,
				},
				'rpm-url'	:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				}
			}
		},

		# rpm key
		'rpm key'	:	{
			'module'	:	'linux.rpm.key',
			'distro'	:	['amazon', 'redhat', 'centos'],
			'reference'	:	{
				'en'	:	'''
### Description
manage a rpm key

### Parameters

* **`path`** (*required*): the location of the key

		example: /path/to/YOUR-RPM-GPG-KEY
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'path'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				}
			}
		},

		# zyppyer packages
#			'zypper package'	:	{
#				'module'	:	'linux.zypper.package',
#				'distro'	:	['opensuse', 'suse'],
#				'reference'	:	{
#					'en'	:	'''
#### Description
#	manage zypper packages
#
#### Parameters
#
#*   **name** (*required*): the package names and versions. You can specify multiple pakages. The following values can be used for package version:
#	- <***empty***> (*default*): ensure the package is installed. If not, will install the latest version available of all APT repos on
#	- <***version***>: ensure the package is installed, at the version specified. If the version in unavailable of all APT repos on the host, the state will fail
#	- **latest**: ensure the package is installed at the latest version. If a newer version is available of all APT repos on the host, will do a auto-upgrade
#	- **removed**: ensure the package is absent
#	- **purged**: ensure the package is absent, and also delete all related configuration data of the package
#
#
#* **from-repo** (*optional*): an repo name, which you want to use for installing the packages
#		epel
#
#* **verify-gpg** (*optional*): verify the package's GPG siganature, by default ***`true`***
#					''',
#					'cn'	:	''''''
#				},
#				'parameter'	:	{
#					'name'	:	{
#						'type'	:	'dict',
#						'value'		:	['latest', 'removed'],	# values to show in IDE
#						'default'	:	'',			# the default value of the item
#						'required'	:	True
#					},
#					'from-repo'		:	{
#						'type'		:	'line',
#						'required'	:	False
#					},
#					'verify-gpg'	:	{
#						'type'		:	'bool',
#						'default'	:	True,
#						'required'	:	False
#					}
#				}
#			},
#			'zypper repo'	:	{
#				'module'	:	'linux.zypper.repo',
#				'distro'	:	['opensuse', 'suse'],
#				'reference'	:	{
#					'en'	:	'''
#### Description
#	manage zypper repo
#
#### Parameters
#
#*   **name** (*required*): the repo name
#		   packman
#
#
#* **url** (*required*): the repo url
#		http://ftp.gwdg.de/pub/linux/packman/suse/13.1/
#					''',
#					'cn'	:	''''''
#				},
#				'parameter'	:	{
#					'name'		:	{
#						'type'		:	'line',
#						'required'	:	True
#					},
#					'url'	:	{
#						'type'		:	'line',
#						'required'	:	True
#					}
#				}
#			},

		# directory
		'dir'	:	{
			'module'	:	'linux.dir',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage a directory

### Parameters

*   **`path`** (*required*): a list of directory paths

		example: /var/www/html

	>note: This state ensures the specifed directory is present with correposnding attributes. If the parent directory is present, its attributes will be left unchanged, otherwise it will be created with the same attributes as the specified directory itself.

* **`user`** (*optional*): the user name of the directory owner

		example: root

	>note: If specified, the directory owner will be set to this user. Otherwise, the result depends on whether the directory exists or not. If existed, the directory owner will be left unchanged, otherwise default: root

* **`group`** (*optional*): the group name of the directory owner

		example: root

    >note: If specified, the directory will be set to this group. Otherwise, the result depends on whether the directory exists or not. If existed, the directory group will be left unchanged; otherwise default: root

* **`mode`** (*optional*): the directory mode

		example: 0755

	>note: If specified, the directory will be set to this mode. Otherwise, the result depends on whether the directory exists or not. If existed, the directory mode will be left unchanged

* **`recursive`** (*optional*): whehther to recursively set attributes of all sub-directories under *path*, by default ***`true`***

* **`absent`** (*optional*): ensure all directories are absent, by default ***`false`***

	>note: If True, all other parameters are ignored
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'path'		:	{
					'type'		:	'array',
					'required'	:	True
				},
				'user'	:	{
					'type'		:	'line',
					'required'	:	False
				},
				'group'	:	{
					'type'		:	'line',
					'required'	:	False
				},
				'mode':	{
					'type'		:	'line',
					'default'	:	'0755',
					'required'	:	False
				},
				'recursive'	:	{
					'type'		:	'bool',
					'default'	:	True,
					'required'	:	False
				},
				'absent'	:	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False
				}
			}
		},

		# file
		'file'	:	{
			'module'	:	'linux.file',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage a file

### Parameters

*   **`path`** (*required*): the file path

		example: /root/.ssh/known_hosts

	>note: This state ensures the specifed file is present with correposnding attributes and content. If the file is present, its attributes will be left unchanged, otherwise it will be created with the same attributed of the specified file itself.

* **`user`** (*optional*): the user name of the file owner

		example: root

	>note: If specified, the file owner will be set to this user. Otherwise, the result depends on whether the file exists or not. If existed, the file owner will be left unchanged, otherwise default: root

* **`group`** (*optional*): the group name of the file owner

		example: root

	>note: If specified, the file will be set to this group. Otherwise, the result depends on whether the file exists or not. If existed, the file group will be left unchanged; otherwise default: root

* **`mode`** (*optional*): the file mode

		example: 0644

	>note: If specified, the file will be set to this mode. Otherwise, the result depends on whether the file exists or not. If existed, the file mode will be left unchanged

* **`content`** (*optional*): the file content

	>note: If the specified file exists and its MD5 does not match with `content`'s, the file will be overwritten

* **`remote_uri`** (*optional*): path where to get the content of the file (will overwrite the *content* parameter)

	>note: http, https and ftp protocols are supported

	>note: `Links` - @{...} - in files provided using a remote URI won't be rendered.

* **`absent`** (*optional*): ensure the file is absent, by default ***`false`***

	>note: If True, all other parameters are ignored
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'path'	:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'user'	:	{
					'type'		:	'line',
					'required'	:	False,
				},
				'group'	:	{
					'type'		:	'line',
					'required'	:	False
				},
				'mode':	{
					'type'		:	'line',
					'default'	:	'0644',
					'required'	:	False
				},
				'content'	:	{
					'type'		:	'text',
					'required'	:	False
				},
				'remote_uri'	:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				#'source-url'	:	{
				#	'type'		:	'line',
				#	'required'	:	False
				#},
				#'source-checksum'	:	{
				#	'type'		:	'line',
				#	'required'	:	False
				#},
				'absent'	:	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False,
					'visible'	:	True,
				}
			}
		},

		# symlink
		'symlink'	:	{
			'module'	:	'linux.symlink',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage a symbolic link

### Parameters

*   **`source`** (*required*): the path to link to

		example: /data/

* **`target`** (*required*): the path of the symlink

		example: /mnt/data

	>note: If the target's parent path does not exist, this state will fail.

* **`user`** (*optional*): the user name of the link owner

		example: root

	>note: If specified, the link owner will be set to this user. Otherwise, the result depends on whether the link exists or not. If existed, the link owner will be left unchanged, otherwise default: root

* **`group`** (*optional*): the group name of the link owner

		example: root

	>note: If specified, the link will be set to this group. Otherwise, the result depends on whether the link exists or not. If existed, the link group will be left unchanged; otherwise default: root

* **`mode`** (*optional*): the link mode

		example: 0777

	>note: If specified, the link will be set to this mode. Otherwise, the result depends on whether the link exists or not. If existed, the link mode will be left unchanged, otherwise default: 0777

* **`absent`** (*optional*): ensure the link is absent, by default ***`false`***

	>note: If True, all other parameters are ignored
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'source'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True,
				},
				'target'	:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'user'	:	{
					'type'		:	'line',
					'required'	:	False,
				},
				'group'	:	{
					'type'		:	'line',
					'required'	:	False
				},
				# 'mode':	{
				# 	'type'		:	'line',
				# 	'default'	:	'0777',
				# 	'required'	:	False
				# },
				'absent'	:	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False,
					'visible'	:	True
				}
			}
		},

		# abstraction of SysV, systemd, upstart
		'service'	:	{
			'module'	:	'linux.service',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
ensure the specified services are running, and trigger service restart if necessary

### Parameters

*   **`name`** (*required*): the list of the service names to be run. The value represents the action if one of the watched file has changed (if applicable):

	- ***`<null>`*** *`default`*: try to reload the service. If reload fails, restart the service.
	- ***`<command>`***: path to a command to execute
	- ***`reload`***: 'reload' the service
	- ***`restart`***: 'restart' the service


		example: httpd: bash /opt/scripts/nginx_mysql_restart.sh, mysqld: restart


*   **`watch`** (*optional*): watch a list of files, execute action if any of them is modified

		example: /etc/nginx/nginx.conf, /etc/my.cnf
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'name'		:	{
					'type'		:	'dict',
					'required'	:	True,
					'visible'	:	True
				},
				'watch'		:	{
					'type'		:	'array',
					'required'	:	False,
					'visible'	:	True
				}
			}
		},

		# supervisord
		'supervisord'	:	{
			'module'	:	'linux.supervisord',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
ensure supervisord and the specified services are running, and trigger supervisord to restart the services if necessary

### Parameters

*   **`config`** (*required*): the path of supervisord configuration file

		example: /etc/supervisord.conf

		>note: When this file is modified, supervisord will be restarted, which causes all managed services to be restarted

*   **`name`** (*required*): the name list of the services to be running (see below)

		example: httpd, mysqld

*   **`watch`** (*optional*): watch a list of files, restart the service if any of them is modified

		example: /etc/nginx/nginx.conf
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'name'		:	{
					'type'		:	'array',
					'required'	:	True,
					'visible'	:	True,
				},
				'watch'		:	{
					'type'		:	'array',
					'required'	:	False,
					'visible'	:	True
				},
				'config'	:	{
					'type'		:	'line',
					'required'	:	True
				}
			}
		},

		# cron
		'cronjob'	:	{
			'module'	:	'linux.cronjob',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage a cron job

### Parameters

*   **`user`** (*required*): the user to execute the cron job, by default: root

*   **`cmd`** (*required*): a list of command

		example:
			cat /proc/meminfo >> /tmp/meminfo
			ntpdate  time.apple.com

*   **`minute`** (*optional*): 0 - 59

*   **`hour`** (*optional*): 0 - 23 (must be a valid day if a month is specified)

*   **`day-of-month`** (*optional*): 1 - 31

*   **`month`** (*optional*): 1 - 12

*   **`day-of-week`** (*optional*): 0 - 7, sunday is represented by 0 or 7, monday by 1
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'minute'	:	{
					'type'		:	'line',
					'option'	:	['*'],
					'required'	:	False
				},
				'hour'	:	{
					'type'		:	'line',
					'option'	:	['*'],
					'required'	:	False
				},
				'day-of-month'	:	{
					'type'		:	'line',
					'option'	:	['*'],
					'required'	:	False
				},
				'month'	:	{
					'type'		:	'line',
					'option'	:	['*'],
					'required'	:	False
				},
				'day-of-week'	:	{
					'type'		:	'line',
					'option'	:	['*'],
					'required'	:	False
				},
				'user'	:	{
					'type'		:	'line',
					'default'	:	'root',
					'required'	:	True,
					'visible'	:	True
				},
				'cmd'	:	{
					'type'		:	'array',
					'required'	:	True,
					'visible'	:	True
				}
			}
		},

#			'crontab'	:	{
#				'module'	:	'linux.crontab',
#				'distro'	:	None,
#				'reference'	:	{
#					'en'	:	'''
#### Description
#	manage a crontab file
#
#### Parameters
#
#*   **user** (*required*): the user to execute the cron job, by default: ***root***
#
#*   **content** (*required*): a list of command
#		example:
#			cat /proc/meminfo >> /tmp/meminfo
#			ntpdate  time.apple.com
#					''',
#					'cn'	:	''''''
#				},
#				'parameter'	:	{
#					'user'	:	{
#						'type'		:	'line',
#						'default'	:	'root',
#						'required'	:	True,
#						'visible'	:	True
#					},
#					'content'	:	{
#						'type'		:	'text',
#						'required'	:	True,
#						'visible'	:	True
#					}
#				}
#			},
#			'hosts'	:	{
#				'module'	:	'linux.hosts',
#				'distro'	:	None,
#				'reference'	:	{
#					'en'	:	'''
#### Description
#	manage /etc/hosts
#
#### Parameters
#
#*   **ip** (*required*): the IP address
#
#*   **hostnames** (*required*): a list of hostnames
#		example:
#			web, web.example.com
#					''',
#					'cn'	:	''''''
#				},
#				'parameter'	:	{
#					'ip'	:	{
#						'type'		:	'line',
#						'required'	:	True
#					},
#					'hostnames'	:	{
#						'type'		:	'array',
#						'required'	:	True
#					},
#				}
#			},
#			'hostname'	:	{
#				'module'	:	'linux.hostname',
#				'distro'	:	None,
#				'reference'	:	{
#					'en'	:	'''
#### Description
#	manage hostname
#
#### Parameters
#
#*   **hostname** (*required*): the hostname
#					''',
#					'cn'	:	''''''
#				},
#				'parameter'	:	{
#					'hostname'	:	{
#						'type'		:	'line',
#						'required'	:	True,
#						'visible'	:	True
#					}
#				}
#			},
		'mount'	:	{
			'module'	:	'linux.mount',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage mount points

### Parameters

*   **`path`** (*required*): the path of the mount point

*   **`device`** (*required*): the device name

*   **`filesystem`** (*required*): the file system type of the device

*   **`fstab`** (*optional*): whether to save in /etc/fstab or not, by default ***`false`***

*   **`opts`** (*optional*): a list of options for /etc/fstab, see *`fstab(8)`*

	>note: this parameter applies only if `fstab is `true`

*   **`dump`** (*optional*): the dump value in /etc/fstab, see *`fstab(8)`*

	>note: this parameter applies only if `fstab` is `true`

*   **`pass`** (*optional*): the pass value in /etc/fstab, see *`fstab(8)`*

	>note: this parameter applies only if `fstab` is `true`
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'path'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'device'	:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'filesystem':	{
					'type'		:	'line',
					'option'	:	['ext2', 'ext3', 'ext4', 'btrfs', 'iso9660', 'ntfs', 'reiserfs', 'xfs', 'zfs'],
					'required'	:	True
				},
				'fstab'		:	{
					'type'		:	'bool',
					'default'	:	'False',
					'required'	:	False,
					'visible'	:	True
				},
				'opts'		:	{
					'type'		:	'line',
					'required'	:	False
				},
				'dump'		:	{
					'type'		:	'line',
					'default'	:	'0',
					'required'	:	False
				},
				'pass'		:	{
					'type'		:	'line',
					'default'	:	'0',
					'required'	:	False
				}
			}
		},

		# filesystem
		'filesystem'	:	{
			'module'	:	'linux.mkfs',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
create a filesystem

### Parameters

*   **`device`** (*required*): the path of the device to format (/dev/xvd*)

*   **`fstype`** (*required*): the filesystem type to use (ext2, ext3, ext4 or xfs)

	>note: on REHL 6, xfs requires a manual installation of the xfsprogs (yum pkg state)

*   **`label`** (*optional*): label of the device
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'device'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'fstype'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'label'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
#					'block_size'		:	{
#						'type'		:	'line',
#						'required'	:	False,
#						'visible'	:	True
#					},
			}
		},
#			'fs'	:	{
#				'module'	:	'linux.fs',
#				'distro'	:	None,
#				'reference'	:	{
#					'en'	:	'''
#### Description
#	manage the filesystem
#
#### Parameters
#
#*   **dev** (*required*): the device name
#		example:
#			/dev/sda1
#
#*   **filesystem** (*required*): the filesystem type of the device
#
#*   **force** (*optional*): forcefully create the new filesystem, even if there is already one on the specified device, by default *False*
#
#*   **opts** (*optional*): additional options for creating the filesystem, see *MKE2FS(8)*
#			example:
#				-O journal_dev [ -b block-size ] [ -L volume-label ] [ -n ] [ -q ] [ -v ]  external-journal [ blocks-count ]
#					''',
#					'cn'	:	''''''
#				},
#				'parameter'	:	{
#					'dev'	:	{
#						'type'		:	'line',
#						'required'	:	True,
#						'visible'	:	True
#					},
#					'filesystem':	{
#						'type'		:	'line',
#						'option'	:	['ext2', 'ext3', 'ext4', 'btrfs', 'reiserfs', 'xfs', 'zfs'],
#						'required'	:	True,
#						'visible'	:	True
#					},
#					'opts':	{
#						'type'		:	'line',
#						'required'	:	False
#					},
#					'force'		:	{
#						'type'		:	'bool',
#						'default'	:	True,
#						'required'	:	False
#					}
#				}
#			},

		# command
		'cmd'	:	{
			'module'	:	'linux.cmd',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
execute a shell command

### Parameters
*   **`shell`** (*optional*): the absolute path of the shell to execute the command, by default `/bin/sh`

*   **`cmd`** (*required*): the command to execute

		example: find . -name *.pyc | xargs rm

*   **`cwd`** (*optional*): the current working directory to execute the command, be default `/opt/visualops/tmp/`

*   **`user`** (*optional*): the user to execute the command, by default the user which the agent runs as

*   **`group`** (*optional*): the group to execute the command, by default the group which the agent runs as

*   **`env`** (*optional*): environment variables for the command

*   **`timeout`** (*optional*): command timeout, by default `600` (in seconds)

	>note: By default, a command will be terminated and taken "failed" if not finishe in 600 seconds. However you can change with this option.

*   **`if-path-present`** (*optional*): the command will run only if all specified paths exist

*   **`if-path-absent`** (*optional*): the command will not run if any of the specified paths exists
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'shell'		:	{
					'type'		:	'line',
					'option'	:	'',
					'default'	:	'/bin/sh',
					'required'	:	False
				},
				'cmd'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'cwd'		:	{
					'type'		:	'line',
					'default'	:	'/opt/visualops/tmp/',
					'required'	:	False
				},
				'user'		:	{
					'type'		:	'line',
					'required'	:	False
				},
				'group'		:	{
					'type'		:	'line',
					'required'	:	False
				},
				'timeout'	:	{
					'type'		:	'line',
					'default'	:	600,
					'required'	:	False
				},
				'env'		:	{
					'type'		:	'dict',
					'required'	:	False
				},
				'if-path-present'	:	{
					'type'		:	'array',
					'required'	:	False,
					'visible'	:	True
				},
				'if-path-absent'	:	{
					'type'		:	'array',
					'required'	:	False,
					'visible'	:	True
				}
			}
		},

		# user account
		'user'	:	{
			'module'	:	'linux.user',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage a user

### Parameters

*   **`username`** (*required*): the user name

*   **`password`** (*required*): the encrypted password

	>note: use `openssl passwd -salt <salt> -1 <plaintext>` to generate the password hash

*   **`fullname`** (*optional*): the user's full name

*   **`uid`** (*optional*): the user id

*   **`gid`** (*optional*): the group id

*   **`home`** (*optional*): the user's home directory, by default `/home/$username`

	>note: if the directory already exists, the uid and gid of the directory will be set to this user; otherwise, the directory (and its parent directories) will be created, with the uid and gid

*   **`system-account`** (*optional*): whether to create a system account or not (see `useradd(8)`), by default: `false`

*   **`no-login`** (*optional*): whether to allow user to login or not, by default `false`

*   **`groups`** (*optional*): a list of groups of the user

	>note: if pass in an empty list, all groups of the user will be removed except the defaut one
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'username'	:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'password'	:	{
					'type'		:	'line',
					'required'	:	True
				},
				'fullname'	:	{
					'type'		:	'line',
					'required'	:	False
				},
				'uid'		:	{
					'type'		:	'line',
					'required'	:	False
				},
				'gid'		:	{
					'type'		:	'line',
					'required'	:	False
				},
				'home'		:	{
					'type'		:	'line',
					'default'	:	'/home/$username',		# TODO:
					'required'	:	False,
					'visible'	:	True
				},
				'system-account':	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False,
					'visible'	:	True
				},
				'no-login'	:	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False,
					'visible'	:	True
				},
				'groups'	:	{
					'type'		:	'array',
					'required'	:	False
				},
			}
		},

		# group
		'group'	:	{
			'module'	:	'linux.group',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage a group

### Parameters

*   **`groupname`** (*required*): the group name

*   **`gid`** (*optional*): the group id

*   **`system-group`** (*optional*): whether to create a system group (see `groupadd(8)`) or not, by default `false`
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'groupname'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'gid'		:	{
					'type'		:	'line',
					'required'	:	False
				},
				'system-group'		:	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False
				}
			}
		},

		# lvm pv
		'pv'	:	{
			'module'	:	'linux.lvm.pv',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage LVM physical volume (PV)

### Parameters

*   **`path`** (*required*): the path of the device or partition
`
		Example: /dev/sdc4, /dev/sde

*   **`force`** (*optional*): force to create the PV without any confirmation, by default ***`false`***

	>note: You can not recreate (reinitialize) a PV belonging to an existing volume group.


*   **`uuid`** (*optional*): specify the uuid for the device

	>note: Without this option, a random uuid will be generated. All of your PVs must have unique uuids. You need to use this option before restoring a backup of LVM metadata onto a replacement device - see vgcfgrestore(8). As such, use of restore file is compulsory unless the norestorefile is used.


*   **`zero`** (*optional*): whether or the first 4 sectors (2048 bytes) of the device should be wiped or not, by default ***`true`***

	>note: If this option is not given, the default is to wipe these sectors unless either or both of the --restorefile or --uuid options were specified.

*   **`data-alignment`** (*optional*): align the start of the data to a multiple of this number

	>note: You should also specify an appropriate "PV size" when creating the Volume Group (VG). To see the location of the first Physical Extent of an existing Physical Volume use pvs -o +pe_start. It will be a multiple of the requested alignment. In addition it may be shifted by alignment_offset from data_alignment_offset_detection (if enabled in lvm.conf(5)) or --dataalignmentoffset.

*   **`data-alignment-offset`** (*optional*): shift the start of the data area by this additional number

*   **`metadata-size`** (*optional*): the approximate amount of space to be set aside for each metadata area

	>note: The size you specify may get rounded

*   **`metadata-type`** (*optional*): specify which type of on-disk metadata to use, by default ***`lvm2`***

		Example: lvm1, lvm2, 1, 2

	>note: lvm1 or lvm2 can be abbreviated to 1 or 2 respectively. The default (lvm2) can be changed by setting format in the global section of the config file.

*   **`metadata-copies`** (*optional*): the number of metadata areas to set aside on each PV

		Example: currently this can be 0, 1 or 2

	>note: If set to 2, two copies of the volume group metadata are held on the PV, one at the front of the PV and one at the end. If set to 1 (the default), one copy is kept at the front of the PV (starting in the 5th sector). If set to 0, no copies are kept on this PV - you might wish to use this with VGs containing large numbers of PVs. But if you do this and then later use vgsplit(8) you must ensure that each VG is still going to have a suitable number of copies of the metadata after the split!

*   **`metadata-ignore`** (*optional*): whether to ignore metadata areas on this PV or not, by default ***`false`***

	>note: This setting can be changed with pvchange. If metadata areas on a physical volume are ignored, LVM will not store metadata in the metadata areas present on this Physical Volume. Metadata areas cannot be created or extended after Logical Volumes have been allocated on the device. If you do not want to store metadata on this device, it is still wise always to allocate a metadata area in case you need it in the future and to use this option to instruct LVM2 to ignore it.

*   **`restore-file`** (*optional*):

	>note: In conjunction with "uuid", this extracts the location and size of the data on the PV from the file (produced  by  vgcfgbackup) and ensures that the metadata that the program produces is consistent with the contents of the file i.e. the physical extents will be in the same place and not get overwritten by new metadata. This provides a mechanism to upgrade the metadata format or to add/remove metadata areas. Use with care. See also vgconvert(8).

*   **`no-restore-file`** (*optional*):

	>note: In conjunction with "uuid", this allows a uuid to be specified without also requiring that a backup of the metadata be provided.

*   **`label-sector`** (*optional*):

	>note: By default the PV is labelled with an LVM2 identifier in its second sector (sector 1). This lets you use a different sector near the start of the disk (between 0 and 3 inclusive - see LABEL_SCAN_SECTORS in the source). Use with care.

*   **`pv-size`** (*optional*):

	>>note: Overrides the automatically-detected size of the PV, use with care
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'path'		:	{
					'type'		:	'array',
					'required'	:	True,
					'visible'	:	True
				},
				'force'		:	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False
				},
				'uuid'		:	{
					'type'		:	'line',
					'required'	:	False
				},
				'zero'		:	{
					'type'		:	'bool',
					'default'	:	True,
					'required'	:	False
				},
				'data-alignment'	:	{
					'type'		:	'line',
					'required'	:	False
				},
				'data-alignment-offset'	:	{
					'type'		:	'line',
					'required'	:	False
				},
				'metadata-size'	:	{
					'type'		:	'line',
					'required'	:	False
				},
				'metadata-type'	:	{
					'type'		:	'line',
					'default'	:	'lvm2',
					'option'	:	['lvm1', 'lvm2'],
					'required'	:	False
				},
				'metadata-copies'	:	{
					'type'		:	'line',
					'option'	:	['0', '1', '2'],
					'required'	:	False
				},
				'metadata-ignore'	:	{
					'type'		:	'bool',
					'dfault'	:	False,
					'required'	:	False
				},
				'restore-file'	:	{
					'type'		:	'line',
					'required'	:	False
				},
				'no-restore-file'	:	{
					'type'		:	'bool',
					'default'	:	True,
					'required'	:	False
				},
				'label-sector'	:	{
					'type'		:	'line',
					'default'	:	'LVM2',
					'required'	:	False
				},
				'pv-size'		:	{
					'type'		:	'line',
					'required'	:	False
				}
			}
		},

		# lvm vg
		'vg'	:	{
			'module'	:	'linux.lvm.vg',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage LVM volume group (VG)

### Parameters


*   **`name`** (*required*): the VG name

*   **`path`** (*required*): a list of block special devices

		Example: /dev/sdk1, /dev/sdl1

*   **`clustered`** (*optional*): whether to enable the clustered locking on the VG or not, by default ***`true`***

	>note: If the new VG is shared with other nodes in the cluster, need to enable this option. If the new VG contains only local disks that are not visible on the other nodes, this option must be turned off. If the cluster infrastructure is unavailable on a particular node at a particular time, you may still be able to use such VGs

*   **`max-lv-number`** (*optional*): specify the maximum number of LVs allowed in this VG

	>note: For VGs with  metadata in lvm1 format, the limit and default value is 255. If the metadata uses lvm2 format, the default value is 0 which removes this restriction: there is then no limit

*   **`max-pv-number`** (*optional*): specify the maximum number of PVs that can belong to this VG

	>note: For VGs with metadata in lvm1 format, the limit and default value is 255. If the metadata uses lvm2 format, the value 0 removes this restriction: there is then no limit

*   **`metadata-type`** (*optional*): specify which type of on-disk metadata to use, by default ***`lvm2`***

		Example: lvm1, lvm2, 1, 2

	>note:
			lvm1 or lvm2 can be abbreviated to 1 or 2 respectively. The default (lvm2) can be changed by setting format
			in the global section of the config file.

*   **`metadata-copies`** (*optional*): specify the desired number of metadata copies in the VG

		Example: unmanaged, all

	>note: If set to a non-zero value, LVM will automatically manage the 'metadata ignore' option on the PVs (see pvcreate(8) or pvchange --metadataignore) in order to achieve the copies of metadata. If set to unmanaged, LVM will not automatically manage the 'metadata ignore' option. If set to all, LVM will first clear all of the 'metadata ignore' option on all metadata areas in the VG, then set the value to unmanaged. This option is useful for VGs containing large numbers of PVs  with metadata  as it may be used to minimize metadata read and write overhead. The default value is unmanaged

*   **`pe-size`** (*optional*): specify the physical extent size on PVs of this VG

		Example: bBsSkKmMgGtTpPeE

   	>note: A size suffix (k for kilobytes up to t for terabytes) is optional, megabytes is the default if no suffix is present. The default is 4 MiB and it must be at least 1 KiB and a power of 2.

	>Once this value has been set, it is difficult to change it without recreating the volume group which would involve  backing up and restoring data on any logical volumes. However, if no extents need moving for the new value to apply, it can be altered using vgchange -s.

	>If the volume group metadata uses lvm1 format, extents can vary in size from 8KiB to 16GiB and there is a limit of 65534 extents in each logical volume. The default of 4 MiB leads to a maximum logical volume size of around 256GiB.

	>If the volume group metadata uses lvm2 format those restrictions do not apply, but having a large number of extents will slow down the tools but have no impact on I/O performance to the logical volume. The smallest PE is 1KiB

	>The 2.4 kernel has a limitation of 2TiB per block device.

*   **`autobackup`** (*optional*): whether to metadata should be backed up automatically after a change or not, by default ***`true`***

	>note: You are strongly advised not to disable this! See vgcfgbackup(8)

*   **`tag`** (*optional*): add the tag to this VG

	>note: A tag is a word that can be used to group LVM2 objects of the same type together. Tags can be given on the command line in place of PV, VG or LV arguments. Tags should be prefixed with  @ to avoid ambiguity. Each tag is expanded by replacing it with all objects possessing that tag which are of the type expected by its position on the command line. PVs can only possess tags while they are part of a Volume Group: PV tags are discarded if the PV is removed from the VG. As an example, you could tag some LVs as database and others as userdata and then activate the  database  ones  with  lvchange  -ay @database. Objects can possess multiple tags simultaneously. Only the new LVM2 metadata format supports tagging: objects using the LVM1 metadata format cannot be tagged because the on-disk format does not support it. Characters allowed in tags are: A-Z a-z 0-9 _ + . - and as of version 2.02.78 the following characters are also accepted: / = ! : # &

*   **`allocation-policy`** (*optional*): specify the allocation policy

		Example: contiguous, cling, normal, anywhere or inherit

	>note: When a command needs to allocate Physical Extents from the Volume Group, the allocation policy controls how they are chosen. Each Volume Group and Logical Volume has an allocation policy defined. The default for a Volume Group is normal which applies common-sense rules such as not placing parallel stripes on the same Physical Volume. The default for a Logical Volume is inherit which applies the same policy as for the Volume Group. These policies can be changed using lvchange(8) and vgchange(8) or overridden on the command line of any command that performs allocation. The contiguous policy requires that new Physical Extents be placed adjacent to existing Physical Extents. The cling policy places new Physical Extents on the same Physical Volume as existing Physical Extents in the same stripe of the Logical Volume. If there are sufficient free Physical Extents to satisfy an allocation request but normal doesn't use them, anywhere will - even if that reduces performance by placing two stripes on the same Physical Volume.
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'name'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'path'		:	{
					'type'		:	'array',
					'required'	:	True,
					'visible'	:	True
				},
				'clustered'		:	{
					'type'		:	'bool',
					'default'	:	True,
					'required'	:	False
				},
				'max-lv-number'		:	{
					'type'		:	'line',
					'required'	:	False
				},
				'max-pv-number'		:	{
					'type'		:	'line',
					'required'	:	False
				},
				'metadata-type'	:	{
					'type'		:	'line',
					'default'	:	'lvm2',
					'option'	:	['lvm1', 'lvm2'],
					'required'	:	False
				},
				'metadata-copies'		:	{
					'type'		:	'line',
					'option'	:	['unmanaged', 'all'],
					'required'	:	False
				},
				'pe-size'		:	{
					'type'		:	'line',
					'default'	:	'4m',
					'required'	:	False
				},
				'autobackup'		:	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False
				},
				'tag'		:	{
					'type'		:	'line',
					'required'	:	False
				},
				'allocation-policy'		:	{
					'type'		:	'line',
					'option'	:	['anywhere', 'contiguous', 'cling', 'inherit', 'normal'],
					'required'	:	False
				},
			}
		},

		# lvm lv
		'lv'	:	{
			'module'	:	'linux.lvm.lv',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage LVM logical volume (LV)

### Parameters

*   **`name`** (*required*): specify the name of the new LV

	>note: Without this option a default names of "lvol#" will be generated where # is the LVM internal number of the logical volume

*	**`vg-name`** (*required*): specify the volume group name which the new LV created from

*   **`path`** (*optional*): a list of physical volume path

		Example: /dev/sdk1, /dev/sdk2

	>note: VolumeGroup{Name|Path}[/ThinPoolLogicalVolumeName]
	   [PhysicalVolumePath[:PE[-PE]]...]

*   **`available`** (*optional*): specify the name of the new LV

		Example: y, ay, n, ey, en, ly, ln

	>note: Controls the availability of the Logical Volumes for immediate use after the command finishes running.  By default, new Logical Volumes are activated (-ay). If it is possible technically, -an will leave the new Logical Volume inactive. But for example, snapshots can only be created in the active state so -an cannot be used with --snapshot. Normally the --zero n argument has to be supplied too because zeroing (the default behaviour) also requires activation. If autoactivation option is used (-aay), the logical volume is activated only if it matches an item in the activation/auto_activation_volume_list set in lvm.conf. For autoactivated logical volumes, --zero n is always assumed and it can't be overridden. If clustered locking is enabled, -aey will activate exclusively on one node and -aly will activate only on the local node.

*   **`chunk-size`** (*optional*): speicy the size of chunk for snapshot and thin pool LV

	>note: For snapshots the value must be power of 2 between 4KiB and 512KiB and the default value is 4. For thin pools the value must be between 64KiB and 1048576KiB and the default value starts with 64 and scales up to fit the pool metadata size within 128MB, if the poolmetadata size is not specified. Older dm thin pool target version (<1.4) requires the value to be power of 2. The newer version requires to be the multiple of 64KiB, however discard is not supported for non power of 2 values.  Default unit is in kilobytes.

*   **`contiguous`** (*optional*): set or reset the contiguous allocation policy for LVs, by default ***`false`***

	>note: Default is no contiguous allocation based on a next free principle.

*   **`discards`** (*optional*): specify the discards behavior, by default ***`passdown`***

		Example: ignore, nopassdown, passdown

*   **`stripe-number`** (*optional*): specify the number of stripes

	>note: This is equal to the number of physical volumes to scatter the logical volume

*   **`stripe-size`** (*optional*): specify the number of kilobytes for the granularity of the stripes.

	>note: size must be 2^n (n = 2 to 9) for metadata in LVM1 format. For metadata in LVM2 format, the stripe size may be a  larger power of 2 but must not exceed the physical extent size

*   **`le-number`** (*optional*): specify the number of logical extents to allocate for the new LV

	>note: The number can also be expressed as a percentage of the total space in the Volume Group with the suffix %VG, as a percentage of the remaining free space in the Volume Group with the suffix %FREE, as a percentage of the remaining free space for the specified PhysicalVolume(s) with the suffix %PVS, or (for a snapshot) as a percentage of the total space in the Origin  Logical Volume with the suffix %ORIGIN

*   **`le-size`** (*optional*): specify the size to allocate for the new LV

	>note: A size suffix of K for kilobytes, M for megabytes, G for gigabytes, T for terabytes, P for petabytes or E for exabytes is optional. Default unit is megabytes

*   **`minor-number`** (*optional*): specify the minor number

*   **`persistent`** (*optional*): whether to make the minor number specified persistent or not, by default ***`false`***

*   **`mirror-number`** (*optional*): Create a mirrored LV with this number of copies

	>note: For example, specifying "-m 1" would result in a mirror with two- sides; that is, a linear volume plus one copy.

	>Specifying the optional argument --nosync will cause the creation of the mirror to skip the initial resynchronization. Any data written afterwards will be mirrored, but the original contents will not be copied. This is useful for skipping a potentially long and resource intensive initial sync of an empty device.

    >The optional argument --mirrorlog specifies the type of log to be used. The default is disk, which is persistent and requires a small amount of storage space, usually on a separate device from the data being mirrored. Using core means the mirror is regenerated by copying the data from the first device again each time the device is activated, for example, after every reboot. Using "mirrored" will create a persistent log that is itself mirrored.

	>The optional argument --corelog is equivalent to --mirrorlog core

*   **`no-udev-sync`** (*optional*): whether to disable udev synchronisation or not, by default ***`false`***

	>note: The process will not wait for notification from udev. It will continue irrespective of any possible udev processing in the background. You should only use this if udev is not running or has rules that ignore the devices LVM2 creates

*   **`monitor`** (*optional*): whether to monitor a mirrored or snapshot LV with dmeventd or not, if it is installed, by default ***`false`***

	>note: If a device used by a monitored mirror reports an I/O error, the failure is handled according to mirror_image_fault_policy and mirror_log_fault_policy set in lvm.conf

*   **`ignore-monitoring`** (*optional*): make no attempt to interact with dmeventd unless ***monitor*** is ***`true`*** ,by default ***`false`***

*   **`permission`** (*optional*): specify the access permissions to read only or read and write, by default ***RW***

		Example: r, rw

*   **`pool-metadata-size`** (*optional*): specify the size of thin pool's metadata LV

	>note: Supported value is in range between 2MiB and 16GiB. Default value is (Pool_LV_size / Pool_LV_chunk_size  *  64b).   Default unit is megabytes.

*   **`region-size`** (*optional*):

	>note: A mirror is divided into regions of this size (in MB), and the mirror log uses this granularity to track which regions are in sync.

*   **`readahead`** (*optional*): set read ahead sector count of this LV

		Example: ReadAheadSectors, auto, none

	>note: For volume groups with metadata in lvm1 format, this must be a value between 2 and 120. The default value is "auto" which allows the kernel to choose a suitable value automatically.  "None" is equivalent to specifying zero.

*   **`snapshot`** (*optional*): create a snapshot logical volume (or snapshot) for an existing, so called original logical volume (or origin)

	>note: Snapshots provide a 'frozen image' of the contents of the origin while the origin can still be updated. They enable consistent backups and online recovery of removed/overwritten data/files. Thin snapshot is created when the origin is a thin  volume and the size is not specified. Thin snapshot shares same blocks within the thin pool volume. The snapshot with the specified size does not need the same amount of storage the origin has. In a typical scenario, 15-20% might be enough.  In case the snapshot runs out of storage, use lvextend(8) to grow it. Shrinking a snapshot is supported by lvreduce(8) as well. Run  lvdisplay(8) on the snapshot in order to check how much data is allocated to it. Note that a small amount of the space you allocate to the snapshot is used to track the locations of the chunks of data, so you should allocate slightly more space than  you actually need and monitor the rate at which the snapshot data is growing so you can avoid running out of space

*   **`thinpool`** (*optional*): create thin pool or thin logical volume or both

		Example: ReadAheadSectors, auto, none

	>note: Specifying the optional argument --size will cause the creation of the thin pool logical volume. Specifying the optional argument --virtualsize will cause the creation of the thin logical volume from given thin pool volume. Specifying  both arguments will cause the creation of both thin pool and thin volume using this pool. Requires device mapper kernel driver for thin provisioning from kernel 3.2 or newer

*   **`type`** (*optional*): create a logical volume that uses the specified segment type, (e.g. `raid5`, `mirror`, `snapshot`, `thin`, `thin-pool`)

	>note: Many segment types have a commandline switch alias that will enable their use (-s is an alias for --type snapshot).   However, this argument must be used when no existing commandline switch alias is available for the desired type, as is the  case with error, zero, raid1, raid4, raid5 or raid6

*   **`virtual-size`** (*optional*): Create a sparse device of the given size (in MB by default) using a snapshot or thinly provisioned device when thin pool is specified.

	>note: Anything written to the device will be returned when reading from it. Reading from other areas of the device will return blocks of zeros. Virtual snapshot is implemented by creating a hidden virtual device of the requested size using the zero target. A suffix of _vorigin is used for this device.

*   **`zero`** (*optional*): whether to set zero of the first KB of data in the new LV or not, by default ***`true`***

	>note: Volume will not be zeroed if read only flag is set.

	>Snapshot volumes are zeroed always.

*   **`autobackup`** (*optional*): whether to metadata should be backed up automatically after a change or not, by default ***`true`***

	>note: You are strongly advised not to disable this! See vgcfgbackup(8)

*   **`tag`** (*optional*): add the tag to this VG

	>note: A tag is a word that can be used to group LVM2 objects of the same type together. Tags can be given on the command line in place of PV, VG or LV arguments. Tags should be prefixed with @ to avoid ambiguity. Each tag is expanded by replacing  it with all objects possessing that tag which are of the type expected by its position on the command line. PVs can only possess tags while they are part of a Volume Group: PV tags are discarded if the PV is removed from the VG. As an example, you could tag some LVs as database and others as userdata and then activate the database ones with lvchange -ay @database. Objects can possess multiple  tags  simultaneously. Only the new LVM2 metadata format supports tagging: objects using the LVM1 metadata format cannot be tagged because the on-disk format does not support it. Characters allowed in tags are: A-Z a-z 0-9 _ + . - and as of version 2.02.78 the following characters are also accepted: / = ! : # &

*   **`allocation-policy`** (*optional*): specify the allocation policy

		Example: contiguous, cling, normal, anywhere or inherit

	>note: When a command needs to allocate Physical Extents from the Volume Group, the allocation policy controls how they are chosen. Each Volume Group and Logical Volume has an allocation policy defined. The default for a Volume Group is normal which applies common-sense rules such as not placing parallel stripes on the same Physical Volume. The default for a Logical Volume is inherit which applies the same policy as for the Volume Group.  These policies can be changed using lvchange(8) and vgchange(8) or overridden on the command line of any command that performs allocation. The contiguous policy requires that new  Physical Extents be placed adjacent to existing Physical Extents. The cling policy places new Physical Extents on the same Physical Volume as existing Physical Extents in the same stripe of the Logical Volume. If there are sufficient free Physical Extents to satisfy an allocation request but normal doesn't use them, anywhere will - even if that reduces performance by placing two stripes on the same Physical Volume
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'name'		:	{
					'type'		:	'line',
					'required'	:	True
				},
				'vg-name'	:	{
					'type'		:	'line',
					'required'	:	True
				},
				'path'		:	{
					'type'		:	'array',
					'required'	:	False,
					'visible'	:	True
				},
				'available'		:	{
					'type'		:	'line',
					'option'	:	['y', 'ay' , 'n', 'ey', 'en', 'ly', 'ln'],
					'required'	:	False,
				},
				'chunk-size':	{
					'type'		:	'line',
					'required'	:	False,
				},
				'contiguous':	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False,
				},
				'discards':	{
					'type'		:	'line',
					'default'	:	'passdown',
					'option'	:	['ignore', 'nopassdown', 'passdown'],
					'required'	:	False,
				},
				'stripe-number':	{
					'type'		:	'line',
					'required'	:	False,
				},
				'stripe-size':	{
					'type'		:	'line',
					'required'	:	False,
				},
				'le-number':	{
					'type'		:	'line',
					'required'	:	False,
				},
				'le-size':	{
					'type'		:	'line',
					'required'	:	False,
				},
				'minor-number':	{
					'type'		:	'line',
					'required'	:	False,
				},
				'persistent':	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False,
				},
				'mirror-number':	{
					'type'		:	'line',
					'required'	:	False,
				},
				'no-udev-sync'	:	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False,
				},
				'monitor'		:	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False,
				},
				'ignore-monitoring'	:	{
					'type'		:	'bool',
					'default'	:	True,
					'required'	:	False,
				},
				'permission'	:	{
					'type'		:	'line',
					'option'	:	['r', 'rw'],
					'required'	:	False,
				},
				'pool metadata size':	{
					'type'		:	'line',
					'required'	:	False,
				},
				'region-size'	:	{
					'type'		:	'line',
					'required'	:	False,
				},
				'readahead'	:	{
					'type'		:	'line',
					'option'	:	['ReadAheadSectors', 'auto', 'none'],
					'required'	:	False,
				},
				'snapshot'	:	{
					'type'		:	'line',
					'required'	:	False,
				},
				'thinpool'	:	{
					'type'		:	'line',
					'required'	:	False,
				},
				'type'		:	{
					'type'		:	'line',
					'option'	:	['raid1', 'raid4', 'raid5', 'raid6'],
					'required'	:	False,
				},
				'virtual-size'	:	{
					'type'		:	'line',
					'required'	:	False,
				},
				'zero'			:	{
					'type'		:	'bool',
					'default'	:	True,
					'required'	:	False,
				},
				'autobackup'		:	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False
				},
				'tag'		:	{
					'type'		:	'line',
					'required'	:	False
				},
				'allocation-policy'		:	{
					'type'		:	'line',
					'option'	:	['anywhere', 'contiguous', 'cling', 'inherit', 'normal'],
					'required'	:	False
				},
			}
		},

		# pull a docker image from the hub
		'docker pulled'	:	{
			'module'	:	'linux.docker.pulled',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
Pull the latest image from the specified repository at the specified tag (if any)

### Parameters

*   **`repo`** (*required*): Repository URL or/and Image name

		example:
			namespace/repo

*   **`tag`** (*optional*): Repository tag (default: latest)

		example:
			latest

*   **`username`** (*optional*): Username used to login to repository

*   **`password`** (*optional*): Password used to login to repository (required if username specified)

*   **`email`** (*optional*): Email used to login to repository (required if username specified)

*   **`containers`** (*optional*): Container(s) associated to this image (specify it if you want your container to be re-created when a new version of the image is pulled)

		example:
			my_container
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'repo'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'tag'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'username'	:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'password'	:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'email'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'containers'		:	{
					'type'		:	'array',
					'required'	:	False,
					'visible'	:	True
				},
			},
		},

		# build a docker image locally
		'docker built'	:	{
			'module'	:	'linux.docker.built',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
Ensure an image is built from a `Dockerfile`. If not, build it. If the file changes, the image will be rebuilt.

### Parameters

*   **`tag`** (*required*): Tag of the image

		example:
			namespace/image

*   **`path`** (*required*): Filesystem path to the `Dockerfile`

		example:
			/opt/docker/image

*   **`containers`** (*optional*): Container(s) associated to the newly created image (specify it if you want your container to be re-created when the file changes)

		example:
			my_container

*   **`force`** (*optional*): Force (re)build on each round
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'tag'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'path'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'containers'		:	{
					'type'		:	'array',
					'required'	:	False,
					'visible'	:	True
				},
                                    'force'                 :       {
					'type'		:	'bool',
                                            'default'       :       False,
					'required'	:	False,
					'visible'	:	True
                                    }
			},
		},

		# run a docker container
		'docker running'	:	{
			'module'	:	'linux.docker.running',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
Ensure that a container from the given name is running. If not, run it.

### Parameters

*   **`container`** (*required*): Desired name of the container (must be the name specified in "pulled" and "built" states, if any)

		example:
			my_container

*   **`image`** (*required*): Image from which to build this container

		example:
			namespace/image


*   **`count`** (*optional*): Specify the number of containers to run

*   **`command`** (*optional*): Command to run in the container (if not specified in `Dockerfile`)

		example (in case of apache server):
			/usr/bin/apache2
			-D
			FOREGROUND

*   **`environment`** (*optional*): Environment variables for the container (if not specified in `Dockerfile`)

		example:
			FOO: bar

*   **`volumes`** (*optional*): List of volumes to attach (if not specified in `Dockerfile`). (specify :ro for read only mode)

		example:
			/host/path: /mount/point
			/host/path: /mount/point/read/only:ro

*   **`devices`** (*optional*): List of devices to attach (if not specified in `Dockerfile`). (specify :rwm to set read, write and mknode rights limitation)

		example:
			/dev/sdhost: /dev/sdcontainer
			/dev/sda:    /dev/xvda
                        /dev/xvdf:   /dev/xvdf:r

*   **`mem_limit`** (*optional*): Memory size limit (if not specified in `Dockerfile`)

		example:
			512m

*   **`cpu_shares`** (*optional*): CPU shares authorized (if not specified in `Dockerfile`)

		example:
			0-3

		example:
			0

*   **`port_bindings`** (*optional*): List of ports to expose on host system. Maps containers port/protocol to host listening ip:port

		note:
			If the count parameter is specified, the host port will be incremented by one on each.

		example:
			5000/tcp: 127.0.0.1:5000
			6000/tcp: 6000 (default ip: 0.0.0.0)
			80: 6666 (default protocol: tcp)

*   **`force`** (*optional*): Force (re)build container on each round.

		note:
			Use this option if you edit any other parameter. Don't forget to disable it once a round has succeed.

*   **`files`** (*optional*): list of persistent files

		example:
			/etc/nginx/nginx.conf : *content*
			/etc/my.cnf           : *content*
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'container'	:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'image'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'tag'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'username'	:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'password'	:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'email'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'count'         :       {
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'command'		:	{
					'type'		:	'array',
					'required'	:	False,
					'visible'	:	True
				},
				'environment'	:	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True
				},
				'volumes'		:	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True
				},
				'devices'		:	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True
				},
				'mem_limit'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'cpu_shares'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
#				'publish_all_ports'	:	{
#					'type'		:	'bool',
#					'required'	:	False,
#					'default'	:	False,
#					'visible'	:	True
#				},
#				'links'		:	{
#					'type'		:	'dict',
#					'required'	:	False,
#					'visible'	:	True
#				},
				'port_bindings'		:	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True
				},
                                'files'                 :	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True
				},
				'force'                 :	{
					'type'		:	'bool',
					'required'	:	False,
					'default'	:	False,
					'visible'	:	True
				},
			},
		},


		# push a docker image to the hub
		'docker pushed'	:	{
			'module'	:	'linux.docker.pushed',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
Push an image to a docker registry. (`docker push`)

### Parameters

*   **`repository`** (*required*): Repository to push

		example:
			namespace/image

		example:
			namespace/my_container

*   **`container`** (*optional*): Container id to commit (if desired to push a container as an image)

		example:
			my_container

*   **`tag`** (*optional*): Repository tag (default: latest)

		example:
			latest

*   **`message`** (*optional*): Commit message (if container specified to be commited)

*   **`author`** (*optional*): Author (if container specified to be commited)

*   **`username`** (*optional*): Username used to login to repository

*   **`password`** (*optional*): Password used to login to repository (required if username specified)

*   **`email`** (*optional*): Email used to login to repository (required if username specified)

*   **`dep_containers`** (*optional*): Containers needed to be shutdown if something new is pushed (in order to be rebuilt)

		example:
			my_container
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'repository'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True,
				},
				'container'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True,
				},
				'tag'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True,
				},
				'message'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True,
				},
				'author'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True,
				},
				'username'	:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'password'	:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'email'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'dep_containers'	:	{
					'type'		:	'array',
					'required'	:	False,
					'visible'	:	True,
				},
			},
		},



		# run a docker container from remote image
		'docker'	:	{
			'module'	:	'linux.docker.deploy',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
Run a container from a remote image

### Parameters

*   **`container`** (*required*): Desired name of the container (must be the name specified in "pulled" and "built" states, if any)

		example:
			my_container

*   **`image`** (*required*): Image/repo from which to build this container

		example:
			namespace/image

*   **`tag`** (*optional*): Repository tag (default: latest)

		example:
			latest

*   **`username`** (*optional*): Username used to login to repository

*   **`password`** (*optional*): Password used to login to repository (required if username specified)

*   **`email`** (*optional*): Email used to login to repository (required if username specified)

*   **`count`** (*optional*): Specify the number of containers to run

*   **`command`** (*optional*): Command to run in the container (if not specified in `Dockerfile`)

		example (in case of apache server):
			/usr/bin/apache2
			-D
			FOREGROUND

*   **`environment`** (*optional*): Environment variables for the container (if not specified in `Dockerfile`)

		example:
			FOO: bar

*   **`volumes`** (*optional*): List of volumes to attach (if not specified in `Dockerfile`). (specify :ro for read only mode)

		example:
			/host/path: /mount/point
			/host/path: /mount/point/read/only:ro

*   **`devices`** (*optional*): List of devices to attach (if not specified in `Dockerfile`). (specify :rwm to set read, write and mknode rights limitation)

		example:
			/dev/sdhost: /dev/sdcontainer
			/dev/sda:    /dev/xvda
                        /dev/xvdf:   /dev/xvdf:r

*   **`mem_limit`** (*optional*): Memory size limit (if not specified in `Dockerfile`)

		example:
			512m

*   **`cpu_shares`** (*optional*): CPU shares authorized (if not specified in `Dockerfile`)

		example:
			0-3

		example:
			0

*   **`port_bindings`** (*optional*): List of ports to expose on host system. Maps containers port/protocol to host listening ip:port

		note:
			If the count parameter is specified, the host port will be incremented by one on each.

		example:
			5000/tcp: 127.0.0.1:5000
			6000/tcp: 6000 (default ip: 0.0.0.0)
			80: 6666 (default protocol: tcp)

*   **`force`** (*optional*): Force (re)build container on each round

		note:
			Use this option if you edit any other parameter. Don't forget to disable it once a round has succeed.

*   **`files`** (*optional*): list of persistent files

		example:
			/etc/nginx/nginx.conf : *content*
			/etc/my.cnf           : *content*
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'container'	:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'image'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'tag'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'username'	:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'password'	:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'email'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'count'         :       {
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'command'		:	{
					'type'		:	'array',
					'required'	:	False,
					'visible'	:	True
				},
				'environment'	:	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True
				},
				'volumes'		:	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True
				},
				'devices'		:	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True
				},
				'mem_limit'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
				'cpu_shares'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
#				'publish_all_ports'	:	{
#					'type'		:	'bool',
#					'required'	:	False,
#					'default'	:	False,
#					'visible'	:	True
#				},
#				'links'		:	{
#					'type'		:	'dict',
#					'required'	:	False,
#					'visible'	:	True
#				},
				'port_bindings'		:	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True
				},
                                'files'                 :	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True
				},
				'force'                 :	{
					'type'		:	'bool',
					'required'	:	False,
					'default'	:	False,
					'visible'	:	True
				},
			},
		},






		# Apply a puppet manifest
		'puppet apply'	:	{
			'module'	:	'linux.puppet.apply',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
Apply a Puppet manifest. This module will run independently, and doesn't require to connect to any Puppet server.

`puppet apply` will run the manifests files set in the `manifests` parameter.

Note: Puppet module is incompatible with CentOS 6.4

### Parameters

*   **`manifests`** (*required*): Manifest(s) to run

		example:
			/path/to/manifest1
			/path/to/manifest2

*   **`arguments`** (*optional*): Arguments to the manifest, passed to the Puppet binary (see Puppet documentation). You can use these arguments to specify a modules directory, or some specific classes to run, for example.

		example:
			modulepath: /a/b/modules
			tags:       basefiles::edit,apache::server

*   **`version`** (*optional*): Puppet version to install. Leave empty for latest version.

		example:
			3.7.3
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'manifests'		:	{
					'type'		:	'array',
					'required'	:	True,
					'visible'	:	True,
				},
				'arguments'		:	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True,
				},
				'version'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
			},
		},
		# Run a puppet manifest round
		'puppet run'	:	{
			'module'	:	'linux.puppet.run',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
Run a Puppet round. This module is useful in case you already have a custom configuration for the puppet client, and simply want to run a round. No argument is required. If you don't have any specific requirement and want to apply a Puppet manifest or connect to a Puppet server, this module is probably not the one you want to use.

Note: Puppet module is incompatible with CentOS 6.4

### Parameters

*   **`arguments`** (*optional*): Arguments to the round, passed to the Puppet binary (see Puppet documentation). You can use these arguments to specify a modules directory, or some specific classes to run, for example.

		example:
			tags:       basefiles::edit,apache::server

*   **`version`** (*optional*): Puppet version. Leave empty for latest version.

		example:
			3.7.3
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'arguments'		:	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True,
				},
				'version'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
			},
		},
		# Run Puppet agent
		'puppet agent'	:	{
			'module'	:	'linux.puppet.agent',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
Run Puppet agent. This module will connect to the server specified in `server` and act as a regular Puppet client. Note that, as Puppet require, you need to use the name of the server, not its IP address. You need to be able to resolve this name, either via DNS resolution or host file.

This module is useful if you already have a Puppet server running and you want to control the client recipe execution on your instance using VisualOps.

Note: Puppet module is incompatible with CentOS 6.4

### Parameters

*   **`server`** (*required*): Server to connect to

		example:
			tags:       puppet.mydomain.com

*   **`arguments`** (*optional*): Arguments to the round, passed to the puppet binary (see puppet documentation). You can use these arguments to specify a modules directory, or some specific classes to run, for example.

		example:
			tags:       basefiles::edit,apache::server

*   **`version`** (*optional*): Puppet version. Leave empty for latest version.

		example:
			3.7.3
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'server'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True,
				},
				'arguments'		:	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True,
				},
				'version'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
			},
		},




		# Run a chef solo recipe
		'chef solo'	:	{
			'module'	:	'linux.chef.solo',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
Run a Chef solo. You should have your Chef recipe already present on your instance, or download it using the `recipe_url` parameter. Not that it is highly recommended to write a Chef configuration file, that you can specify in the `config` parameter. The config file may contains the location of your recipe, as well as the different items to run.

See Chef documentation for more details.

### Parameters

*   **`config`** (*recommended*): Path to Chef recipe config file. Generally used to specify a custom location of your Chef recipe.

		example:
			/path/to/config/file

*   **`override_runlist`** (*optional*): Replace current run list with specified items for a single run

		example:
		        recipe[chef-server::default]

*   **`recipe_url`** (*optional*): URI to remote gzipped tarball of recipes (`-r` option of chef-solo)

		example:
			http://server.com/recipe.tgz

*   **`arguments`** (*optional*): Additional arguments to Chef, passed to the Chef binary (see Chef documentation). You can use these arguments to specify a running group, or a log level, for example.

		example:
			group:            root
			log_level:        warning

*   **`version`** (*optional*): Chef version. Leave empty for latest version.

		example:
			12.0.1
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'config'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True,
				},
				'override-runlist'	:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True,
				},
				'recipe_url'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True,
				},
				'arguments'		:	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True,
				},
				'version'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
			},
		},
		# Run a chef client
		'chef client'	:	{
			'module'	:	'linux.chef.client',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
Run a Chef client. This module allows you to run a Chef recipe distributed by a Chef server. This is useful if you already have a Chef server running and you want to control the client recipe execution on your instance using VisualOps.

See Chef documentation for more details.

### Parameters

*   **`server`** (*required*): URI to remote Chef server. Ensure you are able to resolv its hostname.

		example:
			https://localhost

*   **`client_key`** (*optional*): Path to client authentication key. This is usually required to establish a connection to the chef server.

		example:
			/path/to/client/key

*   **`config`** (*optional*): Path to chef config file

		example:
			/path/to/config/file

*   **`arguments`** (*optional*): Additional arguments to chef, passed to the chef binary (see chef documentation). You can use these arguments to specify a running group, or a log level, for example.

		example:
			group:     root
			log_level: warning

*   **`version`** (*optional*): Chef version. Leave empty for latest version.

		example:
			12.0.1
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'server'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True,
				},
				'client_key'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True,
				},
				'config'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True,
				},
				'arguments'		:	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True,
				},
				'version'		:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				},
			},
		},



		# Create and ensure a Raid array is present
		'raid'	:	{
			'module'	:	'linux.raid',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
Create and ensure a Raid array is present.

See `mdadm` documentation for more details.

### Parameters

*   **`device-name`** (*required*): Name of the raid array

		example:
			/dev/md0

*   **`level`** (*required*): The RAID level to use when creating the raid. Options are: linear, raid0, 0, stripe, raid1, 1, mirror, raid4, 4, raid5, 5, raid6, 6, raid10, 10, multipath, mp, faulty, container. Obviously some of these are synonymous.

		example:
			raid1

*   **`devices`** (*required*): A list of devices used to build the array.

		example:
			/dev/xvdf, /dev/xvdg

*   **`arguments`** (*optional*): Additional arguments passed to the mdadm binary (see mdadm documentation). You can use these arguments to specify chunk size, for example.

		example:
			chunk:	256
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'device-name'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True,
				},
				'level'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True,
				},
				'devices'		:	{
					'type'		:	'array',
					'required'	:	True,
					'visible'	:	True,
				},
				'arguments'		:	{
					'type'		:	'dict',
					'required'	:	False,
					'visible'	:	True,
				},
			},
                },




                "mesos master": {
                    "module": "linux.mesos.master",
                    "reference": {
                        "cn": "",
                        "en": """
### Description
Runs a Mesos Master instance

### Parameters

*   **`cluster_name`** (*required*): Name of the Mesos cluster

		example:
			Mesos Cluster

*   **`server_id`** (*required*): ID of the Mesos Master server

		example:
			1
			2

*   **`masters_addresses`** (*required*): IPs/hostnames of the Mesos Master servers. If no hostname is given, the ip address will be used by default as hostname.

		example:
			@{master1.PrivateIpAddress}:    master1
			@{master2.PrivateIpAddress}:    master2
			@{master3.PrivateIpAddress}:

*   **`hostname`** (*optional*): Hostname of the Mesos Master server instance

		example:
			master1

*   **`framework`** (*optional*): Framework to install on top of Mesos

		example:
			marathon
""",
                    },
                    "parameter": {
                        "cluster_name": {
                            "type": "line",
                            "required": True,
                            "visible": True,
                        },
                        "server_id": {
                            "type": "line",
                            "required": True,
                            "visible": True,
                        },
                        "masters_addresses": {
                            "type": "dict",
                            "required": True,
                            "visible": True,
                        },
                        "hostname": {
                            "type": "line",
                            "required": False,
                            "visible": True,
                        },
                        "framework": {
                            "type": "array",
                            "required": True,
                            "visible": True,
                            "option": [
                                "marathon",
                            ],
                        },
                        "master_ip": {
                            "type": "line",
                            "required": True,
                            "visible": False,
                        },
                    },
                },
                "mesos slave": {
                    "module": "linux.mesos.slave",
                    "reference": {
                        "cn": "",
                        "en": """
### Description
Runs a Mesos Slave instance

### Parameters

*   **`masters_addresses`** (*required*): IPs/hostnames of the Mesos Master servers. If no hostname is given, the ip address will be used by default as hostname.

		example:
			@{master1.PrivateIpAddress}:    master1
			@{master2.PrivateIpAddress}:    master2
			@{master3.PrivateIpAddress}:

*   **`attributes`** (*required*): Mesos slave attributes (see Mesos documentation)

		example:
			subnet: web
			public: true
			rack:   rack-5
			asg:    asg0
			zone:   all
""",
                    },
                    "parameter": {
                        "masters_addresses": {
                            "type": "dict",
                            "required": True,
                            "visible": True,
                        },
                        "attributes": {
                            "type": "dict",
                            "required": True,
                            "visible": True
                        },
                        "slave_ip": {
                            "type": "line",
                            "required": True,
                            "visible": False,
                        },
                    },
                },


	}
}

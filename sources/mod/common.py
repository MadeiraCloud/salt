common = {
	'common'	:	{
		# handle archive
		'archive'	:	{
			'module'	:	'common.archive',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
extract an archive file

### Parameters

*   **`source`** (*required*): the archive file url

		example: http(s):///host/path/to/archive.tar.gz

	>note: currently supported archive format: tar, tgz, tar.gz, bz, bz2, tbz, zip (archive file must end with one of these extention name)
			local archive file `file://path/to/file` not supported in this version

*   **`path`** (*required*): the path to extract the archive

	>note: the path will be auto-created if it doesn't exist

*   **`checksum`** (*optional*): the url of the source checksum file or checksum value string, whose value (content) will be used to verify the integrity of the source archive, only support md5

		example:
			http(s):///host/path/to/checksum_file
			md5:md5_value_string

*   **`if-path-absent`** (*optional*): extract the archive only if none of the specified path exists, see blow

	> note: once the source archive is successfully extracted to the specified path, the opsagent will decide whether to re-fetch and extract the source archive depending on or not:
	- when `if-path-absent` specified:
		- if none of the specified paths exist, the archive will be re-fetched, until some paths exist
		- if some paths exists, the archive will only be re-fetched only if `checksum` is used and its value changes between rounds
	- when `if-path-absent` not used:
		- if `checksum` not used, the archive will be re-fetched in every round
		- if `checksum` used, thhe archive will be re-fetched if the checksum value changes between rounds
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'source'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True,
				},
				'checksum'	:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	False
				},
				'path'	:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				#'if-path-present'	:	{
				#	'type'		:	'array',
				#	'required'	:	False,
				#	'visible'	:	True
				#}
				'if-path-absent'	:	{
					'type'		:	'array',
					'required'	:	False,
					'visible'	:	True
				}
			}
		},

		# set the timezone
		'timezone'	:	{
			'module'	:	'common.timezone',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage the timezone

### Parameters

*   **`name`** (*required*): the timezone name

	example: Pacific/Tahiti

*   **`use-utc`** (*optional*): whether to use UTC for the hardware clock or not, by default ***`true`***
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'name'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'use-utc'		:	{
					'type'		:	'bool',
					'default'	:	True,
					'required'	:	False
				}
			}
		},

		# manage gem packages
		'gem'	:	{
			'module'	:	'common.gem.package',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage ruby gems

### Parameters

*	**`name`** (*required*): the package names and versions. You can specify multiple packages. The following values can be used for package version:
	- ***`<null>`*** *`default`*: ensure the package is installed. If not, it will install the latest version available of all GEM repos available
	- ***`<version>`***: ensure the package is installed, at the version specified. If the version in unavailable of all GEM repos available on the host, the state will fail
	- **`latest`**: ensure the package is installed at the latest version. If a newer version is available of all GEM repos available on the host, the package will upgrade automatically
	- **`removed`**: ensure the package is absent
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'name'	:	{
					'type'		:	'dict',
					'option'	:	['latest', 'removed'],	# autofill options to show in IDE
					'default'	:	'',			# the default value to show in IDE,
					'required'	:	True,
					'visible'	:	True
				}
			}
		},

		# manage npm packages
		'npm'	:	{
			'module'	:	'common.npm.package',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
                                        manage node.js package (requires npm 1.2 or higher)

### Parameters

*	**`name`** (*required*): the package names and versions. You can specify multiple packages. The following values can be used for package version:
	- ***`<null>`*** *`default`*: ensure the package is installed. If not, it will install the latest version available in all active NPM repos
	- ***`<version>`***: ensure the package is installed, at the specified version. If the version in unavailable in all active NPM repos on the host, the state will fail
	- **latest**: ensure the package is installed at the latest version. If a newer version is available in all active NPM repos on the host, the package will upgrade automatically
	- **removed**: ensure the package is absent

	>note: the specified packages will be installed as global packages (npm install --global)

* **`path`** (*optional*): the path where the packages should be installed to `$path/node_modules`
		>note:
			if ignored, the packages will be installed as global packages, usually `/usr/local/lib/node_modules/` (e.g. npm install --global)
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'name'	:	{
					'type'		:	'dict',
					'value'		:	['latest', 'removed'],	# values to show in IDE
					'default'	:	'',						# the default value of the item,
					'required'	:	True,
					'visible'	:	True
				},
				'path'	:	{
					'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				}
			}
		},

		# manage php packages with pear
		#'pear'	:	{
		#	'module'	:	'package.pear.package',
		#	'reference'	:	{
		#		'en'	:	'''''',
		#		'cn'	:	''''''
		#	},
		#	'parameter'	:	{
		#		'name'	:	{
		#			'type'		:	'dict',
		#			'value'		:	['latest', 'removed'],	# values to show in IDE
		#			'default'	:	'',			# the default value of the item
		#			'required'	:	True
		#		}
		#	}
		#},
		#'pecl.package'	:	{
		#	'module'	:	'package.pecl.package',
		#	'reference'	:	{
		#		'en'	:	'''''',
		#		'cn'	:	''''''
		#	},
		#	'parameter'	:	{
		#		'name'	:	{
		#			'type'	:	'dict',
		#			'value'		:	['latest', 'removed'],	# values to show in IDE
		#			'default'	:	'',			# the default value of the item
		#			'required'	:	True
		#		}
		#	}
		#},

		# manage python packages
		'pip'	:	{
			'module'	:	'common.pip.package',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage pip packages

### Parameters

*	**`name`** (*required*): the package names and versions. You can specify multiple packages. The following values can be used for package version:
	- ***`<null>`*** *`default`*: ensure the package is installed. If not, it will install the latest version available of all PIP repos activated
	- ***`<version>`***: ensure the package is installed, in the specified version. If the version in unavailable of all PIP repos activated on the host, the state will fail
	- **`latest`**: ensure the package is installed at the latest version. If a newer version is available of all PIP repos activated on the host, the package will upgrade automatically
	- **`removed`**: ensure the package is absent
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
				}
			}
		},

		# git repo
		'git'	:	{
			'module'	:	'common.git',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage a git repo

### Parameters

* **`path`** (*required* ): the path to clone the repo

		example: /var/www/html/mysite/

*   **`repo`** (*required*): the git repository uri

		example:
			/path/to/repo.git/
			file:///path/to/repo.git/
			http[s]://host[:port][path]
			ftp[s]://host[:port][path]
			ssh://[user@]host[:port]/~[user][path]
			git://[user@]host[:port]/~[user][path]
			rsync://host[:port][path]

* **`revision`** (*optional*): the revision to checkout

		example:
			specify a branch and keep it synced: master, develop
			specify a static tag - release-1.0
			specify a particular revision id - 8b1e0f7e499f9af07eed5ba6a3fc5490e72631b6

* **`ssh-key-file`** (*optional*): the path of the ssh keypair file

		example: /root/.ssh/id_rsa

* **`force`** (*optional*): force the checkout if there is conflict, by default ***`false`***

* **`user`** (*optional*): the username that performs the operation, by default ***`root`***
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'path'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'repo'		:	{
					'type'		:	'line',
					'required'	:	True
				},
				'revision'	:	{
					'type'		:	'line',
					'default'	:	'master',
					'required'	:	False
				},
				'ssh-key-file'	:	{
					'type'		:	'line',
					'required'	:	False
				},
				'force':	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False
				},
				'user':	{
					'type'		:	'line',
					'required'	:	False
				}
			}
		},

		# hg repo
		'hg'	:	{
			'module'	:	'common.hg',
			'distro'	:	None,
			'reference'	:	{
					'en'	:	'''
### Description
manage a hg repo

### Parameters

* **`path`** (*required* ): the path to clone the repo

		example: /var/www/html/mysite/

*   **`repo`** (*required*): the hg repository uri

		example:
			local/filesystem/path
			file://local/filesystem/path
			http://[user@]host[:port]/[path]
			https://[user@]host[:port]/[path]
			ssh://[user@]host[:port]/[path]

* **`revision`** (*optional*): the revision to checkout

		example:
			specify a branch and keep it synced: master, develop
			specify a static tag - release-1.0
			specify a particular revision id - 8b1e0f7e499f9af07eed5ba6a3fc5490e72631b6

* **`force`** (*optional*): force the checkout if there is conflict, by default ***`false`***

* **`user`** (*optional*): the username that performs the operation, by default ***`root`***
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'path'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'repo'		:	{
					'type'		:	'line',
					'required'	:	True
				},
				'revision'	:	{
					'type'		:	'line',
					'default'	:	'default',
					'required'	:	False
				},
				'force'		:	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False
				},
				'user'		:	{
					'type'		:	'line',
					'required'	:	False
				}
			}
		},

		# svn repo
		'svn'	:	{
			'module'	:	'common.svn',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage a svn repo

### Parameters

* **`path`** (*required* ): the path to checkout the repo

		example: /var/www/html/mysite/

* **`repo`** (*required*): the svn repository uri

		example:
			file://local/filesystem/path
			http://[user@]host[:port][path]
			https://[user@]host[:port][path]
			svn://[user@]host[:port][path]
			svn+ssh://[user@]host[:port][path]

* **`revision`** (*optional*): the revision to checkout

		example: HEAD, BASE, COMMITED, PREV, etc,. (ref: [Revision Specifiers](http://svnbook.red-bean.com/en/1.7/svn.tour.revs.specifiers.html))

* **`username`** (*optional*): the username of the svn server

* **`password`** (*optional*): the password of the svn user

* **`force`** (*optional*): force the checkout if there is conflict, by default ***`false`***

* **`user`** (*optional*): the username that performs the operation, by default ***`root`***
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'path'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'repo'		:	{
					'type'		:	'line',
					'required'	:	True
				},
				'revision'	:	{
					'type'		:	'line',
					'options'	:	['HEAD', 'BASE', 'COMMITED', 'PREV'],
					'default'	:	'HEAD',
					'required'	:	False

				},
				'username'	:	{
					'type'		:	'line',
					'required'	:	False
				},
				'password'	:	{
					'type'		:	'line',
					'required'	:	False
				},
				'force'		:	{
					'type'		:	'bool',
					'default'	:	False,
					'required'	:	False
				},
				'user'		:	{
					'type'		:	'line',
					'required'	:	False
				}
			}
		},

		# manage pytho virtualenv
		'virtualenv'	:	{
			'module'	:	'common.virtualenv',
			'distro'	:	None,
			'reference'	:	{
				'en'	:	'''
### Description
manage a python virtualenv

### Parameters

*   **`path`** (*required*): the environment path

*   **`python-bin`** (*optional*): the path the python interpreter to use

	>note:
			python2.5 will use the python2.5 interpreter to create the new environment.
			The default is the interpreter that virtualenv was installed with

*   **`requirements-file`** (*optional*): the python requirements file path, which will be used to configure this environment

*   **`system-site-packages`** (*optional*): whether to give the virtual environment access to the global site-packages or not, by default ***`true`***

*   **`extra-search-dir`** (*optional*): whether to always copy files rather than symlinking or not, by default ***`false`***
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'path'		:	{
					'type'		:	'line',
					'required'	:	True,
					'visible'	:	True
				},
				'python-bin'		:	{
					'type'		:	'line',
					'required'	:	False
				},
				'requirements-file'	:	{
					'type'		:	'line',
					'required'	:	False
				},
				'system-site-packages'		:	{
					'type'		:	'bool',
					'default'	:	True,
					'required'	:	False
				},
				'extra-search-dir'	:	{
					'type'		:	'array',
					'required'	:	False
				}
			}
		}
	}
}

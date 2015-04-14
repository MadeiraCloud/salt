meta = {
	'meta'	:	{
		# for comment
		'#'	:	{
			'module'	:	'meta.comment',
			'reference'	:	{
				'en'	:	'''
### Description
	Used for comments
				''',
				'cn'	:	''''''
			},
			'parameter'	:	{
				'comment'	:	{
				'type'		:	'line',
					'required'	:	False,
					'visible'	:	True
				}
			}
		},

		# for coordinate multi instances
		'wait'	:	{
			'module'	:	'meta.wait',
			'reference'	:	{
				'en'	:	'''
### Description
wait for remote state(s) to complete. If any is not done yet, it will block the host on the waiting state.

### Parameters

*   **`state`** (*required*): one or multiple remote states to be waited

		example:
			@{host.state.1}
					''',
					'cn'	:	''''''
				},
				'parameter'	:	{
					'state'	:	{
						'type'		:	'state',	# state is an array
						'required'	:	True,
						'visible'	:	True
					}
				}
			},

#			'reboot'	:	{
#				'module'	:	'meta.reboot',
#				'reference'	:	{
#					'en'	:	'''
#### Description
#    perform a host reboot, >note: do NOT reboot the host directly with cmd or script, which will be taken as the host crash
#					''',
#					'cn'	:	''''''
#				},
#				'parameter'	:	{
#					}
#				}
#			}
	}
}

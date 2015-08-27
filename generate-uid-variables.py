#!/usr/bin/python

'''Generate scripted effects and triggers for unique variables.'''

# Here's the deal.
#
# To store a reference to another scope,
# we can do so by generating a unique ID,
# and storing this ID in the entity that must refer to it.
#
# As a fundamental limit to the scripting engine,
# you can't re-use the same ID in different contexts,
# because while it is possible to compare variables between scopes,
# and between variables under different names in the same context,
# you can't compare variables with different names in different contexts.
#
# Hence to be useful, we need to have different variables for each context.
#
# Because we can't pass parameters in to scripted triggers or effects,
# we need a different trigger and effect per variable.
#
# Since this is non-trivial code,
# it's better to re-generate it when changed
# than have multiple versions which only differ by variable name
# to keep in sync.

import os


PREFIX = "da_"
VARIABLES = {"transfer_recipient_title_id": ('title', 'any_title')}

ASSIGN_ID_TEMPLATE = r'''

%(prefix)sassign_%(variable)s = {
	%(search_scope)s = {
		if = {
			limit = {
				AND = {
					# Title flag check necessary as unset value may be garbage
					has_title_flag = has_%(prefix)s%(variable)s
					# check if this ID > previous
					# (actually checks >=, but we assume it can't be equal
					check_variable = { which = %(prefix)s%(variable)s which = PREVPREV }
				}
			}
			PREVPREV = {
				set_variable = { which = %(prefix)s%(variable)s which = PREV }
			}
		}
	}
	change_variable = { which = %(prefix)s%(variable)s value = 1 }
	set_%(type)s_flag = has_%(prefix)s%(variable)s
}
'''
ID_SET_TEMPLATE = r'''

%(prefix)shas_%(variable)s = {
	has_%(type)s_flag = has_%(prefix)s%(variable)s
}
'''

for template, path in [(ASSIGN_ID_TEMPLATE, ('common', 'scripted_effects', PREFIX + 'generated_effects.txt')),
                       (ID_SET_TEMPLATE, ('common', 'scripted_triggers', PREFIX + 'generated_triggers.txt'))]:
	path = os.path.join(*path)
	if not os.path.exists(os.path.dirname(path)):
		os.makedirs(os.path.dirname(path))
	f = open(path, 'w')
	for variable, (type, search_scope) in VARIABLES.items():
		f.write(template % {'prefix': PREFIX,
		                    'variable': variable,
		                    'type': type,
		                    'search_scope': search_scope})

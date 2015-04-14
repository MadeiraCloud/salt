# -*- coding: utf-8 -*-
'''
Run Chef recipes

@author: Thibault BRONCHAIN
(c) 2014 - MadeiraCloud
'''


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


# Run client node
def client(server, client_key=None, config=None, arguments=[]):
    agd = {}
    agl = []
    if not server:
        return _invalid(comment="No server specified.")
    else:
        agd["server"] = server
    if client_key:
        agd["client_key"] = client_key
    if config:
        agd["config"] = config
    for a in arguments:
        if ("key" not in a): continue
        if a.get("value","") != "":
            agd[a["key"]] = a["value"]
        else:
            agl.append(a["key"])
    try:
        ret = __salt__['chef.client'](*agl,**agd)
        out = "%s\n%s"%(ret["stdout"],ret["stderr"])
        if ret.get("retcode",-1):
            comment = "Client ran with error(s) (code %s).\n"%(ret.get("retcode",-1))
            return _invalid(comment=comment,
                            stdout=out)
        else:
            comment = "Client ran without error.\n"
            return _valid(comment=comment,
                          stdout=out)
    except Exception as e:
        comment = "Error running chef client: %s.\n"%e
        return _invalid(comment=comment)

# Run solo node
def solo(config=None, recipe_url=None, override_runlist=None, arguments=[]):
    agd = {}
    agl = []
    if config:
        agd["config"] = config
    if recipe_url:
        agd["recipe-url"] = recipe_url
    if override_runlist:
        agd["override-runlist"] = override_runlist
    for a in arguments:
        if ("key" not in a): continue
        if a.get("value","") != "":
            agd[a["key"]] = a["value"]
        else:
            agl.append(a["key"])
    try:
        ret = __salt__['chef.solo'](*agl,**agd)
        out = "%s\n%s"%(ret["stdout"],ret["stderr"])
        if ret.get("retcode",-1):
            comment = "Receipe processed with error(s) (code %s).\n"%(ret.get("retcode",-1))
            return _invalid(comment=comment,
                            stdout=out)
        else:
            comment = "Recipe processed without error.\n"
            return _valid(comment=comment,
                          stdout=out)
    except Exception as e:
        comment = "Error running chef solo: %s\n"%e
        return _invalid(comment=comment)

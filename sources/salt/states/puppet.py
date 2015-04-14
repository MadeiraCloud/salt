# -*- coding: utf-8 -*-
'''
Run Puppet recipes

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


# Run puppet agent
def agent(server, arguments=[]):
    ags = [{"key":"agent"},
           {"key":"server","value":server}] + arguments
    return run(ags)


# Run configured Puppet round
def run(arguments=[]):
    ags = []
    for a in arguments:
        if ("key" not in a): continue
        if a.get("value"):
            ags.append("%s=%s"%(a["key"],a["value"]))
        else:
            ags.append(a["key"])
    try:
        ret = __salt__['puppet.run'](*ags)
    except Exception as e:
        return _invalid(comment="Error processing round.")
    else:
        out = "%s\n%s"%(ret["stdout"],ret["stderr"])
        if ret.get("retcode"):
            comment = "Round processed with error(s) (code %s).\n"%(ret["retcode"])
            return _invalid(comment=comment,
                            stdout=out)
        else:
            comment = "Round processed without error.\n"
            return _valid(comment=comment,
                          stdout=out)

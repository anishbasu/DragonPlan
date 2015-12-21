import re


def parseDependencies(reqs):
        if reqs.strip() == '':
            return []
        if re.search(r'and|or',reqs) is None:
            return prettify([re.match('([A-Z]+) ([A-Z]*\d{2,4}) Minimum Grade: ([A-F][+\-]?)',i).groups() for i in re.findall('([A-Z]+ [A-Z]*\d{2,4} Minimum Grade: [A-F][+\-]?)', reqs)])
        expression = filter(None,re.split('\(|\)', reqs.strip()))
        dep_tree = dict(op='and',var=[],children=[])
        for expr in expression:
            m = re.findall('(and|or)', expr)
            vars = prettify([re.match('([A-Z]+) ([A-Z]*\d{2,4}) Minimum Grade: ([A-F][+\-]?)',i).groups() for i in re.findall('([A-Z]+ [A-Z]*\d{2,4} Minimum Grade: [A-F][+\-]?)', expr)])
            if len(m) >= len(vars):
                dep_tree['op'] = m[0]
                dep_tree['var'] = dep_tree['var'] + vars
            else:
                dep_tree['children'].append(dict(op=m[0],var=vars))
        if len(expression) == 1:
            dep_tree['var'] = dep_tree['children'][0]['var']
            dep_tree['op'] = dep_tree['children'][0]['op']
            dep_tree['children'] = []
        return dep_tree

def prettify(vars):
        return map(lambda tup: dict(course=tup[0]+tup[1],min_grade=tup[2]), vars)

print parseDependencies("(CS 172 Minimum Grade: D or CS 133 Minimum Grade: D) or (SE 103 Minimum Grade: D and ECEC 301 Minimum Grade: D)")
print parseDependencies("CS 172 Minimum Grade: D or CS 133 Minimum Grade: D or SE 103 Minimum Grade: D or ECEC 301 Minimum Grade: D")
print parseDependencies("ECEC 301 Minimum Grade: D")
print parseDependencies("(CS 172 Minimum Grade: D or CS 133 Minimum Grade: D) or (SE 103 Minimum Grade: D and ECEC 301 Minimum Grade: D) or CS 133 Minimum Grade: D")
print parseDependencies(" ")


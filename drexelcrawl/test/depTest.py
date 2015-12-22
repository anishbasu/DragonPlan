import re


def parseDependencies(reqs):
        if reqs.strip() == '':
            return []
        if re.search(r'and|or',reqs) is None:
            return get_vars(reqs)
        expression = filter(None,re.split('\(|\)', reqs.strip()))
        dep_tree = dict(op='and',var=[],children=[])
        for expr in expression:
            m = re.findall('(and|or)', expr)
            vars = get_vars(expr)
            if len(m) >= len(vars):
                dep_tree['op'] = m[0]
                dep_tree['var'] = dep_tree['var'] + vars
            else:
                dep_tree['children'].append(dict(op=m[0],var=vars))
        print dep_tree
        if len(expression) == 1:
            dep_tree['var'] = dep_tree['children'][0]['var']
            dep_tree['op'] = dep_tree['children'][0]['op']
            dep_tree['children'] = []
        return dep_tree

def get_vars(expr):
        vars = [re.match('([A-Z]+)\s+([A-Z]*\d{2,4}[A-Z]*)\s+Minimum Grade:\s+([A-F][+\-]?)?',i).groups() for i in re.findall('([A-Z]+\s+[A-Z]*\d{2,4}[A-Z]*\s+Minimum Grade:\s+[A-F][+\-]?)', expr)]
        vars+= map(lambda tup: ('PE_'+tup[0].upper(),tup[1],tup[2]),[re.match('[A-Z]*\s+(\w+)\s+(\d+)\s+Placement Exam\s+Minimum Grade:\s+(\d+)',i).groups() for i in re.findall('([A-Z]*\s+\w+\s+\d+\s+Placement Exam\s+Minimum Grade:\s+\d+)',expr)])
        vars+=map(lambda tup: (tup[0],tup[1],'P'),[re.match('([A-Z]+)\s+([A-Z]*\d{2,4}[A-Z]*)',i).groups() for i in re.findall('([A-Z]+\s+[A-Z]*\d{2,4}[A-Z]*(?!\s+Minimum))',expr)])
        return map(lambda tup: dict(course=tup[0]+tup[1],min_grade=tup[2]), vars)

print parseDependencies("(CS 172 Minimum Grade: D or CS 133 Minimum Grade: D) or (SE 103 Minimum Grade: D and ECEC 301 Minimum Grade: D)")
print parseDependencies("CS 172 Minimum Grade: D or CS 133 Minimum Grade: D or SE 103 Minimum Grade: D or ECEC 301 Minimum Grade: D")
print parseDependencies("ECEC 301 Minimum Grade: D")
print parseDependencies("(CS 172 Minimum Grade: D or CS 133 Minimum Grade: D) or (SE 103 Minimum Grade: D and ECEC 301 Minimum Grade: D) or CS 133 Minimum Grade: D")
print parseDependencies("EDEX 542  Minimum Grade: C  and EDEX 544  Minimum Grade: C")
print parseDependencies("DU Math 101 Placement Exam   Minimum Grade: 061  or MATH 100  Minimum Grade: D")
print parseDependencies("CRHP 501S  and CRHP 502S  and CRHP 503S")


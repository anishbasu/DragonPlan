import pymongo
from scrapy.conf import settings
import items
import re
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class MongoPipeLine(object):

    def __init__(self):
        self.connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT'],
        )
        self.db = self.connection[settings['MONGODB_DB']]

    def process_item(self, item, spider):
        if type(item) is items.CourseItem:
            self.insertClass(item)
        if type(item) is items.CourseDescriptionItem:
            self.insertCourse(item)
        if type(item) is items.TermItem:
            self.insertTerm(item)
        # return item

    def close_spider(self, spider):
        self.connection.close()

    def insertCourse(self, item):
        course = dict(
            _id=item['course_code'],
            entry_type="course",
            course_code=item['course_code'],
            subject=item['subject'],
            number=item['number'],
            subject_id=item['subject_id'],
            college=item['college'][0],
            department=item['department'],
            title=item['title'],
            description=item['description'],
            credits=item['credits'].strip(),
            restrictions=item['restrictions'],
            pre_requisites=self.parseDependencies(item['pre_req']),
            pre_req_text = item['pre_req'],
            co_requisites=self.parseDependencies(item['co_req']),
            co_req_text = item['co_req'],
            repeat=item['repeat']
        )
        self.db['course'].save(course)
        print "course added:", course['_id']

    def insertTerm(self, item):
        term = dict(item)
        term['entry_type'] = "term"
        result = self.db['term'].insert_one(term)
        print "term added", result.inserted_id

    def parseDependencies(self, reqs):
        if reqs.strip() == '':
            return []
        if re.search(r'and|or', reqs) is None:
            return self.get_vars(reqs)
        expression = filter(None, re.split('\(|\)', reqs.strip()))
        dep_tree = dict(op='and', var=[], children=[])
        for expr in expression:
            m = re.findall('(and|or)', expr)
            vars = self.get_vars(expr)
            if len(m) >= len(vars):
                dep_tree['op'] = m[0]
                dep_tree['var'] = dep_tree['var'] + vars
            else:
                dep_tree['children'].append(dict(op=m[0], var=vars))
        if len(expression) == 1:
            dep_tree['var'] = dep_tree['children'][0]['var']
            dep_tree['op'] = dep_tree['children'][0]['op']
            dep_tree['children'] = []
        print "Dependency Tree Added:",dep_tree
        return dep_tree

    def get_vars(self,expr):
        vars = [re.match('([A-Z]+)\s+([A-Z]*\d{2,4}[A-Z]*)\s+Minimum Grade:\s+([A-F][+\-]?)',i).groups() for i in re.findall('([A-Z]+\s+[A-Z]*\d{2,4}[A-Z]*\s+Minimum Grade:\s+[A-F][+\-]?)', expr)]
        vars+= map(lambda tup: ('PE_'+tup[0].upper(),tup[1],tup[2]),[re.match('[A-Z]*\s+(\w+)\s+(\d+)\s+Placement Exam\s+Minimum Grade:\s+(\d+)',i).groups() for i in re.findall('([A-Z]*\s+\w+\s+\d+\s+Placement Exam\s+Minimum Grade:\s+\d+)',expr)])
        vars+=map(lambda tup: (tup[0],tup[1],'P'),[re.match('([A-Z]+)\s+([A-Z]*\d{2,4}[A-Z]*)',i).groups() for i in re.findall('([A-Z]+\s+[A-Z]*\d{2,4}[A-Z]*(?!\s+Minimum))',expr)])
        return map(lambda tup: dict(course=tup[0]+tup[1],min_grade=tup[2]), vars)



    def insertClass(self, item):
         _class = dict(
                _id=item['crn'],
                entry_type="class",
                subject=item['subject_id'],
                term=item['term_id'],
                code=item['course_code'],
                number=item['number'],
                instr_type=item['instr_type'],
                instr_method=item['instr_method'],
                section=item['sec'],
                crn=item['crn'],
                url=item['course_url'],
                days=item['days'][0] if item['days'][0] == 'TBA' or item[
                    'days'][0] == 'TBD' else item['days'].split(),
                time=item['time'],
                instructor=item['instr'],
                section_comments=item['sec_comments'],
                campus=item['campus']
            )
         self.db['class'].save(_class)
         print "class added", _class['_id']

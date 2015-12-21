# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc..org/en/latest/topics/items.html

from scrapy.item import Item,Field

class CourseItem(Item):
    subject_id = Field()
    term_id = Field()
    course_code = Field()
    number = Field()
    instr_type = Field()
    instr_method = Field()
    sec = Field()
    crn = Field()
    course_url = Field()
    days = Field()
    time = Field()
    instr = Field()
    sec_comments = Field()
    campus = Field()

class CourseDescriptionItem(Item):
    course_code = Field()
    subject = Field()
    subject_id = Field()
    college = Field()
    department = Field()
    title = Field()
    description = Field()
    credits = Field()
    restrictions = Field()
    pre_req = Field()
    co_req = Field()
    repeat = Field()

class TermItem(Item):
    url = Field()
    season = Field()
    yearBegin = Field()
    yearEnd = Field()
    full = Field()
    term_type = Field()
    term_id = Field()

class CourseInfoItem(Item):
    term_id = Field()
    subject = Field()
    college = Field()


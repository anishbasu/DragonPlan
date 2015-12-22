from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
import uuid, re
import settings

Base = declarative_base()

def db_connect():
    return create_engine('sqlite:///tms.db')

def create_tables(engine):
    Base.metadata.create_all(engine)

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

class Term(Base):
    __tablename__='term'
    season = Column(String)
    year_begin = Column(Integer)
    year_end = Column(Integer)
    full = Column(String)
    term_type = Column(String)
    id = Column(String, primary_key=True)

    def __init__(self,TermItem):
        self.season = TermItem.season
        self.year_begin = TermItem.year_begin
        self.year_end = TermItem.year_end
        self.full = TermItem.full
        self.term_type = TermItem.term_type
        self.id = TermItem.term_id

class Dependency(Base):
    __tablename__='dependency'
    id = Column(String(35), primary_key=True, unique=True)
    dependent_id=Column(String,ForeignKey('course.course_id'),primary_key=True)
    dependency_id=Column(String,ForeignKey('course.course_id'),primary_key=True)
    co_req = Column(Boolean)#True for Co Req, False for Pre-Req
    min_grade = Column(String)
    group = Column(Integer)
    dependency = relationship("Course", backref=backref("new_dependency"))
    dependent = relationship("Course",backref=backref("new_dependent"))

    def __init__(self,dependent=None,dependency=None,co_req=False,group=0):
        self.id = uuid.uuid4().hex
        self.dependent = dependent
        self.dependency = dependency
        self.co_req = co_req
        self.group = group

class Course(Base):
    __tablename__ = 'course'
    course_code = Column(String,primary_key=True)
    subject = Column(String)
    subject_id = Column(String)
    college = Column(String)
    department = Column(String)
    title = Column(String)
    description = Column(String)
    credits = Column(Float)
    restrictions = Column(String)
    requirements = relationship("Course", secondary="new_dependency")
    dependents = relationship("Course", secondary="new_dependent")
    repeatable = Column(String)

    def __init__(self,descItem,session):
        self.copyFromItem(descItem,session)

    def copyFromItem(self,descItem,session):
        self.course_code = descItem.course_code
        self.subject = descItem.subject
        self.subject_id = descItem.subject_id
        self.college = descItem.college
        self.department = descItem.department
        self.title = descItem.department
        self.description = descItem.description
        self.credits = descItem.credits
        self.restriction = descItem.restriction
        self.repeatable = descItem.repeat
        self.requirements = []
        initializeDeps(descItem.pre_req,False)
        initializeDeps(descItem.co_req,True)

    def initializeDeps(self, req,co_req,session):
        reqlist = re.split('([A-Z]+ \d{2,3} Minimum Grade: [A-F])', req)
        reqlist = sum([i.strip() for i in reqList],[])
        group = 0
        last = []
        for i in xrange(len(reqlist)):
            m = re.match("([A-Z]+) (\d{2,3}) Minimum Grade: (A-F)", reqlist[i])
            if m != None:
                last.append([m.group(0)+m.group(1),m.group(2)])
            else:
                if 'and' in reqlist[i]:
                    while len(last) != 0:
                        e = last.pop()
                        self.add_dependency(get_or_create(session,Course,course_code=e[0]), co_req, group, e[1])
                    group+=1;

        while len(last) != 0:
            e = last.pop()
            self.add_dependency(get_or_create(session,Course,course_code=e[0]), co_req, group, e[1])


    def add_dependency(self,dependency,co_req,group,min_grade):
        self.new_dependency.append(Dependency(self,dependency,co_req,group,min_grade))



class Class(Base):
    __tablename__='class'
    subject_id = Column(String)
    term_id = Column(String,ForeignKey('term.id'))
    term = relationship(
        Term,
        backref=backref('classes',
                       uselist=True,
                        cascade='delete,all')
    )
    course_code = Column(String, ForeignKey('course.course_code'))
    course = relationship(
        Course,
        backref=backref('sections',
                        uselist=True,
                        cascade='delete,all')
    )
    number = Column(Integer)
    instr_type = Column(String)
    instr_method = Column(String)
    sec = Column(Integer)
    crn = Column(Integer, primary_key=True)
    course_url = Column(String)
    days = Column(String)
    time = Column(String)
    exam_date = Column(String)
    exam_time = Column(String)
    campus = Column(String)
    instr = Column(String)
    sec_comments = Column(String)



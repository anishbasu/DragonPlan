# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import re
import drexelcrawl.items as models

class TermSpider(scrapy.Spider):
    name = "tms"
    allowed_domains = ["duapp2.drexel.edu"]
    start_urls = (
        'https://duapp2.drexel.edu/webtms_du/app',
    )
    crawledURLs = []
    crawledCourses = []
    order = []
    def parse(self, response):
        #Grab the Term Data
        terms = response.xpath('//div[@class="term"]/a')
        for term in terms:
            #Extract the term data
            name = term.xpath('text()').extract()[0]
            url = term.xpath('@href').extract()[0]
            attr = re.search(r'(\w+) (\w+) (\d{2})-(\d{2})',name)
            resultTerm = models.TermItem(url=url,season=attr.group(1),yearBegin = attr.group(3), yearEnd = attr.group(4), term_type = attr.group(2), full = name)
            resultTerm['term_id'] = resultTerm['season'][:2]+resultTerm['yearBegin']+resultTerm['term_type'][0][0]

            if url not in self.crawledURLs:
                #Crawl the terms URL to get the college listings
                self.crawledURLs.append(url)
                request = Request("https://"+self.allowed_domains[0]+url,self.parse_colleges)
                courseInfo = models.CourseInfoItem(term_id=resultTerm['term_id'])
                request.meta['first'] = True
                request.meta['general'] = courseInfo
                yield request

            yield resultTerm

    def parse_colleges(self, response):
        #Perform the Subject URL Crawl
        if response.meta['first'] == False:
            subjects = response.xpath('//div[@class="odd"]/a')+response.xpath('//div[@class="even"]/a')
            for subject in subjects:
                url = subject.xpath('@href').extract()[0]
                print "URL HERE:", url
                name = subject.xpath('text()').extract()
                courseInfo = response.meta['general']
                courseInfo['subject'] = name
                if url not in self.crawledURLs:
                    self.crawledURLs.append(url)
                    request = Request("https://"+self.allowed_domains[0]+url,callback=self.parse_courses)
                    request.meta['general'] = courseInfo
                    yield request
        #Only the function call from parse() will perform the sidebar crawl
        else:
            colleges = response.xpath('//div[@id="sideLeft"]/a')
            for college in colleges:
                name = college.xpath('text()').extract()
                url = college.xpath('@href').extract()[0]
                courseInfo = response.meta['general']
                courseInfo['college'] = name
                if url not in self.crawledURLs:
                    self.crawledURLs.append(url)
                    request = Request("https://"+self.allowed_domains[0]+url,self.parse_colleges)
                    request.meta['first'] = False
                    request.meta['general'] = courseInfo
                    yield request

    #Parsing the course listings in the course listings
    def parse_courses(self,response):
        gen_info = response.meta['general']
        courses = response.xpath('//tr[@class="odd"]|//tr[@class="even"]')
        for course in courses:
            info = course.xpath('./td[@valign]')
            if len(info) is not 0:
                info_txt = [''.join(i.xpath('./text()').extract()) for i in info]
                course_item = models.CourseItem(subject_id=info_txt[0],
                                        number=info_txt[1],
                                        instr_type=info_txt[2],
                                        instr_method=info_txt[3],
                                        sec=info_txt[4],
                                        instr=info_txt[7],
                                        term_id=gen_info['term_id'])

                course_item['course_code'] = course_item['subject_id']+course_item['number']
                crn = info.xpath('./p/a')[0]
                course_item['crn'] = crn.xpath('text()').extract()[0]
                course_item['course_url'] = crn.xpath('@href').extract()[0]
                days_col = course.xpath('./td[@colspan=2]/table/tr')
                course_item['days'] = days_col[0].xpath('./td[1]/text()').extract()[0]
                course_item['time'] = days_col[0].xpath('./td[2]/text()').extract()
                #Course Description
                course_desc = None
                if course_item['course_code'] not in self.crawledCourses:
                    course_desc = models.CourseDescriptionItem(course_code = course_item['course_code'],
                                                              subject = gen_info['subject'],
                                                               number = course_item['number'],
                                                              college = gen_info['college'],
                                                               subject_id = info_txt[0],
                                                            title=info_txt[6]
                                                              )
                    self.crawledCourses.append(course_item['course_code'])

                #Go to course URl for additional info
                if course_item['course_url'] not in self.crawledURLs:
                    self.crawledURLs.append(course_item['course_url'])
                    request = Request("https://"+self.allowed_domains[0]+course_item['course_url'],callback=self.extended_info)
                    request.meta['course'] =  course_item
                    request.meta['description'] = course_desc
                    yield request


    def extended_info(self,response):
        course_item = response.meta['course']
        course_desc = response.meta['description']
        sec_cmnts = response.xpath('//td[contains(text(),"Section Comments")]/following-sibling::td[1]/table/tr/td/text()').extract()
        course_item['sec_comments'] = sec_cmnts
        course_item['campus'] = response.xpath('//td[text()="Campus"]/following-sibling::td[1]/text()').extract()[0]
        yield course_item
        if course_desc is not None:
            desc_rows = response.xpath('//table[@class="descPanel"]/tr[2]/td')
            points = desc_rows.xpath('./div[@class="subpoint"]/text()').extract()
            course_desc['description'] =  desc_rows.xpath('./div[@class="courseDesc"]/text()').extract()
            course_desc['credits'] = points[0]
            course_desc['department'] = points[2]
            course_desc['restrictions']= self.parseRestrictions(response)
            reqs = desc_rows.xpath('./div[contains(.,"Requisites:")]')
            course_desc['co_req'] = ''.join(reqs[0].xpath('.//text()').extract()[1:]).strip()
            course_desc['pre_req'] = ''.join(reqs[1].xpath('.//text()').extract()[1:]).strip()
            course_desc['repeat'] = points[5]
            yield course_desc

    def parseRestrictions(self,response):
        restRows = response.xpath('//div[@class="subpoint1"]|//div[@class="subpoint2"]').xpath('./text()').extract()
        if len(restRows) == 0:
            return []
        restrictions = []
        category = dict()
        for i in range(len(restRows)):
            if restRows[i].startswith(' -') == False:
                category = {}
                category['name']=restRows[i]
                category['criteria']=[]
                i+=1
                while i <len(restRows) and restRows[i].startswith(' -'):
                    category['criteria'].append(restRows[i][3:])
                    i+=1
                restrictions.append(category)
                i-=1
        return restrictions


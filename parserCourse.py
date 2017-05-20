#! /usr/bin/env python
# -*-coding:utf-8-*-
from bs4 import BeautifulSoup
from bs4 import element
import re


def analyCourse(htmlPage):
    # 7 days with 12 lessons everyday
    # courseList = [[[] for x in xrange(12)]for x in xrange(7)]
    #
    # indew:meaning,0:周几(1-7),1:第几节(1-12),2:课名,3:上课时间,4:教师名,5:地点
    courseList = []
    # 1 is course name, 2 is time, 3 is teacher , 4 is classroom
    # some course may not have classroom
    ROOMINDEX = 4
    soup = BeautifulSoup(htmlPage, "html.parser")
    tagTable = soup.find('table', id='Table1')  # the table contain course
    # print tagTable.prettify();
    # the <tr> contain <td> but contain some space string
    tbodyContents = tagTable.tbody.contents
    # only want <tr>
    tbodyContents = filter(lambda x: type(x) == element.Tag, tbodyContents)
    # print tbodyContents[0]
    # course time
    timeRule = ur"第\d+-\d+周\|\d节\/周|周[一二三四五六日]第[,\d]+节{第[-\d]+周[\|单双周]*}"
    # timeRule = ur"第\d+-\d+周\|\d节\/周|周[一-六日]第[,\d]+节{.*?}"  # course time
    # course name & teacher & classroom
    # nameAndRoomRule = ur">([\/\u4e00-\u9fa5]+\d*)<"
    nameAndRoomRule = ur"[\u4e00-\u9fa5]+[\/\u4e00-\u9fa5]*\d*"
    digitRoomRule = ur">\d+"  # some classroom like 340303 is only digit ,use > to label
    # regular rule of course
    rule = timeRule + ur"|" + nameAndRoomRule + ur"|" + digitRoomRule
    coursePattern = re.compile(rule)
    # see tbodyContents, 2:第1节,3:第2节, ... 13:第12节 , traverse according to
    # lesson number
    for lessonN in xrange(2, len(tbodyContents)):
        lessonIndex = lessonN - 1
        # only want <td>
        trContent = filter(
            lambda x: type(x) == element.Tag, tbodyContents[lessonN].contents)
        rowN = 0  # the nubmber N row of trContent
        # find the first row of lesson
        while rowN < len(trContent):
            if re.findall(r">第\d+节</td>", str(trContent[rowN])):
                rowN += 1
                break
            rowN += 1
        # begin to analyze course
        row1stOfLesson = rowN  # the table uses row to represent weekday
        dayN = 1  # 0:Monday 1:Tuesday ... 6:Sunday
        # traverse from Monday to Sunday
        for rowN in xrange(row1stOfLesson, len(trContent)):
            # if today there is no course this lesson number,it will be only
            # &nbsp;
            if len(trContent[rowN].text) == 1:
                dayN += 1
                continue
            resultList = coursePattern.findall(unicode(trContent[rowN]))
            # print resultList
            # exit(0)
            messN = 0  # message number N
            result_len = len(resultList)
            for ix in xrange(0, result_len):
                result = resultList[ix]
                messN += 1
                if messN == 1:
                    courseList.append([dayN, lessonIndex])
                if messN == ROOMINDEX:
                    # if it is a classroom with only digit
                    if re.findall(digitRoomRule, unicode(result)):
                        result = result[1:]  # remove ">"
                    # if it is a classroom with Chinese and digit
                    elif re.findall(ur"[\u4e00-\u9fa5]+\d+", unicode(result)):
                        pass
                    # only 4 element ,so it's classroom
                    elif ix + 1 == result_len:
                        pass
                    # this element and next element is only chinese,
                    # so it's classroom
                    elif ix + 1 < result_len and re.findall(ur">[\u4e00-\u9fa5]+<", unicode(result)) and re.findall(ur">[\u4e00-\u9fa5]+<", unicode(result)):
                        pass
                    # the course don't have classroom
                    else:
                        messN = 1  # it is the first message of a course
                        courseList.append([dayN, lessonIndex])
                courseList[len(courseList) - 1].append(result.encode('utf-8'))
                if messN == ROOMINDEX:
                    messN = 0
            dayN += 1
    testPrint(courseList)


def testPrint(courseList):
    print 'day', 'N', '\t', 'course', '\t\t', 'time', '\t\t\t', 'teacher', '\t\t', 'classroom'
    for course in courseList:
        for x in course:
            print x, '\t',
        print ' '

if __name__ == '__main__':
    # htmlPage = open("./course.html")
    htmlPage = open("./course2.html")
    analyCourse(htmlPage)

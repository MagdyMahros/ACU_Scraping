"""Description:

    * author: Awwal Mohammed
    * company: Fresh Futures/Seeka Technologies
    * position: IT Intern
    * date: 09-10-20
    * description:This program extracts the corresponding course details and tabulate it.
"""
import time
from pathlib import Path
from selenium import webdriver
import bs4 as bs4
import requests
import os
import csv

from OneEducationRTOScrape.CustomMethods import DurationConverter


def get_page(url):
    """Will download the contents of the page using the requests library.
    :return: a BeautifulSoup object i.e. the content of the webpage related to the given URL.
    """
    # noinspection PyBroadException,PyUnusedLocal
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return bs4.BeautifulSoup(r.content, 'html.parser')
    except Exception as e:
        pass
    return None


# selenium web driver
# we need the Chrome driver to simulate JavaScript functionality
# thus, we set the executable path and driver options arguments
# ENSURE YOU CHANGE THE DIRECTORY AND EXE PATH IF NEEDED (UNLESS YOU'RE NOT USING WINDOWS!)
option = webdriver.ChromeOptions()
option.add_argument(" - incognito")
option.add_argument("headless")
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, chrome_options=option)

# read the url from each file into a list
course_links_file_path = Path(os.getcwd().replace('\\', '/'))
course_links_file_path = course_links_file_path.parent.__str__() + '/CourseLinks/course_links_file'
course_links_file = open(course_links_file_path, 'r')

# the csv file we'll be saving the courses to
csv_file_path = Path(os.getcwd().replace('\\', '/'))
csv_file = csv_file_path.__str__() + '/CourseData/course_data.csv'

# MAIN ROUTINE
all_courses_info = []
course_links = []
addresses = {'Kelliher': '99 Kelliher Road, RICHLANDS QLD 4077',
             'Gold Coast': '2 Balmoral Avenue, BUNDALL QLD 4217'}

for each_url in course_links_file:
    course_data = dict()
    browser.get(each_url)
    pure_url = each_url.strip()
    each_url = browser.page_source

    soup = bs4.BeautifulSoup(each_url, 'html.parser')
    time.sleep(1)
    if soup.find('h2', class_='et_pb_slide_title'):  # check if the course page has a valid title

        # EXTRACT TITLE
        h2 = soup.find('h2', class_='et_pb_slide_title')
        title = h2.find('a')
        if title:
            title = title.contents[0]
        else:
            title = h2.contents[0]

        # EXTRACT DESCRIPTION
        div = soup.find_all('div', class_='et_pb_text_inner')
        time.sleep(0.5)
        # print(div, '\n')
        if div:
            for i in div:
                p = i.find_next('p')
                # print(p.contents)
                if "OVERVIEW" in i.find_next('strong').contents[0]:
                    course_data['Description'] = p.contents[0]

        # EXTRACT REMARKS
        div = soup.find_all('div', class_='et_pb_text_inner')
        time.sleep(0.5)
        # print(div, '\n')
        if div:
            for i in div:
                h1 = i.find_next('strong')
                if h1:
                    if "ENTRY REQUIREMENTS" in h1.contents[0]:
                        p = i.find_next('p')
                        course_data['Prerequisite_1'] = p.contents[0]

        # EXTRACT DURATION
        div = soup.find_all('div', class_='et_pb_text_inner')
        time.sleep(0.5)
        # print(div, '\n')
        if div:
            for i in div:
                h1 = i.find_next('strong')
                if h1:
                    if "DURATION" in h1.contents[0]:
                        all_p = i.find_all('p')
                        if all_p:
                            p = all_p[1].contents[0]
                            if p:
                                course_data['Duration (Algorithmic Guesstimate)'] = DurationConverter.convert_duration(p)
                                course_data['Duration (Raw)'] = p

        # EXTRACT COURSE FEES
        div = soup.find_all('div', class_='et_pb_text_inner')
        time.sleep(0.5)
        # print(div, '\n')
        if div:
            for i in div:
                all_p = i.find_all('p')
                if all_p:
                    for p in all_p:
                        p_main = p.find_next('strong')
                        if p_main:
                            if "Fee" in p.find_next('strong').contents[0]:
                                ul = p.find_next_sibling('ul')
                                if ul:
                                    li = ul.find('li').contents[0]
                                    if li:
                                        course_data['Local Fees'] = li

        course_data['University'] = '1Education'
        course_data['RTO Code'] = 'RTO6639'
        course_data['Courses'] = title
        course_data['Website'] = pure_url
        course_data['Address'] = '99 Kelliher Road, RICHLANDS QLD 4077'
        course_data['Country'] = 'Australia'
        course_data['City'] = 'Brisbane'
        course_data['State'] = 'Queensland'
        course_data['All_text'] = soup.text.replace('\n', '').strip()
        course_data['Currency'] = 'AUD'

        all_courses_info.append(course_data)

print(*all_courses_info, sep='\n')

# tabulate our data
course_dict_keys = set().union(*(d.keys() for d in all_courses_info))

with open(csv_file, 'w', encoding='utf-8', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, course_dict_keys)
    dict_writer.writeheader()
    dict_writer.writerows(all_courses_info)

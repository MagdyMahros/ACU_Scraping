"""Description:
    * author: Awwal Mohammed
    * refactored and edited by: Magdy Abdelkader
    * company: Fresh Futures/Seeka Technologies
    * position: IT Intern
    * date: 12-10-20
    * description:This program extracts the corresponding course details and tabulate it.
"""
import csv
import re
import time
from pathlib import Path
from selenium import webdriver
import bs4 as bs4
from bs4 import Comment
import requests
import os


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
option.add_argument('--no-sandbox')
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, options=option)

# read the url from each file into a list
course_links_file_path = Path(os.getcwd().replace('\\', '/'))
course_links_file_path = course_links_file_path.__str__() + '/acu_research_links_file.txt'
course_links_file = open(course_links_file_path, 'r')


# the csv file we'll be saving the courses to
csv_file_path = Path(os.getcwd().replace('\\', '/'))
csv_file = csv_file_path.__str__() + '/ACU_bachelors.csv'

course_data = dict()
course_data_all = []
for each_url in course_links_file:
    browser.get(each_url)
    pure_url = each_url.strip()
    each_url = browser.page_source

    soup = bs4.BeautifulSoup(each_url, 'html.parser')
    time.sleep(1)

    # COURSE URL
    course_data['Website'] = pure_url

    # COURSE TITLE
    if soup.find('header', class_='col-md-12 desktop-width'):  # check if the course page has a valid title
        course_title = soup.find('header', class_='col-md-12 desktop-width').text
        course_data['Course'] = course_title.strip().replace('\n', '')
    time.sleep(1)

    # STUDY_MODE
    h3 = soup.find('h3')
    if h3:
        course_data['Study_Mode'] = h3.text

    # AVAILABILITY and LOCATION
    div1 = soup.find('div', class_='box__information--gray box--courses')
    if div1:
        div2 = div1.find('div', class_='col-xs-12 col-sm-6 col-md-6 col-lg-6')
        if div2:
            div3 = div2.find('dl', class_='row')
            if div3:
                dt_all = div3.find_all('dt', class_='col-sm-5 col-md-4')
                dd_all = div3.find_all('dd', class_='col-sm-7 col-md-8')
                dt_items = []
                dd_items = []
                if dt_all and dd_all:
                    for some_dt in dt_all:
                        dt_items.append(some_dt.text)
                    for some_dd in dd_all:
                        dd_items.append(some_dd.text)
                    for key in dt_items:
                        for value in dd_items:
                            course_data[key] = value
                            dd_items.remove(value)
                            break

    # PREREQUISITE_1 (ATAR , and a few other bundled data)
    div1 = soup.find_all("div", {"class": "col-xs-12 col-sm-6 col-md-6 col-lg-6"})[1]
    if div1:
        dl = div1.find('dl', class_='row')
        if dl:
            dt_all = dl.find_all('dt', class_='col-sm-6 col-md-5')
            dd_all = dl.find_all('dd', class_='col-sm-6 col-md-7')
            if dt_all and dd_all:
                dt_all_text = []
                dd_all_text = []
                for each_dt in dt_all:
                    dt_all_text.append(each_dt.text)
                for each_dd in dd_all:
                    temp_dd_list = []
                    p_dd = each_dd.find('p')
                    if p_dd:
                        temp_dd = []
                        for i in p_dd:
                            if not isinstance(i, bs4.NavigableString):
                                if i.next_sibling == None:
                                    temp_dd.append(i.text)

                                elif i.next_sibling != None:
                                    temp_dd.append(i.text)
                                    temp_dd.append(i.next_sibling)
                            elif isinstance(i, bs4.Tag):
                                temp_dd.append(i.name.__str__())
                            else:
                                temp_dd.append('.')
                        temp_dd = ' '.join(temp_dd)
                        dd_all_text.append(temp_dd)
                    ul_dd = each_dd.find('ul', class_='ret-negated')
                    if ul_dd:
                        li = ul_dd.find_all('li', class_='no_bullet')
                        if li:
                            x1 = [i.text for i in li]
                            x2 = ' '.join(x1)
                            dd_all_text.append(x2)
                for key in dt_all_text:
                    for value in dd_all_text:
                        course_data[key] = value
                        dd_all_text.remove(value)
                        break

    # COURSE START DATE INTERNATIONAL
    if soup('div', {'id': 'course--start-dates--international'}):
        div1 = soup.findAll('div', {'id': 'course--start-dates--international'})[0]
        if div1:
            div2 = div1.find('div', class_='col-md-9')
            if div2:
                all_ul = div2.find_all('ul')
                brisbane_inter_start_date = []
                melbourne_inter_start_date = []
                north_sydney_inter_start_date = []
                all_inter_start_date = []
                if all_ul:
                    for ul in all_ul:
                        li = ul.find('li')
                        if li:
                            for text in li(text=lambda text: isinstance(text, Comment)):
                                text.extract()
                                li_list = li.text
#                             li_list = [x.__str__() for x in li]
                            all_inter_start_date.append(li_list)

                try:
                    course_data['Brisbane_International_Start_Date'] = \
                        all_inter_start_date[0].replace('\n','')
                except IndexError:
                    course_data['Brisbane_International_Start_Date'] = 'null'
                try:
                    course_data['Melbourne_International_Start_Date'] = \
                        all_inter_start_date[1].replace('\n','')
                except IndexError:
                    course_data['Melbourne_International_Start_Date'] = 'null'
                try:
                    course_data['North_Sydney_International_Start_Date'] = \
                        all_inter_start_date[2].replace('\n','')
                except IndexError:
                    course_data['North_Sydney_International_Start_Date'] = 'null'

    # COURSE DESCRIPTION
    if soup("div", {"id": "course--description--domestic"}):
        div1 = soup.find_all("div", {"id": "course--description--domestic"})[0]
        if div1:
            div2 = div1.find('div', class_='col-md-9 course-info__details')
            if div2:
                all_p = div2.find_all('p')
                if all_p:
                    all_p_list = [i.text for i in all_p]
                    all_p_list_text = ' '.join(all_p_list).strip()
                    course_data['Description'] = all_p_list_text

    # DOMESTIC COURSE PRICE
    div1 = soup.find_all('div', id='course--costs--domestic')
    if div1:
        for div_n in div1:
            div_x = div_n.find('div', class_='col-md-9 course-info__details')
            if div_x:
                ul = div_x.find('ul', class_='list-unstyled')
                if ul:
                    li = ul.find_all('li', class_='no_bullet')
                    if li:
                        dom_costs_list = [' ']
                        for li_p in li:
                            costs_domestic = li_p.contents.__str__().strip()
                            if costs_domestic:
                                costs_domestic = li_p.get_text().strip()
                                dom_costs_list.append(costs_domestic)
                        dom_costs = ' '.join(dom_costs_list)
                        print('DOMESTIC COURSE PRICE: ', dom_costs.strip().replace('\n', '').replace('<', '').replace('>', ''))
                        course_data['Domestic_Course_Price'] = dom_costs.strip()

    # INTERNATIONAL COURSE PRICE
    div1 = soup.find_all('div', id='course--costs--international')
    if div1:
        for div_n in div1:
            div_x = div_n.find('div', class_='col-md-9')
            if div_x:
                ul = div_x.find('ul', class_='no_bullet')
                if ul:
                    li = ul.find_all('li', class_='no_bullet')
                    if li:
                        int_costs_total = [' ']
                        int_costs_firstYear = [' ']
                        int_costs_Unit = [' ']
                        for index, li_p in enumerate(li):
                            if index == 0:
                                costs_Unit = li_p.contents.__str__().strip()
                                if costs_Unit:
                                    costs_Unit = li_p.get_text().strip()
                                    int_costs_Unit.append(costs_Unit)
                            elif index == 1:
                                costs_firstYear = li_p.contents.__str__().strip()
                                if costs_firstYear:
                                    costs_firstYear = li_p.get_text().strip()
                                    int_costs_firstYear.append(costs_firstYear)
                            elif index == 2:
                                costs_total = li_p.contents.__str__().strip()
                                if costs_total:
                                    costs_total = li_p.get_text().strip()
                                    print(costs_total)
                                    int_costs_total.append(costs_total)
                        int_costs_total = ' '.join(int_costs_total)
                        int_costs_firstYear = ' '.join(int_costs_firstYear)
                        int_costs_Unit = ' '.join(int_costs_Unit)
#                         print('INTERNATIONAL COURSE PRICE: ', int_costs.strip().replace('\n', '').replace('<', '').replace('>', ''))
                        course_data['International unit cost'] = int_costs_Unit.strip()
                        course_data['International first year cost'] = int_costs_firstYear.strip()
                        course_data['International total cost'] = int_costs_total.strip()

    #CAREER PATH
    career_path_div = soup.find('div', id='course--career--domestic')
    if career_path_div:
        career_path_div1 = career_path_div.find('div', class_='col-md-9 course-info__details')
        if career_path_div1:
            career_path = ['']
            p = career_path_div1.find('p')
            ul = career_path_div1.find('ul')
            if ul:
                li = ul.find_all('li')
                if li:
                    for element in li:
                        one_career = element.contents.__str__().strip()
                        if one_career:
                            one_career = element.get_text().strip()
                            career_path.append(one_career)
            elif p and not ul:
                careerP = p.contents.__str__().strip()
                if careerP:
                    careerP = p.get_text().strip()
                    career_path.append(careerP)
            career_path = ' '.join(career_path)
            course_data['Career_path'] = career_path.strip()
    course_data = {str(key).strip().replace(':', '').replace('\n', ''): str(item).strip().replace('\n', '') for key, item in course_data.items()}
    course_data_all.append(course_data)

print(*course_data_all, sep='\n')

# tabulate our data
course_dict_keys = set().union(*(d.keys() for d in course_data_all))

with open(csv_file, 'w', encoding='utf-8', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, course_dict_keys)
    dict_writer.writeheader()
    dict_writer.writerows(course_data_all)

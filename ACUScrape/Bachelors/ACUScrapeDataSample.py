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
import copy
import DurationConverter
import TemplateData


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

course_data = {'University': 'Australian Catholic University', 'Course_Lang': 'English', 'Currency': 'AUD',
               'Full_Time': '', 'Part_Time': '', 'Availability': '', 'Currency_Time': '', 'Study_Mode': '',
               'Int_Fees': '', 'Local_Fees': '', 'Website': '', 'Course': '', 'Description': '', 'Prerequiste_1': '', 
               'Prequisite_1_grade':'', 'Mode_of_Study': '', 'City': '', 'Study_Type': '', 'Online_Only': 'No', 
               'Blended': '', 'Online': '', 'Offline': '', 'Distance': 'Blended', 'Int_Description': '', 'Level_Code': '', 'Course_Level': ''}

possible_cities = {'ballarat': 'Ballarat',
                   'blacktown': 'Blacktown',
                   'brisbane': 'Brisbane',
                   'canberra': 'Canberra',
                   'melbourne': 'Melbourne',
                   'strathfield': 'New South Wales',
                   'new south wales': 'New South Wales',
                   'north sydney': 'North Sydney'}

course_data_all = []
level_key = TemplateData.level_key  # dictionary of course levels

faculty_key = TemplateData.faculty_key  # dictionary of course levels

for each_url in course_links_file:
    actual_cities = []
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
    if course_data['Course'] == '':  # check elsewhere if this code doesn't fetch the title
        if soup.find('header', class_='banner-header-bg'):  # check if the course page has a valid title
            header = soup.find('header', class_='banner-header-bg')
            if header:
                div1 = header.find('div', class_='banner-header')
                if div1:
                    h1 = div1.find('h1')
                    if h1:
                        course_data['Course'] = h1.get_text()

    

    # STUDY_MODE
    if soup("div", {"id": "course--availability--domestic"}):
        div1 = soup.find("div", {"id": "course--availability--domestic"})
        if div1:
            div2 = div1.find('div', class_='col-md-9 course-info__details')
            if div2:
                ul = div2.find('ul')
                if ul:
                    availability = []
                    for each_li in ul:
                        li = each_li.find('strong')
                        if li:
                            availability_mode = li.__str__().strip()\
                                .replace('<strong>', '')\
                                .replace('</strong>', '')\
                                .replace('-1', '').strip()
                            availability.append(availability_mode.lower())
                            if 'online' in availability:
                                course_data['Online'] = 'Yes'
                                course_data['Study_Type'] = 'Online'
                                course_data['Study_Mode'] = '2'
                            if 'online' not in availability:
                                course_data['Offline'] = 'Yes'
                                course_data['Study_Type'] = 'Offline'
                                course_data['Study_Mode'] = '1'
                            if 'online only' in availability:
                                course_data['Online_Only'] = 'Yes'
                                course_data['Study_Type'] = 'Online Only'
                                course_data['Study_Mode'] = '2'
                            if 'attendance' in availability and 'multi-mode' in availability:
                                course_data['Study_Type'] = 'Mixed'
                                course_data['Study_Mode'] = '3'
                    # print('NEW STUDY MODE: ', course_data['Study_Mode'], '\t', availability)

    # AVAILABILITY and LOCATION (and some other bundled data)
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
                            temp_key_var = key.lower()
                            temp_value_var = value.lower()

                            # AVAILABILITY
                            # only availability will be extracted here since Madgy is doing other data
                            if "available to" in temp_key_var:
                                if 'domestic students only' in temp_value_var:
                                    course_data['Availability'] = 'D'
                                elif 'international students only' in temp_value_var:
                                    course_data['Availability'] = 'I'
                                elif 'international' in temp_value_var and 'domestic' in temp_value_var:
                                    course_data['Availability'] = 'A'
                                else:
                                    course_data['Availability'] = 'N'
                            # print('AVAILABILITY B1: ', course_data['Availability'])

                            # LOCATION/CITY
                            for i in possible_cities:
                                if i in temp_value_var:
                                    actual_cities.append(possible_cities[i])
                                else:
                                    if 'online only' in temp_value_var:
                                        print('this course is online only')
                            # print('CITY/LOCATION: ', actual_cities)
                            course_data[key] = value
                            dd_items.remove(value)
                            break

    # DURATION, DURATION_TIME, ATAR , and a few other bundled data
    div1 = soup.find_all("div", {"class": "col-xs-12 col-sm-6 col-md-6 col-lg-6"})[1]
    if div1:
        dl = div1.find('dl', class_='row')
        if dl:
            dt_all = dl.find_all('dt', class_='col-sm-6 col-md-5')
            dd_all = dl.find_all('dd', class_='col-sm-6 col-md-7')
            if dt_all and dd_all:
                dt_all_text = []
                dd_all_text = []
                grades_list = []
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
                            #Prequisite1_grade
                            x1 = [i.text for i in li]
                            x2 = ' '.join(x1)
                            temp = re.findall(r'\d+\.\d+|\d+/\d+', x2)
                            res = list(map(str, temp))
                            for index, number in enumerate(res):
                                    if index == 0:
#                                         print(number)
                                        grades_list.append(number)
                            grades_list = ' '.join(grades_list)
                            # print(grades_list)
                            course_data['Prequisite_1_grade'] = grades_list
                for key in dt_all_text:
                    for value in dd_all_text:
                        for value in dd_all_text:    
                            temp_key_var2 = key.lower()
                            temp_value_var2 = value.lower()
                            temp_pattern = ''
                            duration_time = ''
                            if 'duration' in temp_key_var2:
                                # MODE OF STUDY (PART_TIME/FULL_TME) ======================================
                                if 'full-time' in temp_value_var2:
                                    course_data['Mode_of_Study'] = 'Full Time'
                                    course_data['Full_Time'] = 'Yes'
                                if 'part-time' in temp_value_var2:
                                    course_data['Mode_of_Study'] = 'Part Time'
                                    course_data['Part_Time'] = 'Yes'
                                if 'full-time' in temp_value_var2 and 'part-time' in temp_value_var2:
                                    course_data['Mode_of_Study'] = 'Full Time / Part Time'
                                
                                # DURATION + DURATION_TIME =============================================
                                # print('Current Duration: ', value)
                                if 'year' in value.lower():
                                    value_conv = DurationConverter.convert_duration(value)
                                    duration = float(''.join(filter(str.isdigit, str(value_conv)))[0])
                                    duration_time = 'Years'
                                    # print('FILTERED DURATION + DURATION_TIME: ' + str(duration) + ' ' + duration_time)
                                    course_data['Duration'] = duration
                                    course_data['Duration_Time'] = duration_time
                                elif 'month' in value.lower() and 'year' not in value.lower():
                                    value_conv = DurationConverter.convert_duration(value)
                                    duration = float(''.join(filter(str.isdigit, str(value_conv)))[0])
                                    duration_time = 'Months'
                                    # print('FILTERED DURATION + DURATION_TIME: ' + str(duration) + ' ' + duration_time)
                                    course_data['Duration'] = duration
                                    course_data['Duration_Time'] = duration_time
#                         print('CUR KEY AND VALUE: ', key, value)
                        dd_all_text.remove(value)
                        break

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

    # DOMESTIC FEES
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
                        # print('DOMESTIC COURSE PRICE: ',
                        #       dom_costs.strip().replace('\n', '').replace('<', '').replace('>', ''))
                        dom_costs = dom_costs.strip().lower()
                        currency_pattern = "(?:[\£\$\€]{1}[,\d]+.?\d*)"
                        if 'average first year fee' in dom_costs and 'unit' not in dom_costs:
                            dom_costs_final = ''.join(re.findall(currency_pattern, dom_costs)).replace('$', '')
                            course_data['Local_Fees'] = dom_costs_final
                        else:
                            course_data['Local_Fees'] = '0'  # some of the course won't charge local students

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
                        int_costs_firstYear = [' ']
                        for index, li_p in enumerate(li):
                            if index == 1:
                                costs_firstYear = li_p.contents.__str__().strip()
                                if costs_firstYear:
                                    costs_firstYear = li_p.get_text().strip()
                                    int_costs_firstYear.append(costs_firstYear)
                        int_costs_firstYear = ' '.join(int_costs_firstYear)
#                         print('INTERNATIONAL COURSE PRICE: ', int_costs.strip().replace('\n', '').replace('<', '').replace('>', ''))
                        int_costs = int_costs_firstYear.strip().lower()
                        currency_pattern = "(?:[\£\$\€]{1}[,\d]+.?\d*)"
                        if 'year' in int_costs and '$' in int_costs:
                            int_price_final = ''.join(re.findall(currency_pattern, int_costs)).replace('$', '')
                            int_currency_time = 'Years'
                            course_data['Int_Fees'] = int_price_final
                            course_data['Currency_Time'] = int_currency_time
                            # print('COST PER YEAR: ', int_price_final)
                        elif 'month' in int_costs and '$' in int_costs:
                            int_price_final = ''.join(re.findall(currency_pattern, int_costs)).replace('$', '')
                            int_currency_time = 'Months'
                            course_data['Int_Fees'] = int_price_final
                            course_data['Currency_Time'] = int_currency_time
                            # print('COST PER MONTH: ', int_price_final)
                        elif 'week' in int_costs and '$' in int_costs:
                            int_price_final = ''.join(re.findall(currency_pattern, int_costs)).replace('$', '')
                            int_currency_time = 'Weeks'
                            course_data['Int_Fees'] = int_price_final
                            course_data['Currency_Time'] = int_currency_time
                            # print('COST PER WEEK: ', int_price_final)
                        else:
                            course_data['Int_Fees'] = ''
                            course_data['Currency_Time'] = ''

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
    
    #PREREQUISITE_1
    prerequisite_div = soup.find('div', id='course--requirements--domestic')
    if prerequisite_div:
        prerequisite_list = ['']
        pre_div = prerequisite_div.find('div', class_ = 'col-md-9 course-info__details')
        if pre_div:
            pre_p = pre_div.find_all('p')
            if pre_p:
                for index, p in enumerate(pre_p):
                    if p:
                        prerequi_parag = p.contents.__str__()
                        if prerequi_parag:
                            prerequi_parag = p.get_text().strip()
                            if 'year 12 level' in prerequi_parag:
                                prerequisite_list.append('year 12')
                                # print('yes there is year 12')
                                # print(prerequi_parag)
                prerequisite_list = ''.join(prerequisite_list)
                course_data['Prerequiste_1'] = prerequisite_list.strip()
    

    # removing the columns we don't need
    if 'Available to:' in course_data:
        del course_data['Available to:']
    if 'Location:' in course_data:
        del course_data['Location:']
    if 'CRICOS:' in course_data:
        del course_data['CRICOS:']

    # duplicating entries with multiple cities for each city
    for i in actual_cities:
        course_data['City'] = possible_cities[i.lower()]
        course_data_all.append(copy.deepcopy(course_data))
    del actual_cities


    course_data = {str(key).strip().replace(':', '').replace('\n', ''): str(item).strip().replace('\n', '') for key, item in course_data.items()}
    course_data_all.append(course_data)
    # print(*course_data_all, sep='\n')
# tabulate our data
course_dict_keys = set().union(*(d.keys() for d in course_data_all))

with open(csv_file, 'w', encoding='utf-8', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, course_dict_keys)
    dict_writer.writeheader()
    dict_writer.writerows(course_data_all)

"""Description:

    * author: Awwal Mohammed
    * company: Fresh Futures/Seeka Technologies
    * position: IT Intern
    * date: 13-10-20
    * description: Extracts research links from ACU and write them to file
"""
from pathlib import Path
from selenium import webdriver
import bs4 as bs4
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
exec_path = Path(os.getcwd().replace('\\', '/'))
exec_path = exec_path.parent.parent.__str__() + '/Libraries/Google/v86/chromedriver.exe'
browser = webdriver.Chrome(executable_path=exec_path, chrome_options=option)


# MAIN ROUTINE
course_type_links = []
course_links = []
each_url = 'https://www.acu.edu.au/study-at-acu/find-a-course/course-search-result?CourseType=Research'
browser.get(each_url)
pure_url = each_url.strip()
each_url = browser.page_source

soup = bs4.BeautifulSoup(each_url, 'html.parser')
target_link_tag = soup.find_all('input', class_='hdnUrlValue')
for tag in target_link_tag:
    course_links.append(tag['value'])

course_links_file_path = os.getcwd().replace('\\', '/') + '/acu_research_links_file.txt'
course_links_file = open(course_links_file_path, 'w')
for i in course_links:
    if i is not None and i is not "" and i is not "\n":
        if i == course_links[-1]:
            course_links_file.write(i.strip())
        else:
            course_links_file.write(i.strip()+'\n')

course_links_file.close()
print(*course_links, sep='\n')

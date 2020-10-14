"""Description:

    * author: Awwal Mohammed
    * company: Fresh Futures/Seeka Technologies
    * position: IT Intern
    * date: 09-10-20
    * description:This program extracts the links relating to the types of courses found on the Courses directory of \n
    \t "1Education" RTO (Registered Training Offices) in Brisbane, AU. The links are stored in a file to be used by \n
    \t another program (CourseLinkExtractor.py)
"""
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


# link to 1Education base course page highlighting the types of courses
domain = 'https://www.1education.com.au'
base_url = 'https://www.1education.com.au/courses'
soup = bs4.BeautifulSoup(requests.get(base_url).text, 'html.parser')


# find all the links associated with the COURSE TYPE or COURSE COLLECTION
# these links are contained in an anchor tag with the class "et_pb_button et_pb_promo_button"
course_type_links = []
a_tags = soup.find_all('a', class_='et_pb_button et_pb_promo_button')
for tag in a_tags:
    course_type_links.append(tag['href'])
print(*course_type_links, sep='\n')

# save this in a file
course_type_links_file_path = os.getcwd().replace('\\', '/') + '/course_type_links_file'
course_type_links_file = open(course_type_links_file_path, 'w')
for i in course_type_links:
    if i is not None and i is not "" and i is not "\n":
        if i == course_type_links[-1]:
            course_type_links_file.write(i)
        else:
            course_type_links_file.write(i+'\n')

course_type_links_file.close()

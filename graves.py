'''
Given a grave id number from the findagrave[.]com website and return the following information:
    Birthdate
    Birthplace
    Deathdate
    Deathplace
    Parents
    Spouse
    Siblings
This recursively goes through all the parents returning all parents identified.

Output is to a json file supplied by prompt to the user.
'''
import json
import re
import requests
from bs4 import BeautifulSoup, ResultSet, Tag

URL = 'http://www.findagrave.com/cgi-bin/fg.cgi?page=gr&GRid='


def get_grave_by_id(base_url: str, id_number: int) -> str:
    '''
    Fetches information for a specific grave record using its ID.

    This function retrieves the content of a grave record webpage using the provided
    base URL and ID number. It constructs the full URL by appending the ID to the
    base URL and sends a GET request with a custom User-Agent header to mimic a
    web browser. The function raises an exception if the request fails or the status
    code indicates an error.

    Args:
        base_url (str): The base URL of the grave record webpage (without the ID).
        id_number (int): The unique identifier for the specific grave record.

    Returns:
        str: The text content retrieved from the grave record webpage.

    Raises:
        requests.exceptions.RequestException: If the request fails or the status
        code indicates an error.
    '''
    req_url = base_url + id_number
    ua_string = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    hdrs = {'user-agent': ua_string}
    try:
        req = requests.get(req_url, headers=hdrs, timeout=60)
        req.raise_for_status()
    except requests.exceptions.RequestException as err:
        raise f'Failed to get data from page. Error: {err}'

    return req.text


def parse_page_info(page_info: ResultSet) -> dict[str, dict]:
    '''
    Parses information about family members from a webpage result set.

    This function takes a bs4.BeautifulSoup.ResultSet object containing the parsed
    HTML structure of a webpage. It iterates through the information for each
    family member and extracts details like name, URL of the individual page,
    birth date, and death date. Birth and death dates are assigned a default value
    ("1 Jan 1001") if the corresponding elements are not found.

    The parsed information is organized into a dictionary with relationships as
    keys. Each relationship key holds a nested dictionary containing information
    about family members with that relationship (e.g. 'Spouse', 'Child').

    Args:
        page_info (bs4.BeautifulSoup.ResultSet): The parsed HTML structure of
        the webpage.

    Returns:
        dict[str, dict]: A dictionary where keys are relationships (e.g. 'Spouse',
        'Child') and values are nested dictionaries containing information
        about family members with that relationship (name, URL, birth date, death date).
    '''
    ret_dict = {}
    for _count, records in enumerate(page_info):
        family_recs = records.find_all('div', class_='member-item d-flex mb-2')
        for _counter, info in enumerate(family_recs):
            name = info.find('h3').text.strip()
            url = info['data-href']
            try:
                bday = info.find('span',
                                 {'itemprop': 'birthDate'}).text.strip()
            except AttributeError:
                bday = "1 Jan 1001"
            try:
                dday = info.find('span',
                                 {'itemprop': 'deathDate'}).text.strip()
            except AttributeError:
                dday = "1 Jan 1001"
            tmp_dict = {name: {'url': url, 'bday': bday, 'dday': dday}}
            relationship = records.find('b').text.strip()
            if relationship in ret_dict:
                ret_dict[relationship].update(tmp_dict)
            else:
                ret_dict[relationship] = tmp_dict
    return ret_dict


def get_birth_record(bio: Tag) -> dict:
    '''
    Extracts birth date and birthplace information from a biographical element.

    This function parses a bs4.BeautifulSoup.Tag representing a biographical
    section and attempts to extract the birth date and birthplace information.
    It searches for elements with specific properties (itemprop) to identify
    relevant data. If the elements are not found, the function continues
    processing other records without raising exceptions.

    Args:
    bio (Tag): A bs4.BeautifulSoup.Tag object representing a biographical section.

    Returns:
    dict: A dictionary containing keys 'birthdate' and 'birthplace' with
        extracted information as string values. If the information is not found,
        the corresponding key will have an empty string value.
    '''
    birth_data = {}
    for _count, record in enumerate(bio.find_all('dd')):
        try:
            birth_data['birthdate'] = record.find(
                'time', {'itemprop': 'birthDate'}).text.strip()
            birth_data['birthplace'] = record.find(
                'div', {'itemprop': 'birthPlace'}).text.strip()
        except (KeyError, ValueError, AttributeError):
            pass
    return birth_data


def get_death_record(bio: Tag) -> dict:
    '''
    Extracts death date and deathplace information from a biographical element.

    This function parses a bs4.BeautifulSoup.Tag representing a biographical
    section and attempts to extract the death date and deathplace information.
    It searches for elements with specific properties (itemprop) to identify
    relevant data. If the elements are not found, the function continues
    processing other records without raising exceptions.

    Args:
    bio (Tag): A bs4.BeautifulSoup.Tag object representing a biographical section.

    Returns:
    dict: A dictionary containing keys 'deathdate' and 'deathplace' with
        extracted information as string values. If the information is not found,
        the corresponding key will have an empty string value.
    '''
    death_data = {}
    for _count, record in enumerate(bio.find_all('dd')):
        try:
            death_data['deathdate'] = record.find(
                'span', {'itemprop': 'deathDate'}).text.strip()
            death_data['deathplace'] = record.find(
                'div', {'itemprop': 'deathPlace'}).text.strip()
        except (KeyError, ValueError, AttributeError):
            pass
    return death_data


def get_name(web_data: BeautifulSoup) -> str:
    '''
    Extracts the name from a webpage using a specific HTML structure.

    This function parses a BeautifulSoup object representing the structure of a
    webpage and attempts to extract the name from a specific section. It relies on a
    chain of nested element searches based on class names and IDs. If any element
    in the chain is not found, the function returns an empty string.

    Extra spaces are removed from the name and "VVeteran" is changed "Veteran"

    Args:
    web_data (BeautifulSoup): A BeautifulSoup object representing the parsed
        HTML structure of a webpage.

    Returns:
    str: The extracted name from the webpage, or an empty string if the name
        cannot be found using the assumed HTML structure.

    '''
    name = web_data.find('div', {'class': 'main-wrap'})\
        .find('section', {'id': "content"})\
        .find('div', {'class': 'container-xl section-bio-cover'})\
        .find('div', {'class': 'row flex-print-nowrap'})\
        .find('div', {'class': 'col-12 col-md-7 col-print-auto mt-sm-3'})\
        .find('h1').text
    name = re.sub(' +', ' ', name)
    name = re.sub('VVeteran', 'Veteran', name)
    return name


def get_birth_death_records(web_data: BeautifulSoup) -> Tag:
    '''
    Extracts the  element containing birth and death information.

    This function attempts to extract the HTML element (Tag) containing
    birth and death information from a webpage represented by a BeautifulSoup
    object. It relies on a specific chain of element searches based on class names
    and IDs. If the element chain is not found in the expected structure, the
    function attempts a secondary search with a less specific class name
    ('nonfamous-mem').

    This function assumes the birth and death information is contained within a
    dl element with the class 'mem-events row row-cols-2 gx-2'. If the element
    is not found using the search criteria, the function returns None.

    Args:
    web_data (BeautifulSoup): A BeautifulSoup object representing the parsed
        HTML structure of a webpage.

    Returns:
    Tag: The dl element containing birth and death information (if found),
        or None if the element cannot be located using the assumed structure.
    '''
    try:
        section = web_data.find('div', {'class': 'main-wrap'})\
                          .find('section', {'id': 'content'})\
                          .find('div', {'class': 'nonfamous-mem promod on-photo'})\
                          .find('div', {'class': 'section-first memorial-overview theme-bg'})\
                          .find('div', {'class': 'container-xl section-bio-cover'})\
                          .find('div', {'class': 'row flex-print-nowrap'})\
                          .find('div', {'class': 'col-12 col-md-7 col-print-auto mt-sm-3'})\
                          .find('dl', {'class': 'mem-events row row-cols-2 gx-2'})
    except (KeyError, ValueError, AttributeError):
        section = web_data.find('div', {'class': 'main-wrap'})\
                          .find('section', {'id': 'content'})\
                          .find('div', {'class': 'nonfamous-mem on-photo'})\
                          .find('div', {'class': 'section-first memorial-overview theme-bg'})\
                          .find('div', {'class': 'container-xl section-bio-cover'})\
                          .find('div', {'class': 'row flex-print-nowrap'})\
                          .find('div', {'class': 'col-12 col-md-7 col-print-auto mt-sm-3'})\
                          .find('dl', {'class': 'mem-events row row-cols-2 gx-2'})
    return section


def get_next_parent(person_rec: dict) -> list:
    '''
    Extracts URLs for the next-generation parents from a person's record.

    This function takes a dictionary representing a person's record and a string
    identifying the person within that record (e.g. their name). It assumes the
    record contains a 'Parents' key with nested dictionaries for each parent.
    The function extracts the URLs for these parents from the 'url' key within
    each parent's dictionary.

    Args:
    person_rec (dict): A dictionary representing a person's record, containing
        information about the person and potentially their parents.

    Returns:
    list: A list containing URLs for the next-generation parents found in the
        record, or an empty list if no 'Parents' key is present or the parents don't
        have URLs.
    '''
    parent_lst = []
    if 'Parents' in person_rec:
        for _key, val in person_rec['Parents'].items():
            parent_lst.append(val['url'].split('/', 3)[2])
    return parent_lst


def get_info(rec_num: str, grave_url: str, ret_dict: dict) -> dict:
    '''
    Recursively extracts information for a person from a findagrave.com website.

    This function retrieves and parses information for a person from a findagrave.com
    website. It takes a record number, base URL, and a dictionary to store the
    extracted data.

    1. Fetches Person's Record: It calls get_grave_by_id to fetch the HTML content
        for the person's record using the provided record number and base URL.
    2. Parses Record: It parses the fetched HTML content using BeautifulSoup.
    3. Extracts Basic Information: It calls helper functions to extract the person's
        name (get_name) and birth/death information (get_birth_death_records).
    4. Builds Parent Information Dictionary: It creates a dictionary named
        parents with the person's name as the key and an empty dictionary as the
        value. It then calls get_birth_record and get_death_record to extract birth
        and death details from the birth/death records element.
    5. Extracts Additional Information: It finds all elements with a specific class
        and calls parse_page_info on them to extract additional information about
        family members (e.g. spouse, children). The extracted information is added
        to the parents dictionary under the person's name.
    6. Stores Information: It updates the provided ret_dict with the
        information for the current person stored in parents.
    7. Recursive Calls for Next Generation: It calls get_next_parent to
        retrieve URLs for the next-generation parents (e.g. children) from the
        current person's information. If URLs are found, it recursively calls
        get_info for each parent URL to extract their information as well.

    Args:
    rec_num (str): The record number of the person to retrieve information for.
    grave_url (str): The base URL of the graveyard website.
    ret_dict (dict): A dictionary to store the extracted information for all
        people. The function updates this dictionary with the information for the
        current person.

    Returns:
    dict: The same ret_dict passed as an argument, now updated with the
        information for the current person and potentially their next generation
        (if found).
    '''
    person_info = get_grave_by_id(grave_url, rec_num)  # 120297053
    soup = BeautifulSoup(person_info, "lxml")

    name = get_name(soup)
    b_d_records = get_birth_death_records(soup)

    parents = {name: {}}
    parents[name]['Birth_Info'] = get_birth_record(b_d_records)
    parents[name]['Death_Info'] = get_death_record(b_d_records)

    content = soup.find_all('div', class_='col-12 col-sm-6 col-print-auto')

    parents[name].update(parse_page_info(content))
    ret_dict.update(parents)
    next_gen = get_next_parent(parents[name])
    if len(next_gen) != 0:
        for record in next_gen:
            print(f'Looking up {record}')
            get_info(record, grave_url, ret_dict)
    return ret_dict


def get_user_data() -> tuple[str, str]:
    '''
    Prompts the user for initial grave ID and filename for output storage.

    This function interacts with the user to gather input required for further
    processing. It prompts the user to enter two pieces of information:

    * Initial Grave ID: A string representing the starting ID for processing
        grave records.
    * Filename: A string representing the desired filename where the data
        will be stored in the working directory

    The function validates neither of the inputs. It simply collects the user's
    response and returns a tuple containing both the ID and filename.

    Args:
    None

    Returns:
    tuple[str, str]: A tuple containing the entered grave ID (string) and
        filename (string).
    '''
    person_id = input('Please enter the initial grave id: ')
    fname = input('Please enter the filename to write data: ')
    return (person_id, fname)


(initial_person, filename) = get_user_data()
grave_info = {}
grave_info = get_info(initial_person, URL, grave_info)

print(f'{len(grave_info)} records found!')
with open(filename, 'w', encoding='utf-8') as output:
    array = [{i: grave_info[i]} for i in grave_info]
    output.write(json.dumps(array))

print('Exiting normally')

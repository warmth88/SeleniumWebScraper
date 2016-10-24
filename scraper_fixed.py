#!/usr/bin/env python
import csv
from selenium import webdriver
import time
import random
import sys

#browser = webdriver.Chrome(executable_path='/Users/anthonydefusco/Dropbox/research/foreclosure_delay/data/processed/lexis_foreclosures/script/chromedriver')
browser = webdriver.Firefox(executable_path='/Users/huanxin/bin/wires')
browser.implicitly_wait(2)

# login and get to the search page
url = 'https://www.nexis.com/'
browser.get(url)
browser.find_element_by_name('webId').clear()
browser.find_element_by_name('webId').send_keys('haunxinwu')
browser.find_element_by_name('password').clear()
browser.find_element_by_name('password').send_keys('raaccount1')
browser.find_element_by_xpath(
    '//*[@id="signIn"]/div[2]/input[3]').click()
browser.find_element_by_xpath('//*[@id="secondarytabs"]/ul/li[3]/a').click()


# submit address and first name information
def submit(loc, name, zipcode):
    # if new:
    #     browser.switch_to_frame('fr_feature')
    try:
        browser.switch_to_frame('fr_feature')
    except:
        pass
    browser.find_element_by_id('MainContent_Address1').clear()
    browser.find_element_by_id('MainContent_Address1').send_keys(loc)
    browser.find_element_by_id('MainContent_FirstName').send_keys(name[0])
    browser.find_element_by_id('MainContent_LastName').send_keys(name[1])
    browser.find_element_by_id('MainContent_City').clear()
    browser.find_element_by_id('MainContent_City').send_keys('Cleveland')
    browser.find_element_by_id('MainContent_Zip5').clear()
    browser.find_element_by_id('MainContent_Zip5').send_keys(zipcode)
    browser.find_element_by_xpath('//*[@id="MainContent_State_stateList"]/\
                                  option[contains(text(), "Ohio")]').click()
    browser.find_element_by_xpath(
        '//*[@id="MainContent_formSubmit_searchButton"]').click()


def ssn_sort(info, parcel):
    # only for cases with multiple SSNs
    unique = []
    note = []
    parcel_match = []
    for i in range(len(info)):
        if info[i] != '':
            # go into the page
            browser.find_element_by_xpath(
                '//*[@id="spanNames%s_0"]/a' %
                str(i+1)).click()
            try:
                browser.switch_to_frame('fr_feature')
            except:
                pass
            tmp_ssn = browser.find_element_by_xpath(
                '//*[@id="resultTableDiv"]/div[2]/div[2]/table[2]/\
                tbody/tr[3]/td[1]').text
            if tmp_ssn == '':
                print 'ERROR: SSN only found on main page'
            if ('multiple' not in tmp_ssn) and ('Deceased' not in tmp_ssn):
                unique.append(info[i])
            else:
                note.append(info[i])
            for j in browser.find_elements_by_xpath(
                    "//*[contains(text(), 'Parcel')]/following-sibling::*"):
                if j.text == parcel:
                    parcel_match.append(info[i])
            browser.back()
            try:
                browser.switch_to_frame('fr_feature')
            except:
                pass
    parcel_match = sorted(set(parcel_match), key=parcel_match.index)
    unique = sorted(set(unique), key=unique.index)
    note = sorted(set(note), key=note.index)
    print 'unique', unique
    print 'note', note
    print 'parcel', parcel_match
    if len(parcel_match) >= 1:
        return list(parcel_match)[0], 'Multi SSN, Use Parcel',\
            len(parcel_match)
    else:
        if len(unique) >= 1:
            return list(unique)[0], 'Multi SSN, Use NoNote', len(unique)
        else:
            if len(note) >= 1:
                return list(note)[0], 'Multi SSNs, Use Note', len(note)
            else:
                print 'ERROR: No Multi SSNs found'


# locate the person that matches the requested name
def locate(name_want, parcel):
    SSN = ''
    try:
        cnt = int(browser.find_element_by_xpath(
            '//*[@id="MainContent_toolbar_totalRecords"]').text)
    except:
        print 'ERROR: No Result'
        return '', 'No Match', 0, 0, 0

    # get all SSNs
    info = ['']*cnt
    for i in browser.find_elements_by_xpath("//*[contains(@id, 'spanSSN')]"):
        tmp = i.get_attribute('id')
        info[int(tmp[7:tmp.find('_')])-1] = i.text

    # count number of matched SSNs
    multi = []
    options = 0
    indicator = 0
    for i in info:
        if i != '':
            multi.append(i)
    if len(set(multi)) == 0:
        status = 'Match, No SSN'
    else:
        if len(set(multi)) == 1:
            SSN = multi[0]
            tmp_SSN, tmp_status, tmp_options = ssn_sort(info, parcel)
            if tmp_status == 'Multi SSN, Use Parcel':
                indicator = 1
            status = 'Match, Unique SSN'
        else:
            SSN, status, options = ssn_sort(info, parcel)
    return SSN, status, len(set(multi)), options, indicator

f_in = csv.reader(open(sys.argv[1], 'r'),
                  delimiter=',')
f_in.next()
row_count = sum(1 for row in f_in)
f_in = csv.reader(open(sys.argv[1], 'r'),
                  delimiter=',')
f_in.next()
f_out = csv.writer(open(sys.argv[2], 'w'), delimiter=',',
                   dialect='excel')
new = True
cnt = 0
for i in f_in:
    cnt += 1
    print "Processing %d/%d" % (cnt, row_count)
    name = [i[6], i[7], i[8]]
    address = i[-2]
    parcel = i[1]
    zipcode = i[-1]
    SSN = ''
    print 'serach: ', name, address
    submit(address, name, zipcode)
    SSN, status, multi, options, indicator = locate(name, parcel)
    print SSN, status, multi, options, indicator
    try:
        try:
            browser.switch_to_frame('fr_feature')
        except:
            pass
        browser.find_element_by_xpath(
            '//*[@id="MainContent_detailsHeader_newSearchButton"]').\
            click()
    except:
        try:
            browser.find_element_by_xpath(
                '//*[@id="MainContent_newSearch"]').click()
        except:
            print 'CANNOT START NEW SEARCH'
    new = False
    f_out.writerow(i+[SSN, status, str(multi), str(options), str(indicator)])
    time.sleep(2 + random.randint(-2, 2))

print 'FINISHED PROCESSING ' + sys.argv[1]
browser.quit()

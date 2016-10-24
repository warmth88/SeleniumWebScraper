def clean_name(tmp):
    first = []
    last = []
    for i in tmp.splitlines():
        pair = i.split(',')
        if i[0] != '(' and len(pair) > 1:
            if pair[1][0] != ' ':
                first.append(i.split(',')[1])
            else:
                first.append(i.split(',')[1][1:])
            last.append(i.split(',')[0])
    return [first, last]


def verify_name(name, name_want):
    first = 0.0
    last = 0.0
    for i in name[0]:
        if i in name_want:
            first = 0.5
    for i in name[1]:
        if i in name_want:
            last = 0.5
    return first+last

cnt = int(browser.find_element_by_xpath('//*[@id="MainContent_toolbar_totalRecords"]').text)
max_id = []
max_rating = 0.0
for i in range(cnt):
    tmp = browser.find_element_by_xpath('//*[@id="resultscontent"]/tbody/tr[%s]/td[2]' % str(i+2)).text
    tmp = clean_name(tmp)
    name_want = 'LAKISHA M TUGGLE ET AL'
    rating = verify_name(tmp, name_want)
    if rating > max_rating:
        max_rating = rating
        max_id = [i+2]
    elif rating == max_rating:
        max_id.append(i+2)

if max_id:
    for i in max_id:
        print browser.find_element_by_xpath('//*[@id="resultscontent"]/tbody/tr[%s]/td[2]' % str(i)).text
else:
    print 'not found'

if len(max_id) == 1:
    # browser.get(browser.find_element_by_xpath('//*[@id="resultscontent"]/tbody/tr[%s]/td[2]/span[1]/a' % str(max_id[0])).get_attr    ibute('href'))
    browser.find_element_by_xpath('//*[@id="resultscontent"]/tbody/tr[%s]/td[2]/span[1]/a' % str(max_id[0])).click()
    # print browser.find_element_by_xpath('//*[@id="resultscontent"]/tbody/tr[%s]/td[2]/span[1]' % str(max_id[0])).text
    # print i+1, browser.find_element_by_xpath('//*[@id="resultscontent"]/tbody/tr[%s]/td[4]/span[1]' % str(i+1)).text
# browser.find_element_by_xpath('//*[@id="spanSSN4_261"]/a

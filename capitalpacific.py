import pymongo
from selenium import webdriver
import smtplib
import sys
import json

from pymongo import MongoClient
client = MongoClient('localhost', 27017)

db = client.properties
collection = db['capitalpacific']

#hold old properties imported from DB
oldProperties = []
#holds new properties gathered from page
newProperties = []

driver = webdriver.Firefox()
driver.get("http://cp.capitalpacific.com/Properties")

for property in driver.find_elements_by_css_selector('table.property div.property'):
    title = property.find_element_by_css_selector('div.title h2')
    location = property.find_element_by_css_selector('div.title h4')
    marketing_package = property.find_element_by_partial_link_text('Marketing Package')
    contact_email = property.find_element_by_partial_link_text('.com')


    newProperties.append({
        'title': title.text,
        'location': location.text,
        'marketing_package_url': marketing_package.get_attribute("href"),
        'contact': contact_email.get_attribute("href")
    })

driver.close()

'''if database not empty, add the old properties,
then compare against the newly fetched and remove repeats'''

if collection.count() != 0:
    for post in collection.find():
        oldProperties.append(post)

    for a in oldProperties:
        for b in newProperties:
            if a['marketing_package_url'] == b['marketing_package_url']:
                newProperties.remove(b)

'''if no new listings, exit the program.  Otherwise, email all new 
listings and then insert them into the DB'''

if len(newProperties) == 0:
    sys.exit()
else:
    fromaddr = 'ottoliarobert@gmail.com'
    toaddrs = ['ottoliar@onid.oregonstate.edu']
    username = 'ottoliarobert@gmail.com'
    password = 'xxxxxxxxx'

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)

    for item in newProperties:
        fullMessage = "New Listing @ Capital Pacific: " + "\n"
        fullMessage += "Title: " + str(item['title']) + "\n"
        fullMessage += "Location: " + str(item['location']) + "\n"
        fullMessage += "Contact Email: " + str(item['contact']) + "\n"
        server.sendmail(fromaddr, toaddrs, fullMessage)
        collection.insert(item)

    server.quit()



from selenium import webdriver
from email.mime.text import MIMEText
import pymongo
import smtplib
import sys

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

    for oldListing in oldProperties:
        for newListing in newProperties:
            if oldListing['marketing_package_url'] == newListing['marketing_package_url']:
                newProperties.remove(newListing)

'''if no new listings, exit the program.  Otherwise, email all new 
listings and then insert them into the database'''

if len(newProperties) == 0:
    sys.exit()
else:
    with open('passwords.txt') as inFile:
        password = inFile.read()
    fromaddr = 'ottoliarobert@gmail.com'
    toaddrs = ['andy.ottolia@gmail.com']
    username = 'ottoliarobert@gmail.com'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username, password)
    subject = "New Listing @ Capital Pacific"
    
    for item in newProperties:
        body = "Title: " + str(item['title']) + "\n"
        body += "Location: " + str(item['location']) + "\n"
        body += "URL: " + str(item['marketing_package_url']) + "\n"
        body += "Contact Email: " + str(item['contact']) + "\n"
        msg = """\From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (fromaddr, ", ".join(toaddrs), subject, body)
        server.sendmail(fromaddr, toaddrs, msg)
        collection.insert(item)

    server.close()


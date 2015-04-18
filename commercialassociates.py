from selenium import webdriver
import pymongo
import smtplib
import sys

from pymongo import MongoClient
client = MongoClient('localhost', 27017)

db = client.properties
collection = db['commercialassociates']

#hold old properties imported from DB 
oldProperties = []
#hold new properties from page
newProperties = []

driver = webdriver.Firefox()

driver.get("http://commercialassociates.org")

for property in driver.find_elements_by_class_name("latest_listings"):
	location = property.find_element_by_class_name("listing-meta-top")
	title = property.find_element_by_class_name("metalistingtitle")
	URL = property.find_element_by_partial_link_text("Click here")

	newProperties.append({
		'title': title.text,
		'location': location.text,
		'URL': URL.get_attribute("href")
		})

driver.close()

'''if database not empty, add the old properties,
then compare against the newly fetched and remove repeats'''

if collection.count() != 0:
	for post in collection.find():
		oldProperties.append(post)

	for oldListing in oldProperties:
		for newListing in newProperties:
			if oldListing['URL'] == newListing['URL']:
				newProperties.remove(newListing)

'''if no new listings, exit the program.  Otherwise, email all new 
listings and then insert them into the database'''

if len(newProperties) == 0:
    sys.exit()
else:
    with open('passwords.txt') as inFile:
        password = inFile.read()
    fromaddr = 'commercialinvestorsofus@gmail.com'
    toaddrs = ['andy.ottolia@gmail.com']
    username = 'commercialinvestorsofus@gmail.com'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username, password)
    subject = "New Listing @ Commercial Associates"
    
    for item in newProperties:
        body = "Title: " + str(item['title']) + "\n"
        body += "Location: " + str(item['location']) + "\n"
        body += "URL: " + str(item['URL']) + "\n"
        msg = """\From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (fromaddr, ", ".join(toaddrs), subject, body)
        server.sendmail(fromaddr, toaddrs, msg)
        collection.insert(item)

    server.close()





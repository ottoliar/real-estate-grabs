from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
import sys
import smtplib
import pymongo

from pymongo import MongoClient
client = MongoClient('localhost', 27017)

db = client.properties
collection = db['sperryVanNess']

#holds properties already in DB
oldProperties = []
#holds new properties gathered from page
newProperties = []

driver = webdriver.Firefox()
#go to the website
driver.get('http://www.svnbluestone.com/search-properties/')

# wait for frame to load
frame = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#buildout iframe")))
driver.switch_to.frame(frame)

for property in driver.find_elements_by_class_name('propertyListItem'):
	generalInfo = property.find_element_by_class_name('addressInfo')
	title = generalInfo.find_element_by_tag_name('a')
	location = generalInfo.find_element_by_class_name('propertiesListCityStateZip')
	email = property.find_element_by_partial_link_text('Email')
	link = property.find_element_by_partial_link_text(title.text)
	contact = email.get_attribute('href')
	url = link.get_attribute('href')

	newProperties.append({
		'title': title.text,
		'location': location.text,
		'URL': url,
		'contact': contact
		})

driver.close()

'''if database not empty, add the old properties,
then compare against the newly fetched and remove repeats'''

if collection.count != 0:
	for post in collection.find():
		oldProperties.append(post)

	for oldListing in oldProperties:
		for newListing in newProperties:
			if oldListing['URL'] == newListing['URL']:
				newProperties.remove(newListing)

'''if no new listings, exit the program.  Otherwise, email all new 
listings and then insert them into the DB'''

if len(newProperties) == 0:
	sys.exit()
else:
	with open('passwords.txt') as inFile:
		password = inFile.read()
	fromaddr = 'commercialinvestorsofus@gmail.com'
	toaddrs = ['andy.ottolia@svn.com']
	username = 'commercialinvestorsofus@gmail.com'
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()
	server.login(username, password)
	subject = "New Listing @ Sperry Van Ness BlueStone"

	for item in newProperties:
		body = "Title: " + str(item['title']) + "\n"
		body += "Location: " + str(item['location']) + "\n"
		body += "URL: " + str(item['URL']) + "\n"
		body += "Contact Email: " + str(item['contact']) + "\n"
		msg = """\From: %s\nTo: %s\nSubject: %s\n\n%s
		""" % (fromaddr, ", ".join(toaddrs), subject, body)
		server.sendmail(fromaddr, toaddrs, msg)
		collection.insert(item)

	server.close()
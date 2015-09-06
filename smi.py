from selenium import webdriver
import pymongo
import sys
import smtplib

from pymongo import MongoClient
client = MongoClient('localhost', 27017)

db = client.properties
collection = db['smi']

oldProperties = []
newProperties = []

driver = webdriver.Firefox()

driver.get("http://smicre.com/category/current-properties/properties-for-sale/")

for property in driver.find_elements_by_class_name('search-content-image'):
	URL = property.get_attribute('href')

	newProperties.append({
		'URL': URL
		})

driver.close()

if collection.count != 0:
	for post in collection.find():
		oldProperties.append(post)

	for oldListing in oldProperties:
		for newListing in newProperties:
			if oldListing['URL'] == newListing['URL']:
				newProperties.remove(newListing)

if len(newProperties) == 0:
	sys.exit()
else:
	with open('passwords.txt') as inFile:
		password = inFile.read()
	fromaddr = 'commercialinvestorsofus@gmail.com'
	toaddrs = ['andy.ottolia@svn.com']
	username = fromaddr
	subject = "New Listing @ SMI Commercial Real Estate"
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.set_debuglevel(1)
	server.ehlo()
	server.starttls()
	server.login(username, password)

	for item in newProperties:
		msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" 
			% (fromaddr, ", ".join(toaddrs), subject) )
		msg += "\nURL: " + str(item['URL'])
		server.sendmail(fromaddr, toaddrs, msg)
		collection.insert(item)

server.quit()
	

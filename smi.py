from selenium import webdriver
import pymongo
import sys
import smtplib

from pymongo import MongoClient
with open('uri.txt') as URI_file:
    uri = URI_file.read()
client = MongoClient(uri)

db = client.properties
collection = db['smi']

newProperties = []

driver = webdriver.Firefox()

driver.get("http://smicre.com/category/current-properties/properties-for-sale/")

for property in driver.find_elements_by_class_name('search-content-image'):
	URL = property.get_attribute('href')
	title = property.get_attribute('title')

	newProperties.append({
		'URL': URL,
		'title': title
		})

driver.close()

newProperties = [newListing for newListing in newProperties if collection.find({ 'URL': newListing['URL'] }).count > 0]

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
	server.ehlo()
	server.starttls()
	server.login(username, password)

	for item in newProperties:
		msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" 
			% (fromaddr, ", ".join(toaddrs), subject) )
		msg += item['title'] + "\n"
		msg += item['URL']
		server.sendmail(fromaddr, toaddrs, msg.encode('utf-8'))
		collection.insert(item)

server.quit()
	

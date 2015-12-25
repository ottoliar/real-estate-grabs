from selenium import webdriver
import pymongo
import sys
import smtplib

from pymongo import MongoClient
with open('uri.txt') as URI_file:
    uri = URI_file.read()
client = MongoClient(uri)

db = client.properties
collection = db['hfo']

newProperties = []

driver = webdriver.Firefox()

driver.get("http://hfore.com/transactions.aspx?show=listings")

for property in driver.find_elements_by_class_name('propertyItem'):
	info = property.find_element_by_tag_name('h3')
	links = property.find_element_by_tag_name('a')
	URL = links.get_attribute('href')
	title = info.text
	
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
	subject = "New Listing @ HFO Real Estate"
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
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import pymongo
import sys
import smtplib
import re

from pymongo import MongoClient
with open('uri.txt') as URI_file:
    uri = URI_file.read()
client = MongoClient(uri)

db = client.properties
collection = db['gallre']

newProperties = []

driver = webdriver.Firefox()
delay = 5
driver.get("http://willamettevalleyidx.com/agent_specific_search_results.php?sid=131184&site_id=540&agsp=1&class_id=4")
WebDriverWait(driver, delay)
for property in driver.find_elements_by_class_name("featured-results-listing"):
	URL = property.get_attribute('onclick')
	info = property.find_elements_by_tag_name('li')
	price = None
	city = None
	for data in info:
		if "Price" in data.text:
			price = data.text
		elif "City" in data.text:
			city = data.text
		else:
			continue
	stringSplit = re.findall(r"\'(.*?)\'", URL)
	URL_complete = "willamettevalleyidx.com/" + stringSplit[0]
	newProperties.append({
		'URL': URL_complete,
		'Price': price,
		'City': city
		})

driver.close()

for newListing in newProperties:
    if collection.find({'URL':newListing['URL']}).count > 0:
        newProperties.remove(newListing)

if len(newProperties) == 0:
	sys.exit()
else:
	with open('passwords.txt') as inFile:
		password = inFile.read()
	fromaddr = 'commercialinvestorsofus@gmail.com'
	toaddrs = ['andy.ottolia@svn.com']
	username = fromaddr
	subject = "New Listing @ Gall Real Estate"
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.ehlo()
	server.starttls()
	server.login(username, password)

	for item in newProperties:
		msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" 
			% (fromaddr, ", ".join(toaddrs), subject) )
		msg += item['City'] + "\n"
		msg += item['Price'] + "\n"
		msg += item['URL'] 
		server.sendmail(fromaddr, toaddrs, msg)
		collection.insert(item)

server.quit()
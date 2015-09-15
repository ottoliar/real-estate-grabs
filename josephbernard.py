from selenium import webdriver
import pymongo
import sys
import smtplib

from pymongo import MongoClient
client = MongoClient('localhost', 27017)

db = client.properties
collection = db['josephbernard']

oldProperties = []
newProperties = []

driver = webdriver.Firefox()

driver.get("http://josephbernard.net/properties.php?state=oregon")

listings = driver.find_elements_by_css_selector("table[style='border-bottom:#ccc 1px solid;']")
for post in listings:
	links = post.find_elements_by_tag_name("a")
	if len(links) > 1:
		url = links[1].get_attribute('href')
		info = links[1].text

		newProperties.append({
			'URL': url,
			'Info': info
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
	subject = "New Listing @ Joseph Bernard Real Estate"
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.ehlo()
	server.starttls()
	server.login(username, password)

	for item in newProperties:
		msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" 
			% (fromaddr, ", ".join(toaddrs), subject) )
		msg += item['URL'] + "\n"
		msg += item['Info']
		server.sendmail(fromaddr, toaddrs, msg.encode('utf-8'))
		collection.insert(item)

server.quit()
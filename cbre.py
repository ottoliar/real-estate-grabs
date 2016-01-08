from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
import pymongo
import sys
import smtplib

def extractData(webElement, propertyList):
	linkInfo = webElement.find_element_by_tag_name("a")
	URL = linkInfo.get_attribute('data-url')
	title = webElement.find_element_by_tag_name("h4")
	location = webElement.find_element_by_tag_name("h5")

	propertyList.append({
		'Title': title.text,
		'URL': URL,
		'Location': location.text
		})
	return

from pymongo import MongoClient
with open('uri.txt') as URI_file:
	uri = URI_file.read()
client = MongoClient(uri)

db = client.properties
collection = db['cbre']

newProperties = []

driver = webdriver.Firefox()

driver.get("http://www.cbre.us/PropertyListings/Pages/Properties-for-Sale.aspx")
driver.switch_to.frame("ctl00_PlaceHolderMain_IFrameContent_IFrameContent")
#Searching for multifamily residences
selectPropertyType = Select(driver.find_element_by_id("ForSalePropertyType"))
selectPropertyType.select_by_value("70")

#In the state of Oregon
selectState = Select(driver.find_element_by_id("ForSaleState_ListBox1"))
selectState.select_by_value("OR")

#Submit form
submitBtn = driver.find_element_by_id("ForSaleLooplinkSubmit")
submitBtn.click()

#Wait for results to load
WebDriverWait(driver, 5)

#Get relevant data and place listings into newProperties
for listing in driver.find_elements_by_css_selector("tr[class='llRD-record llRD-alt']"):
	extractData(listing, newProperties)

for listing in driver.find_elements_by_css_selector("tr[class='llRD-record']"):
	extractData(listing, newProperties)

driver.close()

# Send newly found properties before inserting into the Database
newProperties = [newListing for newListing in newProperties if collection.find({ 'URL': newListing['URL'] }).count > 0]

if len(newProperties) == 0:
	sys.exit()
else:
	with open('passwords.txt') as inFile:
		password = inFile.read()
	fromaddr = 'commercialinvestorsofus@gmail.com'
	toaddrs = ['andy.ottolia@svn.com']
	username = fromaddr
	subject = "New Listing @ CBRE Real Estate (Multifamily -- Oregon)"
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.ehlo()
	server.starttls()
	server.login(username, password)

	for item in newProperties:
		msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" 
			% (fromaddr, ", ".join(toaddrs), subject) )
		msg += item['Title'] + "\n"
		msg += item['Location'] + "\n"
		msg += "http://www.cbre.us/PropertyListings/Pages/Properties-for-Sale.aspx"
		server.sendmail(fromaddr, toaddrs, msg.encode('utf-8'))
		collection.insert(item)

server.quit()
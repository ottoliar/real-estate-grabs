from selenium import webdriver
import smtplib
import sys
import re
import json

#holds known URL's
oldProperties = []

#all listing on current page get put into this dict
newProperties = []

driver = webdriver.Firefox()

#Capital Pacific Website
#Commerical Real Estate

#open text file containing property titles we already know about
p = re.compile(r'https?:\/\/[^"]+', re.IGNORECASE | re.MULTILINE)
with(open("properties.txt", "rU")) as f:
	for line in f:
		q = re.findall(p, line)
		oldProperties.extend(q)

#search for new listings
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

#find the properties that we already have by cross referencing the
#marketing URLS
for x in oldProperties:
	for item in newProperties:
		if (item['marketing_package_url'] == x):
			newProperties.remove(item)
	

#properties now has only the new properties
#add them to the file
with open('properties.txt', 'w') as outfile:
	for item in newProperties:
		json.dump(item, outfile)


#if no new properties found, terminate script
#else, email properties
#if no new properties found, terminate script
#else, email properties
if len(newProperties) == 0:
    sys.exit()
else: 
    fromaddr = 'ottoliarobert@gmail.com'
    toaddrs = ['Andrew.Ottolia@marcusmillichap.com']
    username = 'ottoliarobert@gmail.com'
    password = '08Acuratl'

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)

    for item in newProperties:
        fullMessage = "New Listing @ Capital Pacific: " + "\n"
        fullMessage += "Title: " + str(item['title']) + "\n"
        fullMessage += "Location: " + str(item['location']) + "\n"
        fullMessage += "Contact Email: " + str(item['contact']) + "\n"
        server.sendmail(fromaddr, toaddrs, fullMessage)

    server.quit()


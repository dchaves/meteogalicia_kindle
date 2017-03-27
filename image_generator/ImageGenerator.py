#!/usr/bin/python3
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from dateutil.parser import parse as dateparse
import json
import locale
import codecs

def generate_svg(battery='N/A'):
	locale.setlocale(locale.LC_TIME, "es_ES")
	COD_TUI = 36055
	URL = "http://servizos.meteogalicia.gal/rss/predicion/rssLocalidades.action?idZona={0}&dia=-1&request_locale=gl".format(COD_TUI)
	respxml = urlopen(URL).read()
	root = ET.fromstring(respxml)
	information = []
	for channel in root:
		for item in channel.findall('item'):
			#date = dateparse(item.find('{Concellos}dataCreacion').text)
			#print(date)
			preddate = dateparse(item.find('{Concellos}dataPredicion').text)

			tmax = item.find('{Concellos}tMax').text
			tmin = item.find('{Concellos}tMin').text

			ceom = item.find('{Concellos}ceoM').text
			ceot = item.find('{Concellos}ceoT').text
			ceon = item.find('{Concellos}ceoN').text

			ventom = item.find('{Concellos}ventoM').text
			ventot = item.find('{Concellos}ventoT').text
			venton = item.find('{Concellos}ventoN').text

			vmin = min([int(ventom),int(ventot),int(venton)])
			vmax = max([int(ventom),int(ventot),int(venton)])

			if vmin <= 300:
				vsmin = 0
			elif vmin <= 308:
				vsmin = 5
			elif vmin <= 316:
				vsmin = 20
			elif vmin <= 324:
				vsmin = 40
			else:
				vsmin = 70

			if vmax <= 300:
				vsmax = 5
			elif vmax <= 308:
				vsmax = 20
			elif vmax <= 316:
				vsmax = 40
			elif vmax <= 324:
				vsmax = 70
			else:
				vsmax = 120

			choivam = item.find('{Concellos}pChoivaM').text
			choivat = item.find('{Concellos}pChoivaT').text
			choivan = item.find('{Concellos}pChoivaN').text

			day = {
				'date': preddate.strftime('%a, %d %b. %Y'),
				'temp': [tmin, tmax],
				'sky': [ceom, ceot, ceon],
				'wind': [str(vsmin), str(vsmax)],
				'rain': [choivam, choivat, choivan]
				}
			information.append(day)
	#print(json.dumps(information, indent=4, sort_keys=True))
	### Modify image to be shown
	output = codecs.open('template.svg','r',encoding='utf-8').read()

	### Set battery level
	output = output.replace('$battery', battery)
	### Set weather values
	for i in range(0,3):
		output = output.replace('$date{0}'.format(i), information[i]['date'])
		output = output.replace('$tempmin{0}'.format(i), information[i]['temp'][0])
		output = output.replace('$tempmax{0}'.format(i), information[i]['temp'][1])
		output = output.replace('$windmin{0}'.format(i), information[i]['wind'][0])
		output = output.replace('$windmax{0}'.format(i), information[i]['wind'][1])
		output = output.replace('$rain{0}0'.format(i), information[i]['rain'][0])
		output = output.replace('$rain{0}1'.format(i), information[i]['rain'][1])
		output = output.replace('$rain{0}2'.format(i), information[i]['rain'][2])
	### Set weather icons
		#svgtemplateroot = ET.fromstring(output)
		for j in range (0,3):
			imagepath = 'meteo_icons/{0}.svg'.format(information[i]['sky'][j])
			image = codecs.open(imagepath,'r',encoding='utf-8').read()
			svgroot = ET.fromstring(image)
			path = svgroot.find('{http://www.w3.org/2000/svg}path')
			icon = path.attrib['d']
			#print('.//{{http://www.w3.org/2000/svg}}path[@id="icon{0}{1}"]'.format(i,j))
			#iconplace = svgtemplateroot.find('.//{{http://www.w3.org/2000/svg}}path[@id="icon{0}{1}"]'.format(i,j))
			#print(iconplace.tag)
			output = output.replace('$icon{0}{1}'.format(i,j), icon)

	### Write output
	codecs.open('result.svg','w',encoding='utf-8').write(output)

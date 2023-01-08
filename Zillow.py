import requests
import re
import json
import pandas as pd
import warnings
import urllib.parse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib import cm
warnings.filterwarnings('ignore')

img = mpimg.imread('Houston.jpg')
imgplot = plt.imshow(img)

# Map conversion
P1_img = np.array([ 372 , 2449 ])
P1_latlong = np.array([ 29.785469440407883 , -95.66588641683309 ])
P2_img = np.array([ 3483 , 3368 ])
P2_latlong = np.array([ 29.71332485 , -95.39158460609637 ])
intp = []
intp.append( np.polyfit( [ P1_latlong[0] , P2_latlong[0] ] , [ P1_img[1] , P2_img[1] ] , 1 ) )
intp.append( np.polyfit( [ P1_latlong[1] , P2_latlong[1] ] , [ P1_img[0] , P2_img[0] ] , 1 ) )

def Conversion( latlong ):
	return [ np.polyval( intp[1] , float(latlong[1]) ) , np.polyval( intp[0] , float(latlong[0]) ) ]

def Address2Coord( address ):
	url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'
	response = requests.get(url).json()
	return [ response[0]["lat"] , response[0]["lon"] ]

def make_frame(frame):
	for i in data_list:
		for item in i['cat1']['searchResults']['listResults']:
			frame = frame.append(item, ignore_index=True)
	return frame

# pt = Conversion( [ response[0]["lat"] , response[0]["lon"] ] )
# plt.plot( pt[0] , pt[1] , 'rp' )
# plt.show()
# address = '6405 Cavalcade St, Houston, TX 77026'
# exit()

#############################################################################################
city = 'houston/' #*****change this city to what you want!!!!*****
N_pages = 20
Max_price = 300000.
Min_price = 0.
#############################################################################################


#add headers in case you use chromedriver (captchas are no fun); namely used for chromedriver
req_headers = {
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'accept-encoding': 'gzip, deflate, br',
	'accept-language': 'en-US,en;q=0.8',
	'upgrade-insecure-requests': '1',
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

urls = []
for i in range(N_pages):
	base = 'https://www.zillow.com/homes/for_sale/' + city
	if i > 0:
		base += '/' + str(i+2) + '_p/'
	urls.append( base )

data_list = []
with requests.Session() as s:
	for url in urls:
		curr_r = s.get(url, headers=req_headers)
		data_list.append( json.loads(re.search(r'!--(\{"queryState".*?)-->', curr_r.text).group(1)) )


df = pd.DataFrame()
df = make_frame(df)
	
# Drop cols
df = df.drop('hdpData', 1) #remove this line to see a whole bunch of other random cols, in dict format
df = df.drop_duplicates(subset='zpid', keep="last")

# Filters
df['zestimate'] = df['zestimate'].fillna(0)
# Price
f = ( df['unformattedPrice'] >= Min_price ) * ( df['unformattedPrice'] <= Max_price )
df = df[f]



address = df['address']
failed = 0
x , y , c = [] , [] , []
for a , ppp in zip( address , df['unformattedPrice'] ):
	for check in [ '#' , 'APT' , 'UNIT' ]:
		if check in a:
			tmp = a.split(check)
			for i in range(len(tmp[-1])):
				if tmp[-1][i] == ',':
					break
			a = tmp[0] + tmp[-1][i:]
	try:
		latlon = Address2Coord( a )
		pt = Conversion( latlon )
		# plt.plot( pt[0] , pt[1] , 'rp' )
		x.append( pt[0] )
		y.append( pt[1] )
		c.append( ppp )

	except:
		# print( a )
		failed += 1
print( failed , df.shape[0] )

plt.scatter( x , y , s=30 , c=c , cmap = cm.jet )
m = cm.ScalarMappable(cmap=cm.jet)
m.set_array(c)
plt.colorbar(m)

plt.show()
exit()

# df['best_deal'] = df['unformattedPrice'] - df['zestimate']
# df = df.sort_values(by='best_deal',ascending=True)

print('shape:', df.shape)
# display(df[['id','address','beds','baths','area','price','zestimate','best_deal']].head(20))
# print(df[['address','price']])
print( df['unformattedPrice'] )
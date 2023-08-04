from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="weatherapp.log" , level=logging.INFO)
import os
import json
import base64
from datetime import datetime

app = Flask(__name__)
@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            # query to search for images
            citynm = request.form['content'].replace(" ","")
            API_KEY = "36afc31263aaeac1d251fad0fd361fd8"
            # directory to store downloaded images
            save_directory = "images/"
                # create the directory if it doesn't exist
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            # fake user agent to avoid getting blocked by Google
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
                
            # fetch the search results page
            response = requests.get(f"https://www.google.com/search?q={citynm}&tbm=isch&tbs=isz:l&hl=en&sa=X")

            # parse the HTML using BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

            # find all img tags
            image_tags = soup.find_all("img")

            # download each image and save it to the specified directory
            del image_tags[0]
            img_data=[]
            for index,image_tag in enumerate(image_tags):
                # get the image source URL
                image_url = image_tag['src']
                #print(image_url)
                
                # send a request to the image URL and save the image
                image_data = requests.get(image_url).content
                mydict={"Index":index,"Image":image_data}
                img_data.append(mydict)
                imagenm = f"{citynm}_{image_tags.index(image_tag)}.jpg"
                with open(os.path.join(save_directory, imagenm), "wb") as f:
                    f.write(image_data)
                break

            ##Find the longitude and latitude of city
            lonresp = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={citynm}&limit=5&appid={API_KEY}")
            
            logging.info(f"Reponse from remote call for logitude lonresp: {lonresp.content}")
            # JSON respnse from website
            json_resplon = lonresp.json()
            logging.info(f"Reponse from remote call for logitude json_resplon : {json_resplon}")
            resdict = json_resplon[0]
            #lattitude = resdict.get('lat')
            #longitude = resdict.get('lon')
            for key,value in resdict.items():
                   logging.info(f"{key} : {value}")
                   if key == 'lat':
                       lattitude = value
                   elif key == 'lon':
                       longitude = value
            
            #lonsoup = BeautifulSoup(lonresp, 'html.parser')
            #lonsoup_data = json(lonsoup.text)
            #logging.info(f'Ourout of JSON : {lonsoup_data}')
            #longitude = ""
            #lattitude = ""
            #location  = ""
            #countrynm = ""
            #statecd = ""
            #flag = False
            #for d in lonsoup_data:
             #   logging.info(f'Data from the JSON : {d}')
              #  citynmjson = d.get('name')
               # if citynm.upper() == citynmjson.upper():
                #    flag = True
                 #   continue

                #else:
                 #   logging.info(f"Details coming for {citynmjson} are not required to be processed ")
                
                #if flag:
                 #   longitude = d.get('lon')
                  #  lattitude = d.get('lat')
                   # countrynm = d.get('country')
                    #statecd = d.get('state')
            logging.info(f"Details coming for {longitude}, {lattitude} for city {citynm} are not required to be processed ")
            #https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API key}
            weatherresp = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lattitude}&lon={longitude}&appid={API_KEY}&units=metric")

            data = weatherresp.json()
            logging.info(f"Details captured for the {citynm} are as follows : {data}")
            # Parse the JSON string into a Python dictionary
            #data = json.loads(values)
            cur_data =  dict()
            # Access and print specific values from the dictionary
            cur_data["City Name"] =data['name']
            logging.info(f"City Name : {cur_data}")
            cur_data['Date'] =datetime.fromtimestamp(data['dt']).strftime('%Y-%m-%d %H:%M:%S')
            logging.info(f"22222 : {cur_data}")
            cur_data["Coordinates"] = str(data['coord']['lon']) +":"+ str(data['coord']['lat'])
            logging.info(f"33333 : {cur_data}")
            cur_data["Sunrise Time"] =datetime.fromtimestamp(data['sys']['sunrise']).strftime('%Y-%m-%d %H:%M:%S')
            cur_data['Sunset Time '] =datetime.fromtimestamp(data['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S')
            logging.info(f"444444 : {cur_data}")
            cur_data["Weather"] = data['weather'][0]['main']
            cur_data["Current Temp"] =data['main']['temp']
            cur_data["Minimum Temp"] =data['main']['temp_min']
            cur_data["Maximum Temp"] =data['main']['temp_max']
            cur_data["Pressure"] =data['main']['pressure']
            cur_data["Humidity"] =data['main']['humidity']
            cur_data["Visibility"] =data['visibility']
            cur_data["Wind Speed"] =data['wind']['speed']
            cur_data["Wind Degree"] =data['wind']['deg']
            cur_data["Clouds"] =data['clouds']['all']
            
            logging.info(f"Details captured for the {citynm} are as follows : {cur_data}")
            
            image_url = "data:image/png;base64," + base64.b64encode(image_data).decode('utf-8')

            logging.info(f"Image details : {image_url}")
            return render_template('base.html', image_url=image_url, data= cur_data)
        except Exception as e:
            print(e)
            logging.info(e)
            return 'something is wrong'

    else:
        return render_template('index.html')



if __name__ == "__main__":
    app.run(debug=True)
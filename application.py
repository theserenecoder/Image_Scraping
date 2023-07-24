from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import logging
import pymongo
import os

#creating a log file
logging.basicConfig(filename='scrap.log',
                    level=logging.INFO,
                    format='%(name)s %(levelname)s %(message)s')

#creating a folder images if not created to save images
save_dir = "images/"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Windows; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}



application = Flask(__name__)
app = application

#main landiing page
@app.route('/', methods = ['GET'])
@cross_origin()
def homepage():
    return render_template('index.html')

#review page
@app.route('/review', methods = ['Post','GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            #search string entered by user
            query = request.form['content'].replace(" ","")
            #url for query images
            response = requests.get(f"https://www.google.com/search?q={query}&tbm=isch&source=lnms&sa=X&ved=2ahUKEwjX1dba56WAAxXjLzQIHZwIAGAQ0pQJegQIDRAB&biw=1920&bih=947&dpr=1")
            #saving the page content
            soup = bs(response.content, 'html.parser')
            #closing server link
            response.close()
            #saving all images tags on page
            imageTags = soup.find_all('img')
            del imageTags[0]
            imageDataMongo = []

            for i in imageTags:
                try:
                    #saving image url
                    imageURL = i['src']
                except:
                    logging.error("No Image URL")
                
                try:
                    #saving image content
                    imageData = requests.get(imageURL).content
                except:
                    logging.error("No Image available")
                try:
                    #storing image url and image content in a dictionary and appending it into a list
                    myDict = {"Index":imageURL,"Image":imageData}
                    imageDataMongo.append(myDict)
                except:
                    logging.error("No dict object")
                try:
                    #saving image with specified name in image folder
                    with open(os.path.join(save_dir,f"{query}_{imageTags.index(i)}.jpg"),'wb') as f:
                        f.write(imageData)
                except:
                    logging.error("No image saved")
            
            #connecting to mongodb
            client = pymongo.MongoClient("mongodb+srv://theserenecoder:Mukesh90@cluster0.kimqlv5.mongodb.net/?retryWrites=true&w=majority")
            #creating a database
            db = client['imageScraper']
            #creating a collection in our database
            imageColl = db['images']
            #inserting data into our collection
            imageColl.insert_many(imageDataMongo)

            return render_template('result.html')
        
        except Exception as e:
            logging.error(e)
            return "Something is wrong"
    
    else:
        return render_template('index.html')
            


if __name__ == '__main__':
    app.run(host=0.0.0.0, port=8000)

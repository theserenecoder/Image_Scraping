from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import logging
import pymongo
import os

save_dir = "images/"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Windows; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

logging.basicConfig(filename='scrap.log',
                    level=logging.INFO,
                    format='%(name)s %(levelname)s %(message)s')

application = Flask(__name__)
app = application

@app.route('/', methods = ['GET'])
@cross_origin()
def homepage():
    return render_template('index.html')

@app.route('/review', methods = ['Post','GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            query = request.form['content'].replace(" ","")
            response = requests.get(f"https://www.google.com/search?q={query}&tbm=isch&source=lnms&sa=X&ved=2ahUKEwjX1dba56WAAxXjLzQIHZwIAGAQ0pQJegQIDRAB&biw=1920&bih=947&dpr=1")
            soup = bs(response.content, 'html.parser')
            response.close()
            imageTags = soup.find_all('img')
            del imageTags[0]
            imageDataMongo = []

            for i in imageTags:
                try:
                    imageURL = i['src']
                except:
                    logging.error("No Image URL")
                
                try:
                    imageData = requests.get(imageURL).content
                except:
                    logging.error("No Image available")
                try:
                    myDict = {"Index":imageURL,"Image":imageData}
                    imageDataMongo.append(myDict)
                except:
                    logging.error("No dict object")
                try:
                    with open(os.path.join(save_dir,f"{query}_{imageTags.index(i)}.jpg"),'wb') as f:
                        f.write(imageData)
                except:
                    logging.error("No image saved")
            
            client = pymongo.MongoClient("mongodb+srv://theserenecoder:Mukesh90@cluster0.kimqlv5.mongodb.net/?retryWrites=true&w=majority")
            db = client['imageScraper']
            imageColl = db['images']
            imageColl.insert_many(imageDataMongo)

            return render_template('result.html')
        
        except Exception as e:
            logging.error(e)
            return "Something is wrong"
    
    else:
        return render_template('index.html')
            


if __name__ == '__main__':
    app.run(debug=True)
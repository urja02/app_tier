from flask import Flask, render_template, jsonify, request, Response
import sqlite3
__copyright__   = "Copyright 2024, VISA Lab"
__license__     = "MIT"

import os
import csv
import sys
import torch
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
from torchvision import datasets
from torch.utils.data import DataLoader
from app_tier.face_recognition import face_match


app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/api',methods=["POST"])
def getImage():

    
    user_inp = request.files['file'].filename
    print(user_inp)
    res = user_inp[:-4]
    base_path = "/Users/urjagiridharan/Documents/cloud_project/face_images_1000"
    test_image = os.path.join(base_path, user_inp)


    result = face_match(test_image, 'data.pt')
    print(result[0])
    file =    open('/Users/urjagiridharan/Documents/cloud_project/results.text',"a")
    file.write(f"{res}:{result[0]}\n")
    file.close()
    return jsonify({res:result[0]})
if __name__ == '__main__':
    app.run()
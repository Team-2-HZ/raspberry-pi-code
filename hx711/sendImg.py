import requests

imgPath = './images/image_1.jpg'
imgUrl = 'http://localhost:8000/post/image'


def sendImage(weight):
    imgFile = {'file': open(imgPath, 'rb')}
    # post the image and weight to the server
    imgResponse = requests.post(imgUrl, files=imgFile, data={'weight': weight})
    # descrupt the response
    imgResponse = imgResponse.json()

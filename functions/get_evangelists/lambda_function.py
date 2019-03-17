import bs4 as bs
import urllib.request
import boto3
rek = boto3.client('rekognition')

#We are going to parse the AWS Evangelist page for PNG Files and use AWS Rekognition to get some info about them.
source = urllib.request.urlopen('https://aws.amazon.com/developer/community/evangelists/').read()

soup = bs.BeautifulSoup(source,'lxml')

def lambda_handler(event, context):
    # title of the page
    print("Page Title: ", soup.title)

    #Get all of the images in the webpage
    for img in soup.find_all('img'):

        src = "http://" + (img.get('src')).split("//")[1]
        #Make sure we are getting evangelist Bio Pics
        if "png" in src and "evangelist" in src:
            # fetch firstname and last name from alt attribute
            evangelist_name = img.get('alt').title()
            #Open the Image File to pass to Rekognition
            response = urllib.request.urlopen(src)
            data = response.read()

           #Sending to Rekognition
            results = rek.detect_faces(
                Image={
                    'Bytes': data
                },
                Attributes=['ALL']
            )
            #For each face, output some of the attributed identified by AWS Rekognition.
            for face in results["FaceDetails"]:
                msg = "{name} is a {gender} who is between {lowAge} and {highAge}".format(name=evangelist_name,gender=face['Gender']['Value'], lowAge=face['AgeRange']['Low'], highAge=face['AgeRange']['High'])
                print('-------')
                print(msg)
        else:
            print("Not an Evangelist or PNG file")
            
    return "Sucessfully Compeleted"

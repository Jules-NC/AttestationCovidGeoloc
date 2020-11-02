import os
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import qrcode as QRCode
import math
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, request, abort, jsonify, send_from_directory
from flask_cors import CORS
from scipy import spatial

UPLOAD_DIRECTORY = "./"

# Loading DB & het points for kd tree
print("Loading DB...")
df = pd.read_csv("grid_result_IDF.csv")
points = df[['lat','long']].values
ilocs = df.iloc
print("DB loaded")

# Create kd tree
print("Building KD-Tree...")
tree = spatial.KDTree(points)
print("KD-TREE built")


if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Flask init
api = Flask(__name__)
CORS(api)


# Download last file route
@api.route("/file")
def get_file():
    """Download a file."""
    return send_from_directory(UPLOAD_DIRECTORY, "attestation.pdf", as_attachment=True)


# Update file route
@api.route("/update", methods = ['GET', 'POST'])
def update():
    print("------------------------------------------------------------")
    location = (request.args.get('N'), request.args.get('E'))
    name = request.args.get("name")
    birthdate = request.args.get("birthdate")
    birthcity = request.args.get("birthcity")
    

    all_the_bousin(location, name, birthdate, birthcity)
    print("------------------------------------------------------------")
    return "File updated"


def nearest_neighbour(point):
    res = tree.query([point])[1][0]
    return df.iloc[res, :]


def setup(location, name, birthdate, birthcity):
    # Setup db
    global df

    # Get location
    #results = rg.search(coordinates) # default mode = 2

    # Compute dists, get min distance
    #df["point_lat"] = float(coordinates[0])
    #df["point_long"] = float(coordinates[1])
    #df["dist"] = df.apply(lambda x: math.sqrt((x.lat - x.point_lat)**2 + (x.long - x.point_long)**2), axis=1)
    #df2 = df.loc[df['dist'].idxmin()]
    #print(df2)
    coordinates = nearest_neighbour((float(location[0]), float(location[1])))
    print(coordinates)

    # Define Variables
    NAME = name
    BIRTHDATE= birthdate
    BIRTHCITY = birthcity

    time = datetime.now() + timedelta(hours=0, minutes=30) # Because dockerfile is in UTC so i add my timezone 

    CITY = coordinates["city"]
    CITY_CODE = str(coordinates["zipcode"])
    ADRESS = coordinates["adress"]
    NUMBER = coordinates["number"]
    FULL_ADRESS = NUMBER + " " + ADRESS + " " + CITY_CODE + " " + CITY
    DATE = str(time.strftime('%d/%m/%Y'))
    TIME = str(time.strftime('%H:%M'))
    
    fields = {
        "name": NAME,
        "birthcity": birthcity,
        "birthdate": birthdate,
        "full_adress": FULL_ADRESS,
        "city":CITY,
        "date":DATE,
        "time":TIME
    }

    fields_loc  =  {
                NAME: (330, 377),
                BIRTHCITY: (824, 437),
                BIRTHDATE: (330, 437),
                FULL_ADRESS:(369, 498),
                CITY:(290, 1818),
                DATE:(253, 1885),
                TIME:(732, 1885),  
            }
    return (fields, fields_loc)


def all_the_bousin(location, name, birthdate, birthcity):
    # Base infos
    PDF = "blank.pdf"
    FONT = "fonts/micross.ttf"
    FONT_SIZE = 31

    fields, fields_loc = setup(location, name, birthdate, birthcity)
    
    pages = convert_from_path(PDF)

    for i, page in enumerate(pages):
        page.save('out' + str(i) + '.jpg', 'JPEG')

    # Add fields values
    img = Image.open("out0.jpg")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(r'fonts/micross.ttf', 31)
    for text in fields_loc:
        draw.text(fields_loc[text],text,(0,0,0),font=font)

    img.save('sample-out.jpg')

    # QR Code generator
    TEXT = """Cree le: {date} a {h}h{mn};
 Nom: {pastname};
 Prenom: {prename};
 Naissance: {bdate} a {bcity};
 Adresse: {adress};
 Sortie: {date} a {time};
 Motifs: sport_animaux""".format(adress=fields["full_adress"], date=fields["date"], time=fields["time"],
                                 h=fields["time"][:2], mn=fields["time"][3:], pastname = name.split()[1], prename = name.split()[0], bdate=birthdate, bcity=birthcity)

    TEXT = str(TEXT)
    img = QRCode.make(TEXT)
    img.save("qrcode.jpg")

    # Copy on first page
    qrcode = Image.open('qrcode.jpg')
    sample = Image.open('sample-out.jpg')

    qrcode.size
    qrcode.thumbnail((282, 282))

    back_im = sample.copy()
    back_im.paste(qrcode, (1206, 1790))
    back_im.save('result0.jpg')


    #Copy on second page
    qrcode = Image.open('qrcode.jpg')
    qrcode = qrcode.resize((917, 917), 1)

    second_page = Image.open('out1.jpg')

    back_im = second_page.copy()
    back_im.paste(qrcode, (96, 96))
    back_im.save('result1.jpg')

    # Convert img to pdf + merge
    res0 = Image.open('result0.jpg')
    res1 = Image.open('result1.jpg')
    results= [res1]

    filename = "attestation.pdf" # -2020-" + fields["date"][3:5] + "-" + fields["date"][:2] + "_" + fields["time"][:2] + "-" + fields["time"][3:] + ".pdf"
    res0.save(filename, "PDF" ,resolution=100.0, save_all=True, append_images=results)
    print("FILE WRITED OK")


if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True, port=28411)

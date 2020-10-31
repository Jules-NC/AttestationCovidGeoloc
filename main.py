import os
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import qrcode as QRCode
import reverse_geocoder as rg
from datetime import datetime, timedelta
from flask import Flask, request, abort, jsonify, send_from_directory


UPLOAD_DIRECTORY = "./"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

api = Flask(__name__)

@api.route("/file")
def get_file():
    """Download a file."""
    return send_from_directory(UPLOAD_DIRECTORY, "attestation.pdf", as_attachment=True)

@api.route("/update")
def update():
    print("------------------------------------------------------------")
    location = (request.args.get('N'), request.args.get('E'))
    name = request.args.get("name")
    birthdate = request.args.get("birthdate")
    birthcity = request.args.get("birthcity")
    

    all_the_bousin(location, name, birthdate, birthcity)
    print("------------------------------------------------------------")
    return "File updated"



def setup(location, name, birthdate, birthcity):
    # Get location
    coordinates = location
    results = rg.search(coordinates) # default mode = 2

    # Define Variables
    NAME = name
    BIRTHDATE= birthdate
    BIRTHCITY = birthcity

    time = datetime.now() + timedelta(hours=0, minutes=40) # Because dockerfile is in UTC so i add my timezone 

    CITY = results[0]["name"]
    CITY_CODE = "94000"
    ADRESS = "10 allée Bourvil"
    FULL_ADRESS = ADRESS + " " + CITY_CODE + " " + CITY
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

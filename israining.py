import pyproj
import urllib, cStringIO
import Image
import colorsys
import datetime


class RainWizard:
    A = 298.529954775287933
    D = 0.00000000000000
    B = 0.00000000000000
    E = -291.196161556152788
    C = 11502967.777851389721036
    F = 220098.936637653590878

    def __init__(self):
        self.getImage();

    def frompixel(self, px, py):
        px += 0.5; 
        py += 0.5;
    
        return ((self.A*px + self.B*py + self.C), (self.D*px + self.E*py + self.F));
    
    def topixel(self,x,y):
        px = (x-self.B*(y-self.F) - self.C)/ (self.A-self.B*self.D)
        py = (y - self.D *(px) - self.F)/self.E
        
        return (round(px-0.5), round(py-0.5));
    
    def fromlatlng(self,lat,lng):
        src = pyproj.Proj(init='EPSG:4326');
        dst = pyproj.Proj(init='EPSG:3785');
    
        x2,y2 = pyproj.transform(src, dst, lat, lng);
        x, y = self.topixel(x2,y2)
    
        return (x, y)

    def getImage(self):
        self.created_at = datetime.datetime.now()
        self.file = cStringIO.StringIO(urllib.urlopen("http://www.weather.gov.sg/wip/pp/rndops/web/ship/gif/rad70.gif").read())
        self.rgb_img = Image.open(self.file).convert('RGB')

    def getPixelColor(self, lat, lng):

        x,y = self.fromlatlng(lng,lat)

        r, g, b = self.rgb_img.getpixel((x, y))

        return r, g, b

    def isRaining(self, lat, lng):
        if ((datetime.datetime.now() - self.created_at).seconds > 300):
            self.getImage()

        r,g,b = self.getPixelColor(lat, lng)
        h,s, l = colorsys.rgb_to_hls(r/255.0,g/255.0,b/255.0)
        print r/255.0,g/255.0,b/255.0
        print h,s,l
        if (s != 1.0 and l != 1.0):
            return (False, -1)
        else:
            return (True, h)

from flask import Flask, render_template, request

app = Flask(__name__)
app.debug = True

rainW = RainWizard()

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/sg/")
def isRaining():
    lat = request.args.get('lat', 0)
    lng = request.args.get('lng', 0)

    r,g,b = rainW.getPixelColor(lat,lng)
    res = rainW.isRaining(lat,lng)
    return "{ raining: %s, 'intensity': %d}" % (('true' if res[0] else 'false'),res[1]*255)

if __name__ == "__main__":
    app.run()



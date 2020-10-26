from http.server import BaseHTTPRequestHandler
from robohash import Robohash
import io
import base64
import urllib


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Set default values
        sizex = 300
        sizey = 300
        format = "png"
        bgset = None
        color = None

        parsed_path = urllib.parse.urlparse(self.path)
        args = urllib.parse.parse_qs(parsed_path.query)

        address = args.get('address').pop()

        # Ensure we have something to hash!
        if address is None:
            address = self.request.remote_ip

        # Split the size variable in to sizex and sizey
        if "size" in args:
            sizex, sizey = args.get('size').pop().split("x")
            sizex = int(sizex)
            sizey = int(sizey)
            if sizex > 4096 or sizex < 0:
                sizex = 300
            if sizey > 4096 or sizey < 0:
                sizey = 300

        # Create our Robohashing object
        r = Robohash(address)

        # Build our Robot.
        r.assemble(roboset='set1', format=format, bgset=bgset,
                   color=color, sizex=sizex, sizey=sizey)

        self.send_response(200)

        # We're going to be returning the image directly, so tell the browser to expect a binary.
        self.send_header("Content-Type", "image/" + format)
        self.send_header("Cache-Control", "public,max-age=31536000")
        self.end_headers()

        # Print the Robot to the handler, as a file-like obj
        if r.format != 'datauri':
            r.img.save(self.wfile, format=format)
        else:
            # Or, if requested, base64 encode first.
            fakefile = io.BytesIO()
            r.img.save(fakefile, format='PNG')
            fakefile.seek(0)
            b64ver = base64.b64encode(fakefile.read())
            b64ver = b64ver.decode('utf-8')
            self.wfile.write("data:image/png;base64," + str(b64ver))

        return

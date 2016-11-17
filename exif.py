import io, sys, os
from PIL import Image
import piexif

class ExifEditer:
    def __init__(self):
        self.id = 0

    def write_exif(self, path, artist, desc, comment, rating):
        try:
            zeroth_ifd = {piexif.ImageIFD.Artist: artist.encode('ascii'),
                          piexif.ImageIFD.ImageDescription: desc.encode('ascii'),
                          piexif.ImageIFD.Rating: rating}
            exif_ifd = {piexif.ExifIFD.UserComment: u''.join(comment).encode('utf-8').strip()}

            exif_dict = {"0th":zeroth_ifd, "Exif":exif_ifd}
            exif_bytes = piexif.dump(exif_dict)
            im = Image.open(path)
            im.load()
            if im.mode != "RGB":
                im = im.convert("RGB")
            if os.stat(path).st_size >= 2048:
                im.save(path,format=im.format, exif=exif_bytes)
        except IOError:
            sys.stdout.write(' ' * 79 + '\r')
            sys.stdout.write('IOError @ '+path+'\n')
            pass # You can always log it to logger
        except OSError:
            sys.stdout.write(' ' * 79 + '\r')
            sys.stdout.write('OSError @ '+path+'\n')
            pass # You can always log it to logger
        except UnicodeEncodeError:
            sys.stdout.write(' ' * 79 + '\r')
            sys.stdout.write('UnicodeEncodeError @ '+path+'\n')
            pass # You can always log it to logger

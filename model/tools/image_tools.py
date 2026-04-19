from PIL import Image, ImageDraw

class ImageTools:
    @staticmethod
    def create_status_image(color):
        """Erzeugt ein Icon mit der angegebenen Farbe (RGB). Und Pixe"""
        image = Image.new('RGB', (64, 64), (30, 30, 30))
        dc = ImageDraw.Draw(image)
        dc.ellipse((10, 10, 50, 50), fill=color)
        return image

if __name__ == "__main__":
    ImageTools.create_status_image(color=(0, 255, 0)).show()
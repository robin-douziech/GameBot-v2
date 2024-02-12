from PIL import Image
import copy, random, re
import numpy as np

image_finder_answers = {
	"narak.jpg": ["narak"]
	
}

def check_answer(image_name, answer) :
	for valid_answer in image_finder_answers[image_name] :
		if valid_answer.lower() in answer.lower() :
			return True
		elif re.match(r""+valid_answer, answer) :
			return True
	return False

def blur(image, n) :
	longueur, hauteur = image.size

	if longueur > hauteur :
		pixel_size = longueur//n
	else :
		pixel_size = hauteur//n
	pixel_nb = (int(longueur//pixel_size), int(hauteur//pixel_size))

	new_image = Image.new('RGB', (pixel_size*pixel_nb[0], pixel_size*pixel_nb[1]), (0, 0, 0))

	for i in range(pixel_nb[0]) :
		for j in range(pixel_nb[1]) :
			color = np.array([0, 0, 0])
			for k in range(i*pixel_size, (i+1)*pixel_size) :
				for l in range(j*pixel_size, (j+1)*pixel_size) :
					color += np.array(image.getpixel((k, l)))
			color[0] /= (pixel_size**2)
			color[1] /= (pixel_size**2)
			color[2] /= (pixel_size**2)
			for k in range(i*pixel_size, (i+1)*pixel_size) :
				for l in range(j*pixel_size, (j+1)*pixel_size) :
					new_image.putpixel((k, l), tuple(color))
	return new_image


new_image = black_and_white(blur(image, 10))
new_image.save("images/narak2.jpg")


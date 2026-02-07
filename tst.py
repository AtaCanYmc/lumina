from lumina import *

img_path = "assets/images/example_input.jpg"
img_path_2 = "assets/images/example_input_2.jpg"

if __name__ == "__main__":
    #m = flat_lithophane(img_path, resolution=5)
    #m.save("assets/stl/example_output.stl")

    m2 = flat_lithophane(img_path_2, resolution=5, shape='circle', width_mm=100, height_mm=100)
    m2.save("assets/stl/example_output_2.stl")

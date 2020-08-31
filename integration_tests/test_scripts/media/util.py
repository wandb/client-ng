import object3D
import point_cloud_scene
import molecule
import table
import html_script
import video
import image_bounding_box
import image_mask
import image
import sys
import os
# Add current directory so we can run this as a module
sys.path.append(os.path.dirname(__file__))

# This conflict with a local library with we aren't explicit about the
# locak dir
# import plotly_fig
# import matplotlib_fig


project_name = "all-media-test"


all_tests = {}
all_tests.update(image.all_tests)
all_tests.update(image_mask.all_tests)
all_tests.update(image_bounding_box.all_tests)
all_tests.update(video.all_tests)
all_tests.update(html_script.all_tests)
all_tests.update(table.all_tests)
all_tests.update(molecule.all_tests)
all_tests.update(point_cloud_scene.all_tests)
all_tests.update(object3D.all_tests)
# all_tests.update(plotly_fig.all_tests)
# all_tests.update(matplotlib_fig.all_tests)

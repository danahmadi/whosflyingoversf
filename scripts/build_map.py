from common import *
import map_component
D = load_data()
write('map.html', page('Flight map', 'Explore possible banner-tow aircraft tracks over San Francisco and compare dates with public sightings.', '/map', map_component.panel(), map_component.scripts(D['brands']), map_component.HEAD))

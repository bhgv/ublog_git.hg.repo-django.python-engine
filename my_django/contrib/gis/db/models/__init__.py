# Want to get everything from the 'normal' models package.
from my_django.db.models import *

# Geographic aggregate functions
from my_django.contrib.gis.db.models.aggregates import *

# The GeoManager
from my_django.contrib.gis.db.models.manager import GeoManager

# The geographic-enabled fields.
from my_django.contrib.gis.db.models.fields import (
     GeometryField, PointField, LineStringField, PolygonField,
     MultiPointField, MultiLineStringField, MultiPolygonField,
     GeometryCollectionField)

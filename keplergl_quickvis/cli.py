"""Console script for kepler_quickvis."""
import sys
from pathlib import Path

import click
import geojson
import geopandas as gpd

from keplergl_quickvis import Visualize


# https://stackoverflow.com/a/45845513
def get_stdin(ctx, param, value):
    if not value and not click.get_text_stream('stdin').isatty():
        return click.get_text_stream('stdin').read().strip()
    else:
        return value


@click.command()
@click.option(
    '--api_key',
    type=str,
    default=None,
    help=
    'Mapbox API Key. Must be provided on the command line or exist in the MAPBOX_API_KEY environment variable.'
)
@click.option(
    '--style',
    type=str,
    default='streets',
    show_default=True,
    help=
    'Mapbox style. Accepted values are: streets, outdoors, light, dark, satellite, satellite-streets, or a custom style URL.'
)
@click.argument('files', nargs=-1, required=True, callback=get_stdin, type=str)
def main(api_key, style, files):
    """Interactively view geospatial data using kepler.gl"""
    vis = Visualize(api_key=api_key, style=style)

    # For each file, try to load data with GeoPandas
    for item in files:
        # If body exists as a path; assume it represents a Path
        try:
            path = Path(item)
            if path.exists():
                gdf, layer_name = load_file(path)
                vis.add_data(gdf, layer_name)
                continue

        except OSError:
            pass

        # Otherwise, it should be GeoJSON
        # Parse with geojson.loads to make sure
        geojson.loads(item)
        vis.add_data(item)

    vis.render(open_browser=True, read_only=False)
    return 0


def load_file(path):
    """Load geospatial data at path

    Loads data with GeoPandas; reprojects to 4326
    """
    layer_name = path.stem
    gdf = gpd.read_file(path)

    # Try to automatically reproject to epsg 4326
    # For some reason, it takes forever to call gdf.crs, so I don't want
    # to first check the crs, then reproject. Anyways, reprojecting from
    # epsg 4326 to epsg 4326 should be instant
    try:
        gdf = gdf.to_crs(epsg=4326)
    except:
        pass

    return gdf, layer_name


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

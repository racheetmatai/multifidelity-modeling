import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

def read_raster_file(filename):
    """
    Read raster file using rasterio.

    :param filename: Name of the file.
    :return: Raster data and metadata.
    """
    file = rasterio.open(filename, 'r')
    data = file.read(1)  # Reading the first band
    return file, data

def resample_raster(src_raster, src_data, target_raster):
    """
    Resample source raster data to match the target raster grid.

    :param src_raster: Source raster file.
    :param src_data: Source raster data.
    :param target_raster: Target raster file.
    :return: Resampled data.
    """
    transform, width, height = calculate_default_transform(
        src_raster.crs, target_raster.crs, target_raster.width, target_raster.height, *target_raster.bounds)
    
    resampled_data = np.empty((height, width), dtype=src_data.dtype)

    reproject(
        source=src_data,
        destination=resampled_data,
        src_transform=src_raster.transform,
        src_crs=src_raster.crs,
        dst_transform=transform,
        dst_crs=target_raster.crs,
        resampling=Resampling.bilinear,  # You can choose different resampling methods
    )

    return resampled_data

def save_raster(data, reference_raster, filename):
    """
    Save the resampled raster data to a new file.

    :param data: Resampled raster data.
    :param reference_raster: Reference raster file.
    :param filename: Name of the new file.
    """
    profile = reference_raster.profile
    profile.update(
        dtype=rasterio.float32,
        count=1,
        compress='lzw'
    )

    with rasterio.open(filename, 'w', **profile) as dst:
        dst.write(data, 1)

def get_df(tif_file, tif_data, name):
    # Extract coordinates
    transform = tif_file.transform
    width = tif_file.width
    height = tif_file.height

    xs, ys = np.meshgrid(np.arange(width), np.arange(height))
    x_coords, y_coords = rasterio.transform.xy(transform, ys, xs)

    # Flatten arrays
    x_coords = np.array(x_coords).flatten()
    y_coords = np.array(y_coords).flatten()

    # Create DataFrame
    df = pd.DataFrame({
        'x': x_coords,
        'y': y_coords,
    })
    df[name] = tif_data.flatten()
    return df

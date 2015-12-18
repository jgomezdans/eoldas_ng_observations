import netCDF4 
import numpy as np

import numpy as np
import datetime as dt
import os
import gdal
import netCDF4

from best_chunk import chunk_shape_3D

class OutputFile ( object ):
    def __init__ ( self, fname, times=None, input_file=None ):
        self.fname = fname
        self.create_netcdf ( times )
        if input_file is not None:
            self._get_spatial_metadata ( input_file )
            self.create_spatial_domain( )
        
    def _get_spatial_metadata ( self, geofile, basedate=dt.datetime(1858,11,17,0,0,0) ):
        g = gdal.Open ( geofile )
        if g is None:
            raise IOError ("File %s not readable by GDAL" % geofile )
        ny, nx = g.RasterYSize, g.RasterXSize
        geo_transform = g.GetGeoTransform ()
        self.x = np.arange ( nx )*geo_transform[1] + geo_transform[0]
        self.y = np.arange ( ny )*geo_transform[5] + geo_transform[3]
        self.nx = nx
        self.ny = ny
        self.basedate = basedate
        self.wkt = g.GetProjectionRef()

    def create_netcdf ( self, times=None ):
        
        self.nc = netCDF4.Dataset( self.fname, 'w', clobber=True )


        # create dimensions, variables and attributes:
        if times is None:
            self.nc.createDimension( 'time', None )
        else:
            self.nc.createDimension( 'time', len ( times ) )
        timeo = self.nc.createVariable( 'time', 'f4', ('time') )
        timeo.units = 'days since 1858-11-17 00:00:00'
        timeo.standard_name = 'time'
        timeo.calendar = "Gregorian"
        if times is not None:
            timeo[:] = netCDF4.date2num ( times, units=timeo.units, 
                                         calendar=timeo.calendar )

    def create_spatial_domain ( self ):
        self.nc.createDimension( 'x', self.nx )
        self.nc.createDimension( 'y', self.ny )

        xo = self.nc.createVariable('x','f4',('x'))
        xo.units = 'm'
        xo.standard_name = 'projection_x_coordinate'

        yo = self.nc.createVariable('y','f4',('y'))
        yo.units = 'm'

        # create container variable for CRS: x/y WKT
        crso = self.nc.createVariable('crs','i4')
        crso.grid_mapping_name ( srs )
        crso.crs_wkt ( self.wkt )
        xo[:] = self.x
        yo[:] = self.y
        self.nc.Conventions='CF-1.7'

    def create_group ( self, group ):
        self.nc.createGroup ( group )

    def create_variable ( self, group, varname, vardata,
            units, long_name, std_name, vartype='f4' ):
        varo = self.nc.group.createVariable(varname, vartype,  ('time', 'y', 'x'), 
            zlib=True,chunksizes=[16, 12, 12],fill_value=-9999)
        varo.units = units
        varo.scale_factor = 1.00
        varo.add_offset = 0.00
        varo.long_name = long_name
        varo.standard_name = std_name
        varo.grid_mapping = 'crs'
        varo.set_auto_maskandscale(False)
        varo[:,...] = vardata
    
    def set_variable ( self, varname, var ):
        self.nc[varname][:,...] = var 

    def __del__ ( self )
        self.nc.close()

def pkl_to_nc4 ( pk_file, nc_output, the_state ):

        with open ( pk_file, 'r' ) as fp:
            f = cPickle.load ( fp )


            nc = netCDF4.Dataset(nc_output,'w',format='NETCDF4')
            print nc.file_format

            lat = nc.createDimension('lat', 1)
            lon = nc.createDimension('lon', 1)
            time = nc.createDimension('time', 365)
            n_lat = len ( lat )
            n_lon = len ( lon )
            n_time = len ( time )


            times = nc.createVariable('time', np.float64, ('time',))
            latitudes = nc.createVariable('latitude', np.float32,
            ('lat',))
            longitudes = nc.createVariable('longitude', np.float32,
            ('lon',))
            # Create the actual variables from the pkl file...

            groups=[]
            variables=[]
            for group in f.iterkeys():
                if group == "post_sigma":
                    continue
                elif group == "post_cov":
                    continue
                else:
                    this_group = nc.createGroup ( group )
                    for variable in f[group].iterkeys():
                        this_var = this_group.createVariable ( variable, np.float32,
                                ('time', 'lat','lon'))
                        output = np.ones (( n_time, n_lat, n_lon ))
                        try:
                            output[:,:,:] = f[group][variable][:, None, None]
                        except: 
                            output[:,:,:] = f[group][variable]

                        this_var[:, :, :] = output


                    
        nc.close() 
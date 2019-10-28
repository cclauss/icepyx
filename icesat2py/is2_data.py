#import numpy as np
import datetime as dt
#import re

class Icesat2Data():
    """
    ICESat-2 Data object to query, obtain, and perform basic operations on 
    available ICESat-2 datasets using temporal and spatial input parameters. 
    Allows the easy input and formatting of search parameters to match the 
    NASA NSIDC DAAC and conversion to multiple data types.
    
    Parameters
    ----------
    dataset : string
        ICESat-2 dataset ID, also known as "short name" (e.g. ATL03). 
        Available datasets can be found at: https://nsidc.org/data/icesat-2/data-sets
    spatial_extent : list
        Spatial extent of interest, provided as a bounding box. 
        Bounding box coordinates should be provided in decimal degrees as
        [lower-left-longitude, lower-left-latitute, upper-right-longitude, upper-right-latitude].
        DevGoal: allow broader input of polygons and polygon files (e.g. kml, shp) as bounding areas
    date_range : list of 'YYYY-MM-DD' strings
        Date range of interest, provided as start and end dates, inclusive.
        The required date format is 'YYYY-MM-DD' strings, where
        YYYY = 4 digit year, MM = 2 digit month, DD = 2 digit day.
        Currently, a list of specific dates (rather than a range) is not accepted.
        DevGoal: accept date-time objects, dicts (with 'start_date' and 'end_date' keys, and DOY inputs).
        DevGoal: allow searches with a list of dates, rather than a range.
    start_time : HH:mm:ss, default 00:00:00
        Start time in UTC/Zulu (24 hour clock). If None, use default.
        DevGoal: check for time in date-range date-time object, if that's used for input.
    end_time : HH:mm:ss, default 23:59:59
        End time in UTC/Zulu (24 hour clock). If None, use default.
        DevGoal: check for time in date-range date-time object, if that's used for input.
    version : string, default most recent version
        Dataset version, given as a 3 digit string. If no version is given, the current
        version is used.
        Current version (Oct 2019): 001
    
        
    See Also
    --------


    Examples
    --------
    Initializing Icesat2Data with a bounding box.
    >>> sho
    >>> reg_a_bbox = [lllong, lllat, urlong, urlat]
    >>> reg_a_dates = ['2019-02-22','2019-02-28']
    >>> region_a = icepyx.Icesat2Data('ATL06', reg_a_bbox, reg_a_dates)
    >>> region_a
    [show output here after inputting above info and running it]
    """

    # ----------------------------------------------------------------------
    # Constructors

    def __init__(
        self,
        dataset = None,
        spatial_extent = None,
        date_range = None,
        start_time = None,
        end_time = None,
        version = None,
    ):
        
        if dataset is None or spatial_extent is None or date_range is None:
            raise ValueError("Please provide the required inputs. Use help([function]) to view the function's documentation")

            
        if isinstance(dataset, str):
            self.dset = str.upper(dataset)
            assert self.dset in ['ATL02', 'ATL03', 'ATL04','ATL06', 'ATL07', 'ATL08', 'ATL09', 'ATL10', 'ATL12', 'ATL13'],\
            "Please enter a valid dataset"
        else:
            raise ValueError("Please enter a dataset string")
         
        if isinstance(spatial_extent, list):
            if len(spatial_extent)==4:
                #BestPractices: move these assertions to a more general set of tests for valid geometries?
                assert -90 <= spatial_extent[1] <= 90, "Invalid latitude value"
                assert -90 <= spatial_extent[3] <= 90, "Invalid latitude value"
                assert -180 <= spatial_extent[0] <= 360, "Invalid longitude value" #tighten these ranges depending on actual allowed inputs
                assert -180 <= spatial_extent[2] <= 360, "Invalid longitude value"
                assert spatial_extent[0] <= spatial_extent[2], "Invalid bounding box longitudes"
                assert spatial_extent[1] <= spatial_extent[3], "Invalid bounding box latitudes"
                self.spat_extent = spatial_extent
                self.extent_type = 'bbox'
            else:
                raise ValueError('Your spatial extent bounding box needs to have four entries')
                           
            
        if isinstance(date_range, list):
            if len(date_range)==2:
                self.start = dt.datetime.strptime(date_range[0], '%Y-%m-%d')
                self.end = dt.datetime.strptime(date_range[1], '%Y-%m-%d')
                #BestPractices: can the check that it's a valid date entry be implicit (e.g. by converting it to a datetime object, as done here?) or must it be more explicit?
                assert self.start.date() <= self.end.date(), "Your date range is invalid"               
            else:
                raise ValueError("Your date range list is the wrong length. It should have start and end dates only.")
            
#         elif isinstance(date_range, date-time object):
#             print('it is a date-time object')
#         elif isinstance(date_range, dict):
#             print('it is a dictionary. now check the keys for start and end dates')
                        
        
        if start_time is None:
            self.start = self.start.combine(self.start.date(),dt.datetime.strptime('00:00:00', '%H:%M:%S').time())
        else:
            if isinstance(start_time, str):
                self.start = self.start.combine(self.start.date(),dt.datetime.strptime(start_time, '%H:%M:%S').time())
            else:
                raise ValueError("Please enter your start time as a string")
        
        if end_time is None:
            self.end = self.start.combine(self.end.date(),dt.datetime.strptime('23:59:59', '%H:%M:%S').time())
        else:
            if isinstance(end_time, str):
                self.end = self.start.combine(self.end.date(),dt.datetime.strptime(end_time, '%H:%M:%S').time())
            else:
                raise ValueError("Please enter your end time as a string")
                
        if version is None:
            self.version = '001'
            #DevGoal: query data for what's available and get most recent version
        else:
            if isinstance(version, str):
                assert int(version)>0, "Version number must be positive"
                vers_length = 3
                self.version = version.zfill(vers_length)
            else:
                raise ValueError("Please enter the version number as a string")

           
    
    # ----------------------------------------------------------------------
    # Properties
    
    @property
    def dataset(self):
        """
        Return the short name dataset ID string associated with the ICESat-2 data object.
        
        Example
        --------
        >>> region_a = [define that here]
        >>> region_a.dataset
        [put output here]
        """
        return self.dset
    
    @property
    def spatial_extent(self):
        """
        Return an array showing the spatial extent of the ICESat-2 data object.
        Spatial extent is returned as an input type followed by the geometry data.
        Bounding box data is [lower-left-longitude, lower-left-latitute, upper-right-longitude, upper-right-latitude].

        Examples
        --------
        >>> region_a = [define that here]
        >>> region_a.spatial_extent
        [put output here]
        """
        
        if self.extent_type is 'bbox':
            return ['bounding box', self.spat_extent]
        else:
            return ['unknown spatial type', self.spat_extent]
         
        
    @property
    def dates(self):
        """
        Return an array showing the date range of the ICESat-2 data object.
        Dates are returned as an array containing the start and end datetime objects, inclusive, in that order.

        Examples
        --------
        >>> region_a = [define that here]
        >>> region_a.dates
        [put output here]
        """
        return [self.start.strftime('%Y-%m-%d'), self.end.strftime('%Y-%m-%d')] #could also use self.start.date()
    
    
    @property
    def start_time(self):
        """
        Return the start time specified for the start date.
        
        Example
        --------
        >>> region_a = [define that here]
        >>> region_a.start_time
        [put output here]
        """
        return self.start.strftime('%H:%M:%S')

    @property
    def end_time(self):
        """
        Return the end time specified for the end date.
        
        Example
        --------
        >>> region_a = [define that here]
        >>> region_a.end_time
        [put output here]
        """
        return self.end.strftime('%H:%M:%S')
    
    @property
    def dataset_version(self):
        """
        Return the dataset version of the data object.
        
        Example
        --------
        >>> region_a = [define that here]
        >>> region_a.dataset_version
        [put output here]
        """
        return self.version

    #Note: Would it be helpful to also have start and end properties that give the start/end date+time?
    
    # ----------------------------------------------------------------------
    # Static Methods

#     @staticmethod
#     def earthdata_login(self):
        
    
#     @staticmethod
#     def time_range_params(time_range): #initial version copied from topohack; ultimately will be modified heavily
#         """
#         Construct 'temporal' parameter for API call.

#         :param time_range: dictionary with specific time range
#                            *Required_keys* - 'start_date', 'end_date'
#                            *Format* - 'yyyy-mm-dd'

#         :return: Time string for request parameter or None if required keys are
#                  missing.
#         """
#         start_time = '00:00:00'  # Start time in HH:mm:ss format
#         end_time = '23:59:59'    # End time in HH:mm:ss format

#         if 'start_date' not in time_range or 'end_date' not in time_range:
#             return None

#         return f"{time_range['start_date']}T{start_time}Z," \
#             f"{time_range['end_date']}T{end_time}Z"
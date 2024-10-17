import pandas as pd
from obspy import UTCDateTime
from obspy.core import Stream, Trace
import numpy as np
import os
from datetime import datetime
import logging


class CSVToMiniSEEDConverter:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)
    
    def convert_csv_to_miniseed(self, csv_file_path):
        """Convert a single CSV file to MiniSEED format."""
        if not os.path.exists(csv_file_path) or not csv_file_path.endswith('.csv'):
            self.logger.error(f"Invalid CSV file path provided: {csv_file_path}")
            return

        self.logger.info(f"Starting the conversion process for: {csv_file_path}")
        output_mseed_file = csv_file_path.replace('.csv', '.mseed')
        
        try:
            # Start the conversion
            self.csv_to_miniseed(csv_file_path, output_mseed_file)
        except Exception as e:
            self.logger.error(f"Failed to convert {csv_file_path} to MiniSEED: {str(e)}")
        else:
            # Only log success if no exception occurs
            if os.path.exists(output_mseed_file):  # Ensure file was created
                self.logger.info(f"Successfully converted {csv_file_path} to {output_mseed_file}.")
            else:
                self.logger.error(f"Conversion failed, MiniSEED file was not created for {csv_file_path}")


    def csv_to_miniseed(self, csv_file, output_mseed_file):
        """Convert a single CSV file to MiniSEED format."""
        try:
            self.logger.info(f"Reading CSV file: {csv_file}")
            metadata, data = self.read_csv_file(csv_file)

            # Extract metadata and convert date to UTCDateTime
            date_str, latitude, longitude = self.extract_metadata(metadata)
            start_time = self.convert_to_utc(date_str)
            self.logger.info(f"Extracted metadata - Date: {date_str}, Latitude: {latitude}, Longitude: {longitude}")

            # Validate data columns
            self.validate_data_columns(data, csv_file)

            # Prepare traces for X, Y, Z data
            stream = self.prepare_traces(data, start_time)

            # Write the stream to MiniSEED format
            stream.write(output_mseed_file, format='MSEED')
            self.logger.info(f"CSV successfully converted to MiniSEED: {output_mseed_file}")

        except Exception as e:
            self.logger.error(f"Failed to convert {csv_file} to MiniSEED: {str(e)}")
            raise


    def read_csv_file(self, csv_file):
        """Read the CSV file, separating metadata and data."""
        try:
            metadata = pd.read_csv(csv_file, nrows=1)  # First row for metadata
            data = pd.read_csv(csv_file, skiprows=2)    # Skip first two rows for data
            self.logger.info(f"Successfully read CSV file: {csv_file}")
            return metadata, data
        except Exception as e:
            self.logger.error(f"Error reading {csv_file}: {str(e)}")
            raise

    def extract_metadata(self, metadata):
        """Extract date, latitude, and longitude from the metadata."""
        try:
            date_str = f"{metadata['Date'][0]} {metadata['Time'][0]}"
            latitude = float(metadata['Latitude'][0])
            longitude = float(metadata['Longitude'][0])
            self.logger.info(f"Extracted metadata - Date string: {date_str}, Latitude: {latitude}, Longitude: {longitude}")
            return date_str, latitude, longitude
        except (KeyError, ValueError, IndexError) as e:
            self.logger.error(f"Metadata extraction failed: {str(e)}")
            raise ValueError(f"Metadata extraction failed for {metadata}")

    def convert_to_utc(self, date_str):
        """Convert date from dd/mm/yyyy to UTCDateTime."""
        try:
            date_object = datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
            return UTCDateTime(date_object)
        except ValueError as e:
            self.logger.error(f"Date conversion failed for date string '{date_str}': {str(e)}")
            raise

    def validate_data_columns(self, data, csv_file):
        """Ensure that the necessary data columns are present."""
        required_columns = ['Xdata', 'Ydata', 'Zdata']
        if not all(col in data.columns for col in required_columns):
            self.logger.error(f"Data columns 'Xdata', 'Ydata', 'Zdata' not found in {csv_file}.")
            raise ValueError(f"Missing required data columns in {csv_file}.")

    def prepare_traces(self, data, start_time, sampling_rate=1):
        """Prepare the Trace objects for X, Y, and Z data."""
        X_data = data['Xdata'].values
        Y_data = data['Ydata'].values
        Z_data = data['Zdata'].values

        trace_X = self.create_trace(X_data, start_time, sampling_rate, "X")
        trace_Y = self.create_trace(Y_data, start_time, sampling_rate, "Y")
        trace_Z = self.create_trace(Z_data, start_time, sampling_rate, "Z")

        return Stream(traces=[trace_X, trace_Y, trace_Z])

    def create_trace(self, data_array, start_time, sampling_rate, channel):
        """Create a single Trace object."""
        trace = Trace(data=np.array(data_array, dtype=np.float32))
        trace.stats.starttime = start_time
        trace.stats.sampling_rate = sampling_rate
        trace.stats.station = "STA"
        trace.stats.channel = channel
        return trace

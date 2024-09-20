

import subprocess
import json
import os
import shutil
from collections import defaultdict
from datetime import datetime
from tqdm import tqdm  

def get_metadata(file_path):
    try:
        # Run ExifTool and capture the output
        result = subprocess.run(['exiftool', '-j', file_path], capture_output=True, text=True, check=True)
        # Parse JSON output
        metadata = json.loads(result.stdout)[0]
        # Extract desired properties
        file_name = metadata.get('FileName', '')
        desired_properties = {
            'CameraSerialNumber': metadata.get('CameraSerialNumber'),
            'Model': metadata.get('Model'),
            'TrackCreateDate': metadata.get('TrackCreateDate'),
            'FileName': file_name
        }

        # Analyze filename to determine video type
        base_name = os.path.splitext(file_name)[0]  # Remove extension
        prefix = base_name[:2]  # First 2 characters
        middle_part = base_name[2:4]  # Next 2 characters
        file_number = base_name[4:]  # Remaining characters

        # Determine video type
        if prefix in ['GH', 'GX']:
            if middle_part.isdigit() and len(file_number) == 4:
                # Chaptered video
                video_type = 'Chaptered'
            elif middle_part.isalpha() and len(file_number) == 4:
                # Looped video
                video_type = 'Looped'
            else:
                video_type = 'Unknown'
        else:
            video_type = 'Unknown'
        
        desired_properties['VideoType'] = video_type
        return desired_properties
    except Exception as e:
        print(f"Error reading metadata for {file_path}: {e}")
        return None


def process_videos_in_folder(input_folder_path, output_folder_path, min_date_time=datetime(1900, 1, 1, 00, 00, 00), max_date_time=datetime.now(), operation='move'):
    """
        input_folder_path: Please enter input folder path
        output_folder_path: Please enter output folder path
        min_date_time: Start date of files to transfer, default => datetime(1900, 1, 1, 00, 00, 00)
        max_date_time: End date of files to transfer, default => datetime.now()
        operation: Choose operation 'move' or 'copy', default=> 'move'
    """
    try:
        print(f"Starting to process videos in folder: {input_folder_path}")
        files = os.listdir(input_folder_path)
        video_files = [f for f in files if f.lower().endswith(('.mp4', '.mov', '.avi'))]
        # Create a list of image files
        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp'))]

        print(f"Found {len(video_files)} video files to process.")
        
        metadata_results = {}
        videos_by_serial = defaultdict(lambda: defaultdict(list))
        
        # Get metadata of video files to classify them
        for video_file in video_files:
            file_path = os.path.join(input_folder_path, video_file)
            print(f"Processing {file_path}...")
            metadata = get_metadata(file_path)
            
            if metadata:
                track_create_date = metadata.get('TrackCreateDate')
                if track_create_date:
                    video_datetime = datetime.strptime(track_create_date, '%Y:%m:%d %H:%M:%S')
                    if (video_datetime >= min_date_time) & (video_datetime < max_date_time):
                        metadata_results[video_file] = metadata
                        serial_number = metadata.get('CameraSerialNumber', 'UnknownSerial')
                        video_type = metadata['VideoType']
                        videos_by_serial[serial_number][video_type].append((file_path, metadata.get('TrackCreateDate')))
        
        # Create folders and transfer files according to the serial numbers that videos are taken
        for serial_number, types in videos_by_serial.items():
            serial_folder = os.path.join(output_folder_path, serial_number)
            os.makedirs(serial_folder, exist_ok=True)
            print(f"Created folder for serial number {serial_number}")
            
            for video_type, videos in types.items():
                print(f"Processing {video_type} videos for serial number {serial_number}")
                if video_type == 'Chaptered':
                    grouped_by_number = defaultdict(list)
                    for video, track_create_date in videos:
                        base_name = os.path.splitext(os.path.basename(video))[0]
                        file_number = base_name[4:]
                        grouped_by_number[file_number].append((video, track_create_date))
                    
                    for file_number, vids in grouped_by_number.items():
                        first_video_timestamp = vids[0][1]
                        if first_video_timestamp:
                            formatted_timestamp = datetime.strptime(first_video_timestamp, '%Y:%m:%d %H:%M:%S').strftime('%Y%m%d_%H%M%S')
                        else:
                            formatted_timestamp = 'UnknownTimestamp'

                        timestamp_folder = os.path.join(serial_folder, formatted_timestamp)
                        os.makedirs(timestamp_folder, exist_ok=True)
                        print(f"Created timestamp folder {timestamp_folder} for Chaptered videos.")
                        
                        # Adding progress bar for file operations
                        with tqdm(total=len(vids), desc=f"Processing {video_type} videos", unit="file") as pbar:
                            for vid, _ in vids:
                                try:
                                    if operation == 'move':
                                        shutil.move(vid, os.path.join(timestamp_folder, os.path.basename(vid)))
                                        print(f"Moved video {vid} to {timestamp_folder}")
                                    elif operation == 'copy':
                                        shutil.copy2(vid, os.path.join(timestamp_folder, os.path.basename(vid)))
                                        print(f"Copied video {vid} to {timestamp_folder}")
                                    pbar.update(1)  # Update progress bar
                                except Exception as e:
                                    print(f"Error processing video {vid}: {e}")
                else:
                    with tqdm(total=len(videos), desc=f"Processing {video_type} videos", unit="file") as pbar:
                        for video, _ in videos:
                            try:
                                if operation == 'move':
                                    shutil.move(video, os.path.join(serial_folder, os.path.basename(video)))
                                    print(f"Moved video {video} to {serial_folder}")
                                elif operation == 'copy':
                                    shutil.copy2(video, os.path.join(serial_folder, os.path.basename(video)))
                                    print(f"Copied video {video} to {serial_folder}")
                                pbar.update(1)  # Update progress bar
                            except Exception as e:
                                print(f"Error processing video {video}: {e}")
        
        return metadata_results
    except Exception as e:
        print(f"Error processing videos in folder {input_folder_path}: {e}")
        return None

# Example usage
input_folder_path = r'C:\Users\mek0967\OneDrive - University of Tulsa\TU MASTER\Thesis\Maldistribution\Experiments\Experimental Recordings\Go-Pro\Calibration-Dye experiments'
output_folder_path = r'C:\Users\mek0967\OneDrive - University of Tulsa\TU MASTER\Thesis\Maldistribution\Experiments\Experimental Recordings\Go-Pro\Calibration-Dye experiments'
min_date_time = datetime(2023, 1, 1, 14, 20, 0)  # Replace with your desired start date and time
max_date_time = datetime.now()  # Current time as maximum date
operation = 'move'  # Set to 'move' or 'copy' based on your preference

metadata_results = process_videos_in_folder(input_folder_path, output_folder_path, min_date_time, max_date_time, operation)

if metadata_results:
    for video_file, metadata in metadata_results.items():
        print(f"\nMetadata for {video_file}:")
        for key, value in metadata.items():
            print(f"{key}: {value}")

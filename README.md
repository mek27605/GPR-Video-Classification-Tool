# GPR-Video-Classification-Tool
This code reads the metadata of go-pro videos to classify them in terms of go-pro serial number, video reatin time and name convention

Prerequisites:
*  Python Libraries: tqdm library
*  ExifTool command line must be installed: https://exiftool.org/


<img width="612" alt="image" src="https://github.com/user-attachments/assets/d78d0c10-0f4d-4e91-89ce-e68d76e7ceda">



Code input variable definitions:
* input_folder_path:                  Enter input file path that contains video
* output_folder_path:                 Enter desired folder to move (Same with input if only classification)
* min_date_time & max_date_time:    Enter specific date interval to limit videos
* Operation:                        Move or Copy

Go-Pro Video File Name Convention

<img width="624" alt="image" src="https://github.com/user-attachments/assets/fc846d54-ff25-4f6d-a8af-00eaee58cf95">

![image](https://github.com/user-attachments/assets/9f1e0b36-7892-4eda-8013-79e7bd48caa6)
Further information: https://community.gopro.com/s/article/GoPro-Camera-File-Naming-Convention?language=en_US

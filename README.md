<details>
<summary>Image Reduction Pipeline</summary>

# How to Use the Image Reduction Pipeline

This guide provides instructions on how to set up and use the Image Reduction Pipeline for processing astronomical images. The pipeline is designed to reduce bias, flat, and data frames, perform photometry, and calculate production rates for comets.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Running the Pipeline](#running-the-pipeline)
- [Photometry](#photometry)
- [Calibration](#calibration)
- [Production Rate Calculation](#production-rate-calculation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Prerequisites
Before running the pipeline, ensure you have the following:

- **Google Colab**: The pipeline is designed to run in Google Colab. You will need a Google account to access Colab.
- **Google Drive**: All input files (FITS images, CSV files) should be stored in Google Drive.
- **Python Libraries**: The pipeline requires several Python libraries, which will be installed automatically when you run the code.

---

## Setup

### Upload Files to Google Drive
Upload your FITS files and CSV files to a specific folder in Google Drive. Ensure the folder structure is organized as follows:

``` /MyDrive/Colab Notebooks/Research/Jan20/ ├── list.csv ├── list_photometry.csv ├── bias_images/ ├── flat_images/ ├── data_images/ ```


### Open Google Colab
1. Go to [Google Colab](https://colab.research.google.com/).
2. Create a new notebook or upload the provided notebook (`Image_Reduction_Pipeline_Colab.ipynb`).

### Mount Google Drive: Run the following code in the first cell to mount your Google Drive: 
```python from google.colab import drive drive.mount('/content/drive', force_remount=True) ``` 
### Install Required Packages: Run the following code to install all necessary Python packages: 
```python !pip install git+https://github.com/mkelley/mskpy.git !pip install sbpy !pip install astroscrappy !pip install ccdproc !pip install astropy !pip install photutils !pip install tabulate !pip install pandas !pip install ipywidgets !pip install matplotlib !pip install tk ``` 
## Running the Pipeline 
### Set Directory Path: Specify the directory path where your FITS files are stored: 
```python dir_path = '/content/drive/MyDrive/Colab Notebooks/Research/Jan20' ```
### Run the Image Reduction Pipeline: Execute the code cells in the notebook to process the bias, flat, and data frames. 
The pipeline will: 
- Create a master bias frame.
- Create a master flat frame.
- Apply cosmic ray correction and flat field correction to the data frames.
- Save the processed images in the `final_files` folder.
### Check Output: The processed images will be saved in the `final_files` folder within your specified directory. 
## Photometry 
### Prepare Photometry CSV File:
Ensure you have a CSV file (`list_photometry.csv`) with the following columns:  

| Column   | Description               |
|----------|---------------------------|
| `date`   | Date of observation       |
| `filenum` | File number               |
| `type`   | Type of image (star or comet) |
| `x`      | X-coordinate of the object |
| `y`      | Y-coordinate of the object |

### Run Photometry: Execute the photometry section of the notebook. 
The pipeline will: 
- Perform aperture photometry on stars and comets.
- Allow you to adjust the aperture size interactively.
- Save the photometry results in CSV files (`fluxcal_table.csv` and `comet_table.csv`).
## Calibration 
### Calibrate Star Photometry: The pipeline will use the star photometry data to calibrate the magnitudes and calculate extinction coefficients. 
### Calibrate Comet Photometry: The pipeline will use the calibrated star data to calibrate the comet photometry and calculate the flux for each filter (NH, CN, BC, C2, OH). 
## Production Rate Calculation 
### Calculate Production Rates: The pipeline will calculate the production rates for OH, NH, CN, and C2 using the Haser model. It will also calculate the Afrho parameter for dust and the H2O production rate. 
### Save Results: The production rate results will be saved in a text file (`Production_Rate.txt`). 
## Troubleshooting 
### File Not Found Errors: 
- Ensure the file paths in the notebook match the actual paths in your Google Drive.
- Double-check the names of the CSV files and FITS files.
### Package Installation Issues: 
- If a package fails to install, try installing it manually using: ```python !pip install <package_name> ```
### Aperture Size Adjustment: 
- If the aperture size is not correct, you can adjust it interactively during the photometry step.
## Contributing

Contributions are welcome! If you'd like to improve the **Image Reduction Pipeline**, follow these steps:

### 1. Fork the Repository
Click the **Fork** button at the top right of this repository to create your own copy.

### 2. Clone Your Fork
Clone the repository to your local machine using:

```bash
git clone https://github.com/your-username/Image-Reduction-Pipeline.git
```

### 3. Create a Branch
Create a new branch for your feature or bug fix:

```bash
git checkout -b feature-name
```

### 4. Make Changes
Edit the code or documentation as needed.

### 5. Commit and Push
Commit your changes and push to your fork:

```bash
git add .
git commit -m "Describe your changes"
git push origin feature-name
```

### 6. Submit a Pull Request
Go to the original repository and submit a pull request with a clear description of your changes.

---

**Note**: I am no longer working on this project, so this code can be considered deprecated. Please contact **Dr. Adam McKay** at Appalachian State University for further inquiries. You can reach him via email at [mckayaj@appstate.edu](mailto:mckayaj@appstate.edu).

## License

This project is licensed under the [MIT License](LICENSE).  
You are free to use, modify, and distribute this software, provided that you include the original license and attribution.

Here's a guide on how to use the Photometry GUI:
</details>

---
<details>
<summary>Photometry GUI</summary>


# **Photometry GUI - User Guide**

## **Introduction**
The Photometry GUI is designed to facilitate aperture photometry on FITS images. Users can load image data, define photometric parameters, and process astronomical objects such as stars and comets.

## **Installation Requirements**
Ensure you have the following Python libraries installed:
```bash
pip install numpy astropy photutils pandas tabulate ttkbootstrap matplotlib
```

## **Launching the Application**
Run the script:
```bash
python photometry_gui.py
```

## **User Interface Overview**
The GUI consists of four main tabs:
1. **Parameters** - Set photometric parameters.
2. **Plots** - View plotted results.
3. **Table** - Displays image metadata.
4. **Photometry Output** - View processed photometry results.

## **How to Use**
### **1. Loading Data**
1. Click **"Browse"** to select the folder containing your FITS images and photometry list (`list_photometry.csv`).
2. The application will populate the table with image metadata.

### **2. Setting Parameters**
- **Filename**: Displays the selected file.
- **Radius**: Set the aperture radius for photometry.
- **Position**: Define the target’s (x, y) position in the image.
- **Inner & Outer Radius**: Specify annulus radii for background estimation.

### **3. Modifying Table Data**
- Left-click a row to select it.
- Right-click the table to update the selected row with the current parameter values.

### **4. Automating Settings**
- **Set For All Star Images**: Apply the current parameters to all star images.
- **Set For All Comet Images**: Apply the current parameters to all comet images.

### **5. Running Photometry**
- Click **"Photometry"** to process the selected images.
- Results are displayed in the **Photometry Output** tab.

### **6. Plotting Data**
- Click **"Plot"** to visualize the selected image.

### **7. Exporting Results**
- The processed photometry data is saved as a CSV file.

### **8. Exiting**
- Click **"Quit"** to close the application.
</details>

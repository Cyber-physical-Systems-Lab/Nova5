# README

This part contains two main Python scripts for analyzing experimental trials and facial emotions in video data:

---

## 1. `trials_analysis.py`

### Overview
This script processes experimental data and emotion data to analyze trials based on various criteria such as cube color, correctness, and True/False values.

### Prerequisites
- **Python**: 3.10 or higher
- **Libraries**: `pandas`, `numpy`, `openpyxl`

### Input Files
- `emotion_data.xlsx`
- `P*.xlsx` (experiment data)

### Environment Setup

#### Option 1: Conda
```bash
conda env create -f environment.yml
conda activate trial_env
```

#### Option 2: pip
```bash
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Usages
```bash
python3 trials_analysis.py
```

### Output
- Saves results to `block_analysis.xlsx` with sheets for each block.
- Rows after row 17 in each sheet are bolded in the first column.

### Customization
- Adjust `fps` for video frame rate.
- Modify `block_ranges`:
```python
block_ranges = {
    1: (15, 31),
    2: (34, 50),
    3: (53, 69)
}
```

---

## 2. `face_analysis.py`

### Overview
Processes video files to analyze facial emotions frame-by-frame using the DeepFace library. Results are saved to `emotion_data.xlsx`.

### Prerequisites
- **Python**: 3.10 or higher
- **Libraries**: `opencv-python`, `deepface`, `pandas`

### Input Files
- `Block 1.mp4`
- `Block 2.mp4`
- `Block 3.mp4`

### Environment Setup
Same as above using `environment.yml` or `requirements.txt`.

### Usage
```bash
python3 face_analysis.py
```

### Output
- Results saved to `emotion_data.xlsx`
- Each sheet corresponds to a block

### Customization
- Adjust crop region:
```python
crop_x, crop_y, crop_w, crop_h = 200, 180, 100, 80
```

### Troubleshooting
- Ensure video files are in the same directory as the script.
- Verify DeepFace installation: `pip install deepface`.
- Adjust crop area if no faces are detected.

---

## License
These scripts are provided "as-is" for research and analysis purposes.
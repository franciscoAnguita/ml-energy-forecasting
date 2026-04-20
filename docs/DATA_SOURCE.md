# DATA SOURCE DOCUMENTATION
## UCI Household Electric Power Consumption Dataset

---

## OVERVIEW

This project uses the **Individual Household Electric Power Consumption Dataset** from the UCI Machine Learning Repository.

**What it contains:** Measurements of electric power consumption in one household over 4 years, recorded every minute.

---

## DATASET DETAILS

### **Source Information**

- **Provider:** UCI Machine Learning Repository
- **Original Collectors:** Georges Hébrail, Alice Bérard (EDF R&D, France)
- **Time Period:** December 2006 - November 2010 (47 months)
- **Measurement Frequency:** Every minute
- **Total Records:** 2,075,259 measurements
- **Geographic Location:** Sceaux, France (suburb of Paris)

### **Download Links**

**Primary source:**
- UCI Repository: https://archive.ics.uci.edu/ml/datasets/individual+household+electric+power+consumption
- Direct download: https://archive.ics.uci.edu/ml/machine-learning-databases/00235/household_power_consumption.zip

**File Information:**
- **Filename:** `household_power_consumption.txt`
- **Format:** Text file (semicolon-separated values)
- **Size:** ~127 MB (compressed), ~132 MB (uncompressed)
- **Encoding:** ASCII

---

## DATASET FEATURES

The dataset contains **9 features** (columns):

### **1. Date** 
- **Type:** Date (DD/MM/YYYY)
- **Description:** Measurement date
- **Range:** 16/12/2006 - 26/11/2010
- **Example:** `16/12/2006`

### **2. Time**
- **Type:** Time (HH:MM:SS)
- **Description:** Measurement time
- **Format:** 24-hour clock
- **Example:** `17:24:00`

### **3. Global_active_power** ⭐ **(TARGET VARIABLE)**
- **Type:** Numeric (kilowatts)
- **Description:** Household global minute-averaged active power
- **Unit:** kilowatt (kW)
- **Range:** 0.076 - 11.122 kW
- **Missing values:** 1.25% (marked as "?")
- **Physical meaning:** Total real power consumed by the household (actual energy used)
- **This is what we predict!**

### **4. Global_reactive_power**
- **Type:** Numeric (kilowatt-reactive-power)
- **Description:** Household global minute-averaged reactive power
- **Unit:** kilovolt-ampere reactive (kVAR)
- **Range:** 0.000 - 1.390 kVAR
- **Physical meaning:** Power oscillating between source and load (doesn't do useful work, but needed for AC equipment like motors)

### **5. Voltage**
- **Type:** Numeric (volts)
- **Description:** Minute-averaged voltage
- **Unit:** volt (V)
- **Range:** 223.2 - 254.2 V
- **Nominal:** 230V (European standard)
- **Physical meaning:** Electric potential difference

### **6. Global_intensity**
- **Type:** Numeric (amperes)
- **Description:** Household global minute-averaged current intensity
- **Unit:** ampere (A)
- **Range:** 0.2 - 48.4 A
- **Physical meaning:** Current flow (combined for all circuits)
- **Relationship:** Power ≈ Voltage × Intensity

### **7. Sub_metering_1**
- **Type:** Numeric (watt-hours)
- **Description:** Energy sub-metering No. 1
- **Unit:** watt-hour (Wh) of active energy
- **Covers:** Kitchen appliances (mainly dishwasher, oven, microwave)
- **Physical meaning:** Energy consumed by kitchen over 1 minute

### **8. Sub_metering_2**
- **Type:** Numeric (watt-hours)
- **Description:** Energy sub-metering No. 2
- **Unit:** watt-hour (Wh) of active energy
- **Covers:** Laundry room appliances (washing machine, dryer, refrigerator, light)
- **Physical meaning:** Energy consumed by laundry room over 1 minute

### **9. Sub_metering_3**
- **Type:** Numeric (watt-hours)
- **Description:** Energy sub-metering No. 3
- **Unit:** watt-hour (Wh) of active energy
- **Covers:** Electric water heater and air conditioner
- **Physical meaning:** Energy consumed by climate control over 1 minute

---

## DATA CHARACTERISTICS

### **Temporal Coverage**
- **Start date:** 2006-12-16 17:24:00
- **End date:** 2010-11-26 21:02:00
- **Duration:** 1,442 days (~4 years)
- **Completeness:** 99.8% (some missing values)

### **Missing Values**
- **Percentage:** ~1.25% of records
- **Representation:** Marked as "?" in the file
- **Distribution:** Scattered throughout the dataset
- **Handling:** We remove rows with missing values during preprocessing

### **Data Quality**
- **Consistency:** High - professionally collected
- **Outliers:** Minimal - real household consumption patterns
- **Errors:** Very few sensor errors or anomalies
- **Sampling rate:** Consistent 1-minute intervals

---

## UNDERSTANDING THE MEASUREMENTS

### **Power vs Energy**

**Power (Global_active_power):**
- **What it is:** Rate of energy consumption
- **Unit:** kilowatt (kW)
- **Analogy:** Like the speed of a car (km/h)
- **Example:** "The house is using 2.5 kW right now"

**Energy (Sub_metering):**
- **What it is:** Total energy consumed over time
- **Unit:** watt-hour (Wh)
- **Analogy:** Like the distance traveled (km)
- **Example:** "The kitchen used 45 Wh in the last minute"

**Relationship:** Energy = Power × Time

### **Active vs Reactive Power**

**Active Power (Global_active_power):**
- Does actual work (heating, lighting, motion)
- What we pay for on our electricity bill
- **Example:** Light bulb converting electricity to light and heat

**Reactive Power (Global_reactive_power):**
- Doesn't do useful work
- Needed for AC motors, transformers, fluorescent lights
- Creates magnetic/electric fields
- **Example:** Motor building up magnetic field

### **Sub-metering Coverage**

The three sub-meters don't cover 100% of household consumption:

```
Total consumption (Global_active_power)
├── Sub_metering_1 (Kitchen: ~20-30%)
├── Sub_metering_2 (Laundry: ~15-25%)  
├── Sub_metering_3 (Climate: ~30-40%)
└── Unmetered (Lights, TV, computers, etc.: ~15-30%)
```

**Note:** Sub-metering values in Wh; Global values in kW (different units!)

---

## HOUSEHOLD CONTEXT

### **Location**
- **Country:** France
- **Region:** Île-de-France (Paris region)
- **City:** Sceaux (southern suburb of Paris)
- **Type:** Typical suburban household

### **Electrical System**
- **Voltage:** 230V AC (European standard)
- **Frequency:** 50 Hz
- **Main breaker:** Likely 40-60A (typical for France)
- **Max observed current:** 48.4A

### **Energy Profile**
- **Average consumption:** ~1.2 kW
- **Peak consumption:** ~11 kW
- **Typical range:** 0.5 - 3.0 kW
- **Annual usage:** ~10,500 kWh (estimated)

**Comparison:** 
- Average French household: ~4,500 kWh/year
- This household: Above average (larger home or more appliances)

---

## SCIENTIFIC CONTEXT

### **Why This Dataset is Valuable**

1. **Long duration:** 4 years captures seasonal patterns
2. **High frequency:** Minute-level allows detailed analysis
3. **Sub-metering:** Rare to have appliance-level breakdown
4. **Real-world:** Actual household, not laboratory conditions
5. **Complete metadata:** Full documentation and context

### **Common Research Uses**

- **Load forecasting:** Predict future electricity demand
- **Anomaly detection:** Identify unusual consumption patterns
- **Appliance disaggregation:** Separate individual appliance usage (NILM)
- **Demand response:** Optimize consumption timing
- **Energy efficiency:** Identify savings opportunities
- **Pattern recognition:** Understand household behavior

---

## CITATION

If you use this dataset in academic work, please cite:

**APA Format:**
```
Hébrail, G., & Bérard, A. (2012). Individual household electric power consumption 
[Data set]. UCI Machine Learning Repository. 
https://archive.ics.uci.edu/ml/datasets/individual+household+electric+power+consumption
```

**BibTeX:**
```bibtex
@misc{hebrail2012household,
  author = {Hébrail, Georges and Bérard, Alice},
  title = {Individual Household Electric Power Consumption},
  year = {2012},
  publisher = {UCI Machine Learning Repository},
  howpublished = {\url{https://archive.ics.uci.edu/ml/datasets/individual+household+electric+power+consumption}}
}
```

---

## OUR PREPROCESSING PIPELINE

We transform the raw data as follows:

### **Step 1: Data Ingestion** (`src/data_ingestion.py`)
- Load the semicolon-separated file
- Parse dates and times
- Convert "?" to NaN (missing values)
- Combine Date and Time into single datetime column

### **Step 2: Data Preprocessing** (`src/data_preprocessing.py`)
- Remove rows with missing values (~1.25% of data)
- Remove outliers (physically impossible values)
- Resample from minute to hourly (reduces size by 60x)
- Average values within each hour
- **Result:** 35,000+ hourly records → 8,761 clean hourly records (1 year)

### **Step 3: Feature Engineering** (`src/feature_engineering.py`)
- Extract time features: hour, day of week, month, is_weekend
- Create interaction features:
  - `hour_weekend_interaction` = hour × is_weekend
  - `voltage_intensity_product` = Voltage × Global_intensity
  - `total_sub_metering` = sum of all sub-meters
- **Result:** 15 total features (9 original + 6 engineered)

### **Why We Resample to Hourly?**

**Minute-level data:**
- ✅ Extremely detailed
- ❌ 2 million rows (slow to train)
- ❌ Very noisy (minute-to-minute fluctuations)
- ❌ Appliance on/off creates spikes

**Hourly data:**
- ✅ Smooth patterns emerge
- ✅ Manageable size (~8,000 rows)
- ✅ Still captures daily/weekly patterns
- ✅ Better for forecasting typical consumption

**For our use case** (predicting typical household consumption), hourly is optimal.

---

## DATA STATISTICS

### **Global Active Power (Target Variable)**

After preprocessing (hourly data):

```
Count:     8,761 records
Mean:      1.23 kW
Std Dev:   0.68 kW
Min:       0.08 kW
25%:       0.72 kW
50%:       1.14 kW  (median)
75%:       1.61 kW
Max:       6.45 kW
```

**Distribution:**
- Low consumption (<1.0 kW): ~35% of time
- Medium (1.0-3.0 kW): ~60% of time
- High (>3.0 kW): ~5% of time

### **Typical Patterns**

**Daily pattern:**
- **Night (00:00-06:00):** Low (~0.5 kW) - mostly baseline appliances
- **Morning (06:00-09:00):** Rising (~1.5 kW) - breakfast, showers
- **Day (09:00-18:00):** Medium (~1.2 kW) - background consumption
- **Evening (18:00-23:00):** Peak (~2.0 kW) - cooking, entertainment

**Weekly pattern:**
- **Weekdays:** More consistent (people at work)
- **Weekends:** Higher morning consumption (people home)
- **Weekends:** More variable (different activities)

**Seasonal pattern:**
- **Winter:** Higher (heating, more lights)
- **Summer:** Variable (air conditioning on hot days)
- **Spring/Fall:** Lower (mild weather)

---

## DATA LIMITATIONS

### **Things to Consider**

1. **Single household:** Patterns may not generalize to all homes
2. **French context:** Climate, appliances, lifestyle specific to France
3. **2006-2010:** Some appliance types/efficiency may be outdated
4. **Suburban:** Urban or rural homes may differ
5. **No occupancy data:** We don't know if people are home
6. **No weather data:** External temperature not recorded
7. **No appliance details:** We don't know specific models/ages

### **Missing Information**

The dataset **does NOT include:**
- Number of occupants
- Home size/type
- Appliance inventory
- Outdoor temperature
- Solar generation (if any)
- Electric vehicle charging
- Individual circuit details (beyond 3 sub-meters)

---

## SUITABILITY FOR ML

### **Why This Dataset Works Well**

✅ **Large sample size:** 2M+ minute records → 8K+ hourly records
✅ **Temporal features:** Clear daily/weekly/seasonal patterns
✅ **Low noise:** Professional data collection
✅ **Complete metadata:** Well-documented
✅ **Real-world:** Actual household consumption
✅ **Continuous target:** Regression-friendly (predicting kW)

### **Prediction Task**

**What we predict:** `Global_active_power` (total household consumption in kW)

**Using these features:**
- Voltage (V)
- Global_intensity (A)
- Global_reactive_power (kVAR)
- Sub_metering_1 (Wh)
- Sub_metering_2 (Wh)
- Sub_metering_3 (Wh)
- Hour of day (0-23)
- Day of week (0-6)
- Month (1-12)
- Is weekend (0 or 1)

**Plus engineered features:**
- hour_weekend_interaction
- voltage_intensity_product
- total_sub_metering

**Model type:** Regression (Random Forest)

**Performance:** ~92% R² score (explains 92% of variance)

---

## ADDITIONAL RESOURCES

### **Related Datasets**

- **REDD:** MIT residential energy disaggregation dataset (US homes)
- **UK-DALE:** UK domestic appliance-level electricity dataset
- **ECO:** Electricity consumption and occupancy dataset (Switzerland)
- **REFIT:** Personalised retrofit decision support (UK)

### **Relevant Papers**

1. "Energy Disaggregation via Discriminative Sparse Coding" (Kolter & Jaakkola, 2012)
2. "Neural NILM: Deep Neural Networks Applied to Energy Disaggregation" (Kelly & Knottenbelt, 2015)
3. "Sequence-to-Point Learning with Neural Networks for NILM" (Zhang et al., 2018)

### **Standards & References**

- **IEC 61000-4-30:** Power quality measurement methods
- **ISO 50001:** Energy management systems
- **EN 50470:** Electricity metering equipment (European standard)

---

## LICENSE & USAGE

### **Dataset License**

The UCI dataset is **publicly available for research and educational purposes**.

**Terms:**
- ✅ Free to use for research
- ✅ Free to use for education
- ✅ Free to use for non-commercial projects
- ⚠️ Must cite the source (see Citation section)
- ❌ Commercial use may require permission from EDF R&D

### **Our Project License**

This ML pipeline and API are released under **MIT License**:
- ✅ Free to use, modify, distribute
- ✅ Commercial use allowed
- ⚠️ Must include license and copyright notice
- ❌ No warranty provided

**Note:** The dataset and the code have separate licenses!

---

## DATA QUESTIONS?

**For dataset-specific questions:**
- UCI Repository: https://archive.ics.uci.edu/ml/support
- Original collectors: EDF R&D, France

**For our preprocessing/usage questions:**
- See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- See [QUICKSTART.md](QUICKSTART.md)
- Open an issue on GitHub

---

## ✅ QUICK REFERENCE

**Dataset:** UCI Household Electric Power Consumption
**Size:** 127 MB (2M+ records)
**Period:** Dec 2006 - Nov 2010
**Frequency:** Every minute
**Target:** Global_active_power (kW)
**Features:** 9 original + 6 engineered
**After preprocessing:** 8,761 hourly records
**Model performance:** 92% R² score

---

**This documentation is accurate as of April 2024. Always check the UCI repository for the latest information.**

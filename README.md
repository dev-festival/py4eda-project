# Automotive Manufacturing Preventive Maintenance Analysis

## INSY6500 - Exploratory Data Analysis Project

**Team Members:** Abby Tucker & Mike Moyer

**Institution:** Auburn University

**Course:** INSY6500 - Python for Analytics  

**Semester:** Fall 2025

---

## Project Overview
This project performs exploratory data analysis on one year of preventive maintenance (PM) forecast data from an automotive manufacturing facility. The dataset consists of 2 files, containing forecasted (scheduled) maintenance activities across multiple production for the coming fiscal year (103ki) as well as historical results from the previous fiscal year (101ki). 

### Why These Datasets?

I selected these datasets because it represents the complexity of real-world preventive maintenance questions that I struggle with on a regular basis. This project offers me the opportunities to explore this data with industry standard data exploration techniques which are (to my knowledge) almost non-existent in our maintenance culture. 

---
## Dataset Descriptions
### Source and Attribution
**Source:** Internal preventive maintenance forecasting system - IBM's Maximo DB2 Database + SQL Query.

**Time Periods:** 
* 12-month forecast (April 2026 - March 2027)
* 12-month historical performance (April 2024 - March 2025)

**Data Collection:** Extracted from Maximo Enterprise Asset Management system. 

**Files:** 
* `103ki_pm_forecast.csv`
* `101ki_pm_performance.csv`

### Dataset Characteristics
**Observations:** 92,000+ scheduled PM activities
- **Features:** 20 columns covering maintenance scheduling, labor requirements, and asset information
- **Scope:** Multiple production departments (Paint, Engine Assembly, Bumper Paint)
- **Complexity:** Mix of location-based and asset-based maintenance with varying intervals


### Key Features

#### PM FORECAST

| Feature | Description | Type |
|---------|-------------|------|
| `DUE_DATE` | Scheduled completion date for PM activity | Date |
| `PMNUM` | `foreign key` Unique preventive maintenance identifier | String |
| `COUNTKEY` | PMNUM concatenated to date for distinct count of occurence | String |
| `PMDESCRIPTION` | Description of the maintenance task | String |
| `INTERVAL` | Frequency of maintenance (e.g., 1-MONTHS, 6-MONTHS) | String |
| `FORECASTJP` | Job plan forecast identifier | String |
| `JOB_TYPE` | Type of work (REPAIR, INSPECTION, ADJUSTMENT) | Categorical |
| `LABOR_CRAFT` | Required labor skill/craft | Categorical |
| `PLANNED_LABOR_HRS` | Estimated labor hours | Float |
| `TOTAL_MATERIAL_COST` | Estimated material cost | Float |
| `TASK_COUNT` | Number of tasks in the job plan (meta complexity) | Integer |
| `TOTAL_TASK_DESC_LENGTH` | Number of characters across all task descriptions | Integer |
| `PMSCOPETYPE` | Scope type (LOCATION, ASSET) | Categorical |
| `LOCATION` | Equipment or location identifier | String |
| `LOCATIONDESC` | Human-readable location description | String |
| `PLANT` | Plant identifier | String |
| `DEPT` | Department code | String |
| `DEPT_NAME` | Department name | String |
| `DEPT_TYPE` | Department type abbreviation | String |
| `LINE` | Production line identifier | String |
| `ZONENAME` | Manufacturing zone name | String |
| `PROCESSNAME` | Process area name | String |

#### PM PERFORMANCE (Previous full fiscal year 2024-2025)

| Feature | Description | Type |
|---------|-------------|------|
| `PMNUM` | `primary key` Unique preventive maintenance identifier | String |
| `TIMES_SCHEDULED` | Number of times this PM came out | Integer |
| `TIMES_ONTIME` | Number of times the work was done on time | Integer |
| `TIMES_LATE` | Number of times the work was late | Integer |
| `TIMES_NOT_COMPLETED` | Number of times the work was not done at all | Integer |
| `AVG_PLANNED_HOURS` | Average of planned labor hours for the year | Float |
| `AVG_ACTUAL_HOURS` | Average of actual labor hours for the year | Float |

---
## Project Plan
Two team members, two complete analytical paths. Each person does the full EDA workflow independently. Convergence only if insights naturally connect.

### Path 1 - Maintenancy Strategy Comparison
**Owner**: Mike Moyer

**Question**: *How do different departments approach preventative maintenance? Does it reveal anything about their operational philosophy?*

#### Path 1: Direction Skeleton: 

| Phase | Focus | Key Activities | Outputs |
|-------|-------|----------------|---------|
| **I: Foundation** | Data prep & feature engineering | • Parse `INTERVAL` into frequency groups<br>• Calculate Job Complexity<br>• Create job type mix ratios<br>• Build asset/location preference metrics | Engineered features ready for analysis |
| **II: Exploration** | Answer 3 research questions | **Q1:** Department "maintenance personalities"<br>• Job type distributions<br>• Interval strategies<br>• Craft utilization patterns<br><br>**Q2:** Asset treatment across departments<br>• Compare intervals for similar equipment<br>• Identify departmental culture differences<br><br>**Q3:** Craft specialization patterns<br>• Department-specific vs shared crafts<br>• Workload concentration analysis | • Department comparison tables<br>• Craft heatmaps<br>• Strategy visualizations<br>• Standalone insights |
| **III: Optional** | Performance context | Merge with performance data to see if strategies correlate with success | Strategy-performance connections |

### Path 2 - Strategy Execution Analysis
**Owner**: Abby Tucker

**Question**: *Are there any that patterns emerge when we compare the planned maintenance activities to historical execution results?*

#### Path 2: Direction Skeleton: 

| Phase | Focus | Key Activities | Outputs |
|-------|-------|----------------|---------|
| **I: Foundation** | Join datasets & feature engineering | • Merge forecast + performance on `PMNUM`<br>• Calculate reliability metrics (on-time rate, completion rate)<br>• Build planning accuracy metrics (deviation %)<br>• Create complexity indicators (task density, complexity score) | Merged dataset with performance metrics |
| **II: Exploration** | Answer 3 research questions | **Q1:** How well do plans match reality?<br>• Planned vs actual hour distributions<br>• Planning bias patterns<br>• Accuracy by interval/job type/craft<br><br>**Q2:** Where are our planning blind spots<br>• Compare high vs low completion characteristics<br>• Cross-tabulate by job type, craft, dept<br><br>**Q3:** When and why do PMs fail?<br>• Examine high incompletion PMNUMs<br>• Compare completed vs incomplete characteristics<br>• Department completion discipline | • Planning accuracy visualizations<br>• Problem PM identification<br>• Standalone insights |
| **III: Optional** | Temporal patterns | Map forecast dates to find scheduling hot spots or seasonal patterns | Workload timing insights |


###  Key Feature Engineering by Path

| Path | Key Features Created |
|------|---------------------|
| **Path 1** | • Interval frequency groups (Daily/Weekly/Monthly/etc.)<br>• Craft diversity index per department<br>• Job type mix ratios (REPAIR/INSPECTION/ADJUSTMENT %)<br>• Asset vs Location preference ratio<br>• Workload metrics (total hours, PM count, avg per PM) |
| **Path 2** | • `on_time_rate = TIMES_ONTIME / TIMES_SCHEDULED`<br>• `completion_rate = (SCHEDULED - NOT_COMPLETED) / SCHEDULED`<br>• `hour_deviation_pct = (ACTUAL - PLANNED) / PLANNED`<br>• Task density, complexity scores<br>• Performance tier segmentation (high/medium/low) |

#### Research Questions Quick Reference

| Path | Question | Analysis Type | Complexity |
|------|----------|---------------|------------|
| **Path 1** | What are department "maintenance personalities"? | Univariate + bivariate distributions | Medium |
| **Path 1** | Do similar assets get treated differently? | Cross-departmental comparison | Medium |
| **Path 1** | Is there craft specialization? | Multivariate grouping & heatmaps | Medium-High |
| **Path 2** | How well do plans match reality? | Bivariate relationship + segmentation | Medium |
| **Path 2** | What do high completion PMs have in common? | Comparative group analysis | Medium-High |
| **Path 2** | When and why do PMs fail to meet the plan? | Pattern discovery + cross-tabulation | Medium-High |

---

## Streamlit Ideas: 
*(pick 1 - 3, *time depending*)*

**1. Department Comparison**
>*  Dropdown to select department(s)
>* Shows: job type mix (pie/bar), craft utilization (bar), total PM count, total labor hours
>* Lets users compare 2-3 departments side-by-side
>* Why: Answers "how does my department stack up?" instantly

**2. Planning Accuracy Explorer**
>* Scatter plot: planned vs actual hours with diagonal reference line
>* Filter by: department, interval, job type, craft
>* Hovering shows PMNUM and deviation %
>* Why: Interactive way to find which PM types are hardest to estimate accurately

**3. Workload Calendar Heatmap**
>* Calendar view of the forecast year showing PM density by month (or week)
>* Color intensity = total labor hours scheduled
>* Filter by: department, craft
>* Why: Visualizes where scheduling bottlenecks might occur

**4. Completion Rate Analysis**
>* Bar charts showing completion rates by: interval, job type, department, craft
>* Toggle between on-time rate, completion rate, late rate
>* Filter to specific ranges or categories
>* Why: Quickly identify which categories struggle with execution

**5. PM Deep Dive Search**
>* Search box: enter PMNUM
>* Shows: all forecast occurrences, performance history, characteristics
>* Displays: planned vs actual comparison, completion history, interval, craft, department
>* Why: Lets users investigate specific problematic PMs they know about

---
 
## Project Structure

```
py4eda-project/
│
├── README.md                                     # This file
├── data/
│   └── 103ki_pm_forecast.csv                     
│   └── 101ki_pm_performance.csv                  
│
├── notebooks/
│   ├── 00_data-info_and_loader-template.ipynb    #Target Readiness 11/27 12 PM - Mike
│   ├── 02_individual_exploration_abby.ipynb      #Target Completion - 
│   ├── 03_individual_exploration_mike.ipynb      #Target Completion - 
│   ├── 04_combined_report.ipynb                  #Optional
│
├── src/
│   └── pm_forecast_dashboard.py                           #Target Completion - 
│
├── outputs/
│   ├── cleaned_data.csv                          #Likely to have multiple of these
│   └── intermediate_data.pkl
│   
└── requirements.txt
```

---

## Methodology
This project follows the iterative EDA workflow outlined in INSY6500:

### 1. Load & Initial Reconnaissance

- Import data and examine structure
- Understand feature meanings and relationships
- Initial data profiling and summary statistics 
- Identify data types and potential issues --> `dt.info()`

### 2. Data Quality Assessment
- Missing value analysis --> `.isna().sum()`
- Duplicate detection --> _forecast will have dups, performance should not_
- Outlier identification 
- Data type validation
- Consistency checks across related fields

### 3. Cleaning Decisions
- Handle missing values (drop, impute, or flag) --> _most numeric values safe to replace with 0_
- Correct data type mismatches
- Address outliers and anomalies
- Standardize categorical values
- Document all cleaning decisions and rationale

### 4. Statistical EDA
- Univariate analysis (distributions, summary stats)
- Bivariate analysis (correlations, relationships)
- Multivariate analysis (group comparisons)
- Time series patterns
- Departmental and craft-level breakdowns

### 5. Transformation & Feature Engineering
- Create time-based features (month, quarter, day of week)
- Engineer maintenance density metrics
- Calculate workload concentration indices
- Develop interval category groupings
- Create craft utilization metrics

### 6. Documentation& Insights
- Document findings and patterns
- Create visualizations for key insights
- Summarize recommendations for operational improvements
- Save cleaned datasets for further analysis

---

## Tools & Technologies

- **Python 3.11+**

- **Core Libraries:**

 - `pandas` - Data manipulation and analysis
 - `numpy` - Numerical computing
 - `matplotlib` - Static visualization
 - `seaborn` - Statistical visualization
 - `plotly` - Interactive visualization
- **Dashboard:**
  - `streamlit` - Interactive web application
- **Development:**
  - `jupyter` - Notebook environment
  - `git` - Version control

---

## Installation \& Setup
### Prerequisites
```bash
# Python 3.11 or higher
python --version

# Conda (Anaconda or Miniconda)
conda --version
```

### Clone Repository

```bash
git clone https://github.com/dev-festival/py4eda-project.git
cd py4eda-project
```
### Install Dependencies
#### Option 1: Using Conda (Recommended)

```bash
# Create environment from file
conda env create -f environment.yml
 
# Activate the environment
conda activate insy6500
 ```
#### Option 2: Using pip
```bash
pip install -r requirements.txt
```


### Run Jupyter Notebooks

```bash
 jupyter-lab
# Navigate to notebooks/ directory
```

### Launch Streamlit Dashboard (Graduate Students)

 ```bash
streamlit run src/pm_dashboard.py
```
---


## Limitations \& Considerations
- **Forecast Data:** This is planned maintenance, not actual execution data. Actual work may vary due to production requirements, equipment breakdowns, or resource availability.
- **Timeframe:** One-year forecast provides a snapshot but may not capture multi-year maintenance strategy cycles or long-interval PMs.
- **Cost Data:** Material cost field is largely unpopulated, limiting cost analysis capabilities.
- **Generalizability:** Findings are specific to this manufacturing facility and may not directly apply to other automotive plants or industries.

---

## References
- Maximo Enterprise Asset Management documentation
- Honda Manufacturing maintenance standards
- INSY6500 course materials (Auburn University)
- Industry best practices for preventive maintenance scheduling

---

## Acknowledgments
- INSY6500 instructional team for project guidance
- Honda Manufacturing of Alabama MESD team for domain expertise
- Maximo system administrators for data access support

---

## License
This project is for educational purposes as part of INSY6500 coursework. The dataset contains proprietary manufacturing information and should not be redistributed without permission.

---

## Contact

**Abby Tucker**, **Mike Moyer**

Students, INSY6500 - Python for Analytics  

Auburn University

For questions about the analysis or methodology, please refer to project documentation in the notebooks.

---
*Created: November 2025*




# \# Automotive Manufacturing Preventive Maintenance Analysis

# \## INSY6500 - Exploratory Data Analysis Project

# 

# \*\*Authors:\*\* Abby Tucker \& Mike Moyer

# \*\*Institution:\*\* Auburn University

# \*\*Course:\*\* INSY6500 - Python for Analytics  

# \*\*Semester:\*\* Fall 2025

# 

# ---

# 

# \## Project Overview

# 

# This project performs exploratory data analysis on one year of preventive maintenance (PM) forecast data from an automotive manufacturing facility. The dataset contains scheduled maintenance activities across multiple production areas, providing insights into maintenance planning, resource allocation, and operational patterns in a real-world manufacturing environment.

# 

# \### Why This Dataset?

# 

# As a maintenance professional working at Honda Manufacturing of Alabama, I selected this dataset because it represents the complexity of real-world maintenance operations that I encounter daily. The data offers opportunities to explore maintenance scheduling patterns, labor allocation, departmental workload distribution, and the relationships between equipment types and maintenance strategies—all critical factors in maintenance workload planning and efficiency.

# 

# ---

# 

# \## Dataset Description

# 

# \### Source and Attribution

# 

# \- \*\*Source:\*\* Internal preventive maintenance forecasting system

# \- \*\*Organization:\*\* Honda Manufacturing of Alabama - Auto Plant

# \- \*\*Time Period:\*\* 12-month forecast (April 2026 - March 2027)

# \- \*\*Data Collection:\*\* Extracted from Maximo Enterprise Asset Management system

# \- \*\*File:\*\* `103ki\_aap\_pm\_forecast\_limit10020251118.csv`

# 

# \### Dataset Characteristics

# 

# \- \*\*Observations:\*\* 5,000+ scheduled PM activities

# \- \*\*Features:\*\* 20 columns covering maintenance scheduling, labor requirements, and asset information

# \- \*\*Scope:\*\* Multiple production departments (Paint, Engine Assembly, Bumper Paint)

# \- \*\*Complexity:\*\* Mix of location-based and asset-based maintenance with varying intervals

# 

# \### Key Features

# 

# | Feature | Description | Type |

# |---------|-------------|------|

# | `DUE\_DATE` | Scheduled completion date for PM activity | Date |

# | `PMNUM` | Unique preventive maintenance identifier | String |

# | `PMDESCRIPTION` | Description of the maintenance task | String |

# | `INTERVAL` | Frequency of maintenance (e.g., 1-MONTHS, 6-MONTHS) | String |

# | `FORECASTJP` | Job plan forecast identifier | String |

# | `JOB\_TYPE` | Type of work (REPAIR, INSPECTION, ADJUSTMENT) | Categorical |

# | `LABOR\_CRAFT` | Required labor skill/craft | Categorical |

# | `LABORHRS` | Estimated labor hours | Float |

# | `THISMATCOST` | Estimated material cost | Float |

# | `PMSCOPETYPE` | Scope type (LOCATION, ASSET) | Categorical |

# | `LOCATION` | Equipment or location identifier | String |

# | `LOCATIONDESC` | Human-readable location description | String |

# | `PLANT` | Plant identifier | String |

# | `DEPT` | Department code | String |

# | `DEPT\_NAME` | Department name | String |

# | `DEPT\_TYPE` | Department type abbreviation | String |

# | `LINE` | Production line identifier | String |

# | `ZONENAME` | Manufacturing zone name | String |

# | `PROCESSNAME` | Process area name | String |

# 

# ---

# 

# \## Research Questions

# 

# This analysis is driven by practical questions that impact maintenance operations and resource planning:

# 

# \### \*\*\[DRAFT]\*\* Primary Questions \*\*\[DRAFT]\*\* 

# 

# 1\. \*\*Workload Distribution:\*\* How is preventive maintenance workload distributed across departments and time periods? Are there opportunities for better load balancing?

# 

# 2\. \*\*Resource Planning:\*\* What are the labor hour requirements by craft and department? Can we identify peak demand periods that require additional staffing?

# 

# 3\. \*\*Maintenance Strategy:\*\* What is the distribution of maintenance intervals across different equipment types? Are there patterns that suggest opportunities for interval optimization?

# 

# 4\. \*\*Job Type Analysis:\*\* How do different job types (REPAIR, INSPECTION, ADJUSTMENT) distribute across departments and equipment? What does this reveal about maintenance strategies?

# 

# \### \*\*\[DRAFT]\*\* Secondary Questions \*\*\[DRAFT]\*\* 

# 

# 5\. \*\*Seasonality:\*\* Are there seasonal patterns in maintenance scheduling? Do certain months show higher activity due to production schedules or planned shutdowns?

# 

# 6\. \*\*Location vs. Asset Maintenance:\*\* What proportion of PMs are location-based vs. asset-based? How does this differ by department?

# 

# 7\. \*\*Labor Efficiency:\*\* What is the relationship between PM frequency and labor hours? Are there opportunities to consolidate similar tasks?

# 

# 8\. \*\*Coverage Gaps:\*\* Are there periods with unusually low or high maintenance activity that could indicate scheduling issues?

# 

# ---

# 

# \## Project Structure

# 

# ```

# py4eda/

# │

# ├── README.md                          # This file

# ├── data/

# │   └── 103ki\_aap\_pm\_forecast\_limit10020251118.csv

# │

# ├── notebooks/

# │   ├── 01\_data\_loading\_reconnaissance.ipynb

# │   ├── 02\_data\_quality\_assessment.ipynb

# │   ├── 03\_cleaning\_and\_transformation.ipynb

# │   ├── 04\_statistical\_eda.ipynb

# │   └── 05\_feature\_engineering\_insights.ipynb

# │

# ├── src/

# │   └── pm\_dashboard.py                # Streamlit interactive dashboard

# │

# ├── outputs/

# │   ├── cleaned\_data.csv

# │   └── analysis\_summary.md

# │

# └── requirements.txt

# ```

# 

# ---

# 

# \## Methodology

# 

# This project follows the iterative EDA workflow outlined in INSY6500:

# 

# \### 1. Load \& Initial Reconnaissance

# \- Import data and examine structure

# \- Understand feature meanings and relationships

# \- Initial data profiling and summary statistics

# \- Identify data types and potential issues

# 

# \### 2. Data Quality Assessment

# \- Missing value analysis

# \- Duplicate detection

# \- Outlier identification

# \- Data type validation

# \- Consistency checks across related fields

# 

# \### 3. Cleaning Decisions

# \- Handle missing values (drop, impute, or flag)

# \- Correct data type mismatches

# \- Address outliers and anomalies

# \- Standardize categorical values

# \- Document all cleaning decisions and rationale

# 

# \### 4. Statistical EDA

# \- Univariate analysis (distributions, summary stats)

# \- Bivariate analysis (correlations, relationships)

# \- Multivariate analysis (group comparisons)

# \- Time series patterns

# \- Departmental and craft-level breakdowns

# 

# \### 5. Transformation \& Feature Engineering

# \- Create time-based features (month, quarter, day of week)

# \- Engineer maintenance density metrics

# \- Calculate workload concentration indices

# \- Develop interval category groupings

# \- Create craft utilization metrics

# 

# \### 6. Documentation \& Insights

# \- Document findings and patterns

# \- Create visualizations for key insights

# \- Summarize recommendations for operational improvements

# \- Save cleaned datasets for further analysis

# 

# ---

# 

# \## Tools \& Technologies

# 

# \- \*\*Python 3.11+\*\*

# \- \*\*Core Libraries:\*\*

# &nbsp; - `pandas` - Data manipulation and analysis

# &nbsp; - `numpy` - Numerical computing

# &nbsp; - `matplotlib` - Static visualization

# &nbsp; - `seaborn` - Statistical visualization

# &nbsp; - `plotly` - Interactive visualization

# \- \*\*Dashboard:\*\*

# &nbsp; - `streamlit` - Interactive web application

# \- \*\*Development:\*\*

# &nbsp; - `jupyter` - Notebook environment

# &nbsp; - `git` - Version control

# 

# ---

# 

# \## Installation \& Setup

# 

# \### Prerequisites

# ```bash

# \# Python 3.11 or higher

# python --version

# 

# \# Conda (Anaconda or Miniconda)

# conda --version

# ```

# 

# \### Clone Repository

# ```bash

# git clone https://github.com/dev-festival/py4eda-project.git

# cd py4eda-project

# ```

# 

# \### Install Dependencies

# 

# \#### Option 1: Using Conda (Recommended)

# ```bash

# \# Create environment from file

# conda env create -f environment.yml

# 

# \# Activate the environment

# conda activate py4eda

# ```

# 

# \#### Option 2: Using pip

# ```bash

# pip install -r requirements.txt

# ```

# 

# \### Run Jupyter Notebooks

# ```bash

# jupyter notebook

# \# Navigate to notebooks/ directory

# ```

# 

# \### Launch Streamlit Dashboard (Graduate Students)

# ```bash

# streamlit run src/pm\_dashboard.py

# ```

# 

# ---

# 

# \## Key Findings (To Be Updated)

# 

# \*This section will be populated as analysis progresses. Expected insights include:\*

# 

# \- Maintenance workload patterns across departments

# \- Labor craft utilization

# \- Department Comparisons

# \- Asset Type Comparisons by Department

# \- Interval optimization opportunities

# \- Resource allocation recommendations

# \- Scheduling efficiency metrics

# 

# ---

# 

# \## Limitations \& Considerations

# 

# \- \*\*Forecast Data:\*\* This is planned maintenance, not actual execution data. Actual work may vary due to production requirements, equipment breakdowns, or resource availability.

# 

# \- \*\*Timeframe:\*\* One-year forecast provides a snapshot but may not capture multi-year maintenance strategy cycles or long-interval PMs.

# 

# \- \*\*Cost Data:\*\* Material cost field (`THISMATCOST`) is largely unpopulated, limiting cost analysis capabilities.

# 

# \- \*\*Confidentiality:\*\* Specific equipment identifiers and some operational details have been retained but should be considered proprietary to Honda Manufacturing.

# 

# \- \*\*Generalizability:\*\* Findings are specific to this manufacturing facility and may not directly apply to other automotive plants or industries.

# 

# ---

# 

# \## References

# 

# \- Maximo Enterprise Asset Management documentation

# \- Honda Manufacturing maintenance standards

# \- INSY6500 course materials (Auburn University)

# \- Industry best practices for preventive maintenance scheduling

# 

# ---

# 

# \## Acknowledgments

# 

# \- INSY6500 instructional team for project guidance

# \- Honda Manufacturing of Alabama M.E.S.D. team for domain expertise

# \- Maximo system administrators for data access support

# 

# ---

# 

# \## License

# 

# This project is for educational purposes as part of INSY6500 coursework. The dataset contains proprietary manufacturing information and should not be redistributed without permission.

# 

# ---

# 

# \## Contact

# 

# \*\*Abby Tucker\*\*

# \*\*Mike Moyer\*\*

# Students, INSY6500 - Python for Analytics  

# Auburn University

# 

# For questions about the analysis or methodology, please refer to project documentation in the notebooks.

# 

# ---

# 

# \*Created: November 2025\*




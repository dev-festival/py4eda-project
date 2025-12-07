
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page config
st.set_page_config(page_title="PM Dashboard", layout="wide")

# Path to outputs 
OUTPUT_DIR = Path(__file__).parent.parent / 'outputs'

# Load data (cached so it only loads once)
@st.cache_data
def load_data():
    df = pd.read_pickle(OUTPUT_DIR / 'data_clean_forecast.pkl')
    df['MONTH'] = df['DUE_DATE'].dt.to_period('M').astype(str)
    df['MONTH_DATE'] = df['DUE_DATE'].dt.to_period('M').dt.to_timestamp()  # For better sorting
    return df

forecast = load_data()

# Sidebar for page navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Dashboard", 
                        ["Executive Overview", "Department Deep Dive", "Workload Calendar", "Operational Insights"])

# =============================================================================
# PAGE 1: EXECUTIVE OVERVIEW
# =============================================================================
if page == "Executive Overview":
    st.title("🏭 Executive Overview - Plant-Wide PM Forecast")
    st.markdown("*12-Month Preventive Maintenance Outlook*")
    st.markdown("---")
    
    # TOP KPI CARDS
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_hours = forecast['PLANNED_LABOR_HRS'].sum()
        st.metric("Total Planned Hours", f"{total_hours:,.0f}")
    
    with col2:
        total_pms = forecast['PMNUM'].nunique()
        st.metric("Total PMs", f"{total_pms:,}")
    
    with col3:
        avg_complexity = forecast['complexity_score'].mean()
        st.metric("Avg Complexity Score", f"{avg_complexity:.2f}")
    
    with col4:
        dept_count = forecast['DEPT_NAME'].nunique()
        st.metric("Departments", f"{dept_count}")
    
    st.markdown("---")
    
    # MONTHLY LABOR HOURS TREND (Stacked by Department)
    st.subheader("📊 Monthly Labor Hours by Department")
    
    monthly_dept = forecast.groupby(['MONTH', 'DEPT_NAME'])['PLANNED_LABOR_HRS'].sum().reset_index()
    monthly_dept = monthly_dept.sort_values('MONTH')
    
    fig1 = px.bar(monthly_dept,
                  x='MONTH',
                  y='PLANNED_LABOR_HRS',
                  color='DEPT_NAME',
                  title="Monthly Planned Labor Hours - All Departments",
                  labels={'PLANNED_LABOR_HRS': 'Planned Hours', 'MONTH': 'Month'},
                  barmode='stack',
                  height=500)
    
    fig1.update_layout(xaxis_tickangle=-45, legend_title_text='Department')
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("---")
    
    # DEPARTMENT COMPARISON TABLE
    st.subheader("📋 Department Comparison")
    
    dept_summary = forecast.groupby('DEPT_NAME').agg({
        'PLANNED_LABOR_HRS': 'sum',
        'PMNUM': 'nunique',
        'complexity_score': 'mean',
        'LABOR_CRAFT': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'N/A'
    }).reset_index()
    
    dept_summary.columns = ['Department', 'Total Hours', 'PM Count', 'Avg Complexity', 'Primary Craft']
    dept_summary['Avg Hours/PM'] = dept_summary['Total Hours'] / dept_summary['PM Count']
    dept_summary = dept_summary.sort_values('Total Hours', ascending=False)
    
    # Format for display
    dept_summary_display = dept_summary.copy()
    dept_summary_display['Total Hours'] = dept_summary_display['Total Hours'].apply(lambda x: f"{x:,.0f}")
    dept_summary_display['Avg Hours/PM'] = dept_summary_display['Avg Hours/PM'].apply(lambda x: f"{x:.1f}")
    dept_summary_display['Avg Complexity'] = dept_summary_display['Avg Complexity'].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(dept_summary_display, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # SCOPE TYPE BREAKDOWN
    st.subheader("🎯 Scope Type Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        scope_counts = forecast['PMSCOPETYPE'].value_counts().reset_index()
        scope_counts.columns = ['Scope Type', 'Count']
        
        fig2 = px.pie(scope_counts,
                      values='Count',
                      names='Scope Type',
                      title="PM Distribution by Scope Type",
                      color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        # Job type breakdown
        job_counts = forecast['JOB_TYPE'].value_counts().head(10).reset_index()
        job_counts.columns = ['Job Type', 'Count']
        
        fig3 = px.bar(job_counts,
                      x='Count',
                      y='Job Type',
                      orientation='h',
                      title="Top 10 Job Types",
                      color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig3, use_container_width=True)

# =============================================================================
# PAGE 2: DEPARTMENT DEEP DIVE
# =============================================================================
elif page == "Department Deep Dive":
    st.title("🔍 Department Deep Dive")
    st.markdown("*Detailed analysis for individual departments*")
    st.markdown("---")
    
    # DEPARTMENT SELECTOR - BUTTONS
    st.subheader("Select Department")
    
    dept_list = sorted(forecast['DEPT_NAME'].unique().tolist())
    
    # Create columns for buttons (adjust number based on how many departments you have)
    # Using 4 columns, but you can change this
    cols_per_row = 6
    
    # Split departments into rows
    for i in range(0, len(dept_list), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(dept_list):
                dept = dept_list[i + j]
                with col:
                    if st.button(dept, key=f"dept_{dept}", use_container_width=True):
                        st.session_state.selected_dept = dept
    
    # Get selected department (default to first one if none selected)
    if 'selected_dept' not in st.session_state:
        st.session_state.selected_dept = dept_list[0]
    
    selected_dept = st.session_state.selected_dept
    
    st.markdown(f"### Currently viewing: **{selected_dept}**")
    st.markdown("---")
    
    # Filter data for selected department
    dept_data = forecast[forecast['DEPT_NAME'] == selected_dept].copy()
    
    # KEY METRICS CARDS
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        dept_hours = dept_data['total_labor_hrs'].sum()
        st.metric("Total Hours", f"{dept_hours:,.0f}")
    
    with col2:
        dept_pms = dept_data['PMNUM'].nunique()
        st.metric("Total PMs", f"{dept_pms:,}")
    
    with col3:
        dept_complexity = dept_data['complexity_score'].mean()
        st.metric("Avg Complexity", f"{dept_complexity:.2f}")
    
    with col4:
        dominant_craft = dept_data['LABOR_CRAFT'].mode()[0] if len(dept_data['LABOR_CRAFT'].mode()) > 0 else 'N/A'
        st.metric("Primary Craft", dominant_craft)
    
    with col5:
        avg_hrs_per_pm = dept_hours / dept_pms if dept_pms > 0 else 0
        st.metric("Avg Hrs/PM", f"{avg_hrs_per_pm:.1f}")
    
    st.markdown("---")
    
    # MONTHLY FORECAST WITH CRAFT BREAKDOWN =========================================================
    st.subheader("📅 Monthly Labor Hours by Craft")
    
    # Craft filter
    available_crafts = sorted(dept_data['LABOR_CRAFT'].dropna().unique().tolist())
    selected_crafts = st.multiselect("Filter by Craft", available_crafts, default=available_crafts)
    
    filtered_dept_data = dept_data[dept_data['LABOR_CRAFT'].isin(selected_crafts)]
    
    monthly_craft = filtered_dept_data.groupby(['MONTH', 'LABOR_CRAFT'])['total_labor_hrs'].sum().reset_index()
    monthly_craft = monthly_craft.sort_values('MONTH')
    
    fig1 = px.area(monthly_craft,
                   x='MONTH',
                   y='total_labor_hrs',
                   color='LABOR_CRAFT',
                   title=f"{selected_dept} - Monthly Labor Hours by Craft",
                   labels={'total_labor_hours': 'Planned Hours', 'MONTH': 'Month'},
                   height=400)
    
    fig1.update_layout(
        xaxis_tickangle=-45, 
        legend_title_text='Craft',
        #hovermode='x unified'  # Nice hover effect that shows all crafts at once
    )
    st.plotly_chart(fig1, use_container_width=True)

    # COLLAPSIBLE DETAIL DATA
    if st.checkbox("📋 View detailed data", key="monthly_craft_detail"):
        st.markdown("#### Detailed Monthly Data")
        
        # Month filter for detail view
        all_months_option = ['All Months'] + sorted(filtered_dept_data['MONTH'].unique().tolist())
        selected_month_detail = st.selectbox("Filter by Month", all_months_option, key="month_detail_filter")
        
        # Filter data based on selection
        if selected_month_detail == 'All Months':
            detail_data = filtered_dept_data.copy()
        else:
            detail_data = filtered_dept_data[filtered_dept_data['MONTH'] == selected_month_detail].copy()
        
        # Show preview
        st.markdown(f"**Showing {len(detail_data)} records**")
        st.dataframe(detail_data, use_container_width=True, height=400)

    st.markdown("---")
    
    # ZONE/LINE ANALYSIS (switches based on department) =========================================================
    st.subheader("📍 Zone/Line Analysis")
    
    # Determine if this department uses LINE or ZONENAME
    # Check which has more non-null values for this department
    line_count = dept_data['LINE'].notna().sum()
    zone_count = dept_data['ZONENAME'].notna().sum()
    
    use_line = line_count > zone_count or selected_dept == 'MACHINING'
    location_type = 'LINE' if use_line else 'ZONENAME'
    location_col = 'LINE' if use_line else 'ZONENAME'
    
    st.info(f"**{selected_dept}** uses **{location_type}** for location tracking")
    
    # Filter out null values
    zone_data = filtered_dept_data[filtered_dept_data[location_col].notna()].copy()

    
    if len(zone_data) == 0:
        st.warning(f"No {location_type} data available for this department")
    else:
        # Aggregate by zone/line
        zone_summary = zone_data.groupby(location_col).agg({
            'PMNUM': 'nunique',  # Total unique PMs
            'COUNTKEY': 'count',  # Total PM occurrences
            'PLANNED_LABOR_HRS': 'sum',
            'total_labor_hrs': 'sum'
        }).reset_index()
        
        zone_summary.columns = [location_type, 'Unique PMs', 'Total Occurrences', 
                                'Planned Labor Hrs', 'Total Labor Hrs']

        # FILTER OUT ZEROS
        zone_summary = zone_summary[
            (zone_summary['Planned Labor Hrs'] > 0) | 
            (zone_summary['Total Labor Hrs'] > 0)
        ]
        
        # Visualization choice
        viz_type = st.radio("Select Visualization", 
                           ["Heatmap - Labor Hours", "Scatter - Occurrences vs Hours"],
                           horizontal=True)
        
        if viz_type == "Heatmap - Labor Hours":
            # Heatmap showing both planned and total labor hours
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.bar(zone_summary,
                             x=location_type,
                             y='Planned Labor Hrs',
                             title=f"Planned Labor Hours by {location_type}",
                             color='Planned Labor Hrs',
                             color_continuous_scale='Blues',
                             labels={'Planned Labor Hrs': 'Hours'})
                fig1.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.bar(zone_summary,
                             x=location_type,
                             y='Total Labor Hrs',
                             title=f"Total Labor Hours by {location_type}",
                             color='Total Labor Hrs',
                             color_continuous_scale='Reds',
                             labels={'Total Labor Hrs': 'Hours'})
                fig2.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig2, use_container_width=True)
        
        else:  # Scatter plot
            fig3 = px.scatter(zone_summary,
                             x='Total Occurrences',
                             y='Total Labor Hrs',
                             size='Unique PMs',
                             color='Planned Labor Hrs',
                             hover_name=location_type,
                             title=f"{location_type} Workload Analysis (bubble size = unique PMs)",
                             labels={'Total Occurrences': 'PM Occurrences',
                                    'Total Labor Hrs': 'Total Labor Hours'},
                             color_continuous_scale='Viridis',
                             height=500)
            
            # Add zone/line labels to points
            fig3.update_traces(textposition='top center')
            
            st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("---")
        
        # Summary table
        st.subheader(f"📊 {location_type} Summary Table")
        
        zone_summary_display = zone_summary.copy()
        zone_summary_display['Planned Labor Hrs'] = zone_summary_display['Planned Labor Hrs'].apply(lambda x: f"{x:,.0f}")
        zone_summary_display['Total Labor Hrs'] = zone_summary_display['Total Labor Hrs'].apply(lambda x: f"{x:,.0f}")
        zone_summary_display = zone_summary_display.sort_values('Total Occurrences', ascending=False)
        
        st.dataframe(zone_summary_display, use_container_width=True, hide_index=True)

    st.markdown("---")
    
    # ROW 2: JOB TYPE MIX & COMPLEXITY DISTRIBUTION
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Job Type Mix")
        job_type_dist = dept_data['JOB_TYPE'].value_counts().reset_index()
        job_type_dist.columns = ['Job Type', 'Count']
        
        fig2 = px.pie(job_type_dist,
                      values='Count',
                      names='Job Type',
                      title=f"{selected_dept} - Job Types",
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        st.subheader("📊 Complexity Distribution")
        complexity_dist = dept_data['complexity_level'].value_counts().reset_index()
        complexity_dist.columns = ['Complexity Level', 'Count']
        
        # Order by complexity
        complexity_order = ['Low', 'Medium', 'High', 'Very High']
        complexity_dist['Complexity Level'] = pd.Categorical(
            complexity_dist['Complexity Level'], 
            categories=complexity_order, 
            ordered=True
        )
        complexity_dist = complexity_dist.sort_values('Complexity Level')
        
        fig3 = px.bar(complexity_dist,
                      x='Complexity Level',
                      y='Count',
                      title=f"{selected_dept} - PM Complexity Levels",
                      color='Complexity Level',
                      color_discrete_map={'Low': '#90EE90', 'Medium': '#FFD700', 
                                         'High': '#FFA500', 'Very High': '#FF6347'})
        st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")
    
    # TOP 10 MOST COMPLEX PMs =========================================================
    st.subheader("🎯 Top 10 Most Complex PMs")
    
    # Aggregate to unique PMs (since same PM can appear multiple times for different crafts/dates)
    top_complex = dept_data.groupby('PMNUM').agg({
        'PMDESCRIPTION': 'first',
        'complexity_score': 'mean',
        'PLANNED_LABOR_HRS': 'sum',
        'TASK_COUNT': 'first',
        'JOB_TYPE': 'first'
    }).nlargest(10, 'complexity_score').reset_index()
    
    top_complex.columns = ['PM Number', 'Description', 'Complexity Score', 
                           'Total Planned Hours', 'Task Count', 'Job Type']
    
    # Format for display
    top_complex['Complexity Score'] = top_complex['Complexity Score'].apply(lambda x: f"{x:.2f}")
    top_complex['Total Planned Hours'] = top_complex['Total Planned Hours'].apply(lambda x: f"{x:.1f}")
    
    st.dataframe(top_complex, use_container_width=True, hide_index=True)
    

    st.markdown("---")
    
    # INTERVAL FREQUENCY ANALYSIS ===============================================================
    st.subheader("⏰ Maintenance Interval Deep Dive")
    
    # Key insight callout about daily complexity
    st.info("💡 **Insight**: Daily PMs often show higher complexity scores due to extensive task lists despite lower individual time commitments.")
    
    # INTERVAL VS COMPLEXITY
    st.markdown("#### Interval Complexity Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Complexity by interval
        interval_complexity = filtered_dept_data.groupby('interval_category').agg({
            'complexity_score': 'mean',
            'PMNUM': 'nunique',
            'PLANNED_LABOR_HRS': 'sum'
        }).reset_index()
        interval_complexity.columns = ['Interval', 'Avg Complexity', 'PM Count', 'Total Hours']
        interval_complexity = interval_complexity.sort_values('Avg Complexity', ascending=False)
        
        fig1 = px.bar(interval_complexity,
                      x='Interval',
                      y='Avg Complexity',
                      title=f"{selected_dept} - Average Complexity by Interval",
                      color='Avg Complexity',
                      color_continuous_scale='Reds',
                      text='Avg Complexity')
        
        fig1.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Hours per PM by interval
        interval_complexity['Hours per PM'] = interval_complexity['Total Hours'] / interval_complexity['PM Count']
        
        fig2 = px.bar(interval_complexity,
                      x='Interval',
                      y='Hours per PM',
                      title=f"{selected_dept} - Labor Hours per PM by Interval",
                      color='Hours per PM',
                      color_continuous_scale='Blues',
                      text='Hours per PM')
        
        fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig2.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    # MONTHLY INTERVAL STACKING - LABOR HOURS
    st.markdown("#### Monthly Labor Bottleneck Analysis")
    st.markdown("*How do different interval types stack up month-to-month?*")
    
    # Toggle between labor hours and laborers
    metric_choice = st.radio("View by:", 
                             ["Total Labor Hours", "Total Laborers Required"],
                             horizontal=True,
                             key="interval_metric")
    
    if metric_choice == "Total Labor Hours":
        metric_col = 'PLANNED_LABOR_HRS'
        y_label = 'Planned Labor Hours'
    else:
        metric_col = 'PLANNED_LABORERS'
        y_label = 'Planned Laborers'
    
    # Aggregate by month and interval
    monthly_interval = filtered_dept_data.groupby(['MONTH', 'interval_category'])[metric_col].sum().reset_index()
    monthly_interval = monthly_interval.sort_values('MONTH')
    
    fig3 = px.bar(monthly_interval,
                  x='MONTH',
                  y=metric_col,
                  color='interval_category',
                  title=f"{selected_dept} - Monthly {metric_choice} by Interval Type",
                  labels={metric_col: y_label, 'interval_category': 'Interval'},
                  barmode='stack',
                  height=500)
    
    fig3.update_layout(
        xaxis_tickangle=-45,
        legend_title_text='Interval Type',
        hovermode='x unified'
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")
    
    # BOTTLENECK IDENTIFICATION
    st.markdown("#### 🚨 Potential Bottleneck Months")
    
    # Find months with highest workload by interval type
    monthly_totals = filtered_dept_data.groupby('MONTH').agg({
        'PLANNED_LABOR_HRS': 'sum',
        'PLANNED_LABORERS': 'sum',
        'PMNUM': 'nunique'
    }).reset_index()
    monthly_totals.columns = ['Month', 'Total Hours', 'Total Laborers', 'PM Count']
    monthly_totals = monthly_totals.sort_values('Total Hours', ascending=False)
    
    # Top 3 bottleneck months
    col1, col2, col3 = st.columns(3)
    
    for idx, (i, row) in enumerate(monthly_totals.head(3).iterrows()):
        with [col1, col2, col3][idx]:
            st.metric(
                label=f"#{idx+1}: {row['Month']}",
                value=f"{row['Total Hours']:,.0f} hrs",
                delta=f"{row['Total Laborers']:.0f} laborers | {row['PM Count']} PMs"
            )
    
    st.markdown("---")
    
    # INTERVAL MIX TABLE
    st.markdown("#### 📊 Interval Breakdown Table")
    
    interval_summary = filtered_dept_data.groupby('interval_category').agg({
        'PMNUM': 'nunique',
        'COUNTKEY': 'count',
        'PLANNED_LABOR_HRS': 'sum',
        'PLANNED_LABORERS': 'sum',
        'complexity_score': 'mean',
        'TASK_COUNT': 'mean'
    }).reset_index()
    
    interval_summary.columns = ['Interval', 'Unique PMs', 'Total Occurrences', 
                                'Total Hours', 'Total Laborers', 'Avg Complexity', 'Avg Tasks']
    interval_summary['Hours per PM'] = interval_summary['Total Hours'] / interval_summary['Unique PMs']
    interval_summary = interval_summary.sort_values('Total Hours', ascending=False)
    
    # Format for display
    interval_summary_display = interval_summary.copy()
    interval_summary_display['Total Hours'] = interval_summary_display['Total Hours'].apply(lambda x: f"{x:,.0f}")
    interval_summary_display['Total Laborers'] = interval_summary_display['Total Laborers'].apply(lambda x: f"{x:,.0f}")
    interval_summary_display['Hours per PM'] = interval_summary_display['Hours per PM'].apply(lambda x: f"{x:.1f}")
    interval_summary_display['Avg Complexity'] = interval_summary_display['Avg Complexity'].apply(lambda x: f"{x:.2f}")
    interval_summary_display['Avg Tasks'] = interval_summary_display['Avg Tasks'].apply(lambda x: f"{x:.1f}")
    
    st.dataframe(interval_summary_display, use_container_width=True, hide_index=True)
    
    # INTERVAL BREAKDOWN
    st.subheader("⏰ Maintenance Interval Breakdown")
    
    interval_dist = dept_data['interval_category'].value_counts().reset_index()
    interval_dist.columns = ['Interval Category', 'Count']
    
    fig4 = px.bar(interval_dist,
                  x='Interval Category',
                  y='Count',
                  title=f"{selected_dept} - PM Frequency Distribution",
                  color='Count',
                  color_continuous_scale='Blues')
    
    st.plotly_chart(fig4, use_container_width=True)

# =============================================================================
# PAGE 3: WORKLOAD CALENDAR
# =============================================================================
elif page == "Workload Calendar":
    st.title("📅 Workload Calendar Heatmap")
    st.markdown("*Visualize PM density and identify scheduling bottlenecks*")
    st.markdown("---")
    
    # FILTERS IN SIDEBAR
    st.sidebar.header("Calendar Filters")
    
    # Department filter
    dept_options = ['All Departments'] + sorted(forecast['DEPT_NAME'].unique().tolist())
    selected_dept_cal = st.sidebar.selectbox("Department", dept_options, key="cal_dept")
    
    # Craft filter
    craft_options = ['All Crafts'] + sorted(forecast['LABOR_CRAFT'].dropna().unique().tolist())
    selected_craft_cal = st.sidebar.selectbox("Craft", craft_options, key="cal_craft")
    
    # Complexity filter
    complexity_options = ['All Levels'] + sorted(forecast['complexity_level'].dropna().unique().tolist())
    selected_complexity = st.sidebar.selectbox("Complexity Level", complexity_options, key="cal_complexity")
    
    # Filter data
    cal_data = forecast.copy()
    
    if selected_dept_cal != 'All Departments':
        cal_data = cal_data[cal_data['DEPT_NAME'] == selected_dept_cal]
    
    if selected_craft_cal != 'All Crafts':
        cal_data = cal_data[cal_data['LABOR_CRAFT'] == selected_craft_cal]
    
    if selected_complexity != 'All Levels':
        cal_data = cal_data[cal_data['complexity_level'] == selected_complexity]
    
    # SUMMARY METRICS
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_hours = cal_data['PLANNED_LABOR_HRS'].sum()
        st.metric("Total Planned Hours", f"{total_hours:,.0f}")
    
    with col2:
        total_pms = cal_data['PMNUM'].nunique()
        st.metric("Total PMs", f"{total_pms:,}")
    
    with col3:
        peak_month = cal_data.groupby('MONTH')['PLANNED_LABOR_HRS'].sum().idxmax()
        st.metric("Peak Month", peak_month)
    
    st.markdown("---")
    
    # MONTHLY HEATMAP
    st.subheader("🔥 Monthly Labor Hours Heatmap")
    
    # Aggregate by month
    monthly_hours = cal_data.groupby('MONTH')['PLANNED_LABOR_HRS'].sum().reset_index()
    monthly_hours = monthly_hours.sort_values('MONTH')
    
    # Create heatmap-style visualization
    fig1 = px.bar(monthly_hours,
                  x='MONTH',
                  y='PLANNED_LABOR_HRS',
                  title="Monthly Workload Distribution",
                  labels={'PLANNED_LABOR_HRS': 'Planned Hours', 'MONTH': 'Month'},
                  color='PLANNED_LABOR_HRS',
                  color_continuous_scale='YlOrRd',  # Yellow to Red heat colors
                  height=400)
    
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("---")
    
    # WEEKLY BREAKDOWN (More granular view)
    st.subheader("📊 Weekly Workload Breakdown")
    
    # Add week number
    cal_data['WEEK'] = cal_data['DUE_DATE'].dt.isocalendar().week
    cal_data['YEAR_WEEK'] = cal_data['DUE_DATE'].dt.strftime('%Y-W%U')
    
    weekly_hours = cal_data.groupby('YEAR_WEEK')['PLANNED_LABOR_HRS'].sum().reset_index()
    weekly_hours = weekly_hours.sort_values('YEAR_WEEK')
    
    # Limit to first 52 weeks if data spans multiple years
    if len(weekly_hours) > 52:
        weekly_hours = weekly_hours.head(52)
    
    fig2 = go.Figure(data=go.Scatter(
        x=weekly_hours['YEAR_WEEK'],
        y=weekly_hours['PLANNED_LABOR_HRS'],
        mode='lines+markers',
        line=dict(color='#FF6B6B', width=2),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(255, 107, 107, 0.2)'
    ))
    
    fig2.update_layout(
        title="Weekly Labor Hours Trend",
        xaxis_title="Week",
        yaxis_title="Planned Hours",
        height=400,
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    # PM COUNT HEATMAP BY MONTH AND DEPARTMENT
    st.subheader("🗓️ Department Workload Calendar")
    
    # Create month x department heatmap
    dept_month_pivot = cal_data.groupby(['MONTH', 'DEPT_NAME'])['PLANNED_LABOR_HRS'].sum().reset_index()
    dept_month_pivot = dept_month_pivot.pivot(index='DEPT_NAME', columns='MONTH', values='PLANNED_LABOR_HRS').fillna(0)
    
    fig3 = px.imshow(dept_month_pivot,
                     labels=dict(x="Month", y="Department", color="Planned Hours"),
                     title="Department Workload Heatmap (All Months)",
                     color_continuous_scale='RdYlGn_r',  # Red = high, Green = low
                     aspect="auto",
                     height=500)
    
    fig3.update_xaxes(side="bottom", tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")
    
    # BOTTLENECK ANALYSIS
    st.subheader("⚠️ Potential Scheduling Bottlenecks")
    
    # Find months with highest workload
    monthly_stats = cal_data.groupby('MONTH').agg({
        'PLANNED_LABOR_HRS': 'sum',
        'PMNUM': 'nunique',
        'LABOR_CRAFT': lambda x: x.nunique()
    }).reset_index()
    
    monthly_stats.columns = ['Month', 'Total Hours', 'PM Count', 'Unique Crafts']
    monthly_stats = monthly_stats.sort_values('Total Hours', ascending=False)
    
    # Highlight top 3 busiest months
    st.markdown("**Top 3 Busiest Months:**")
    top_3 = monthly_stats.head(3)
    
    for idx, row in top_3.iterrows():
        st.warning(f"**{row['Month']}**: {row['Total Hours']:,.0f} hours | {row['PM Count']} PMs | {row['Unique Crafts']} crafts needed")
    
    st.markdown("---")
    
    # Full monthly breakdown table
    st.subheader("📋 Monthly Breakdown Table")
    monthly_stats_display = monthly_stats.copy()
    monthly_stats_display['Total Hours'] = monthly_stats_display['Total Hours'].apply(lambda x: f"{x:,.0f}")
    
    st.dataframe(monthly_stats_display, use_container_width=True, hide_index=True)

# =============================================================================
# PAGE 4: OPERATIONAL INSIGHTS
# =============================================================================
elif page == "Operational Insights":
    st.title("💡 Operational Insights")
    st.markdown("*Strategic patterns across maintenance operations*")
    st.markdown("---")
    
    # INTERVAL PATTERNS
    st.subheader("⏰ Maintenance Interval Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Interval distribution
        interval_dist = forecast['interval_category'].value_counts().reset_index()
        interval_dist.columns = ['Interval Category', 'PM Count']
        
        # Calculate labor hours by interval
        interval_hours = forecast.groupby('interval_category')['PLANNED_LABOR_HRS'].sum().reset_index()
        interval_hours.columns = ['Interval Category', 'Total Hours']
        
        interval_summary = interval_dist.merge(interval_hours, on='Interval Category')
        interval_summary = interval_summary.sort_values('PM Count', ascending=False)
        
        fig1 = px.bar(interval_summary,
                      x='Interval Category',
                      y='PM Count',
                      title="PM Distribution by Frequency",
                      color='Total Hours',
                      color_continuous_scale='Blues',
                      labels={'PM Count': 'Number of PMs'})
        
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Hours distribution by interval
        fig2 = px.pie(interval_summary,
                      values='Total Hours',
                      names='Interval Category',
                      title="Labor Hours by Interval Type",
                      color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    # CRAFT UTILIZATION ACROSS DEPARTMENTS
    st.subheader("🔧 Craft Utilization Across Departments")
    
    # Craft x Department heatmap
    craft_dept = forecast.groupby(['DEPT_NAME', 'LABOR_CRAFT'])['PLANNED_LABOR_HRS'].sum().reset_index()
    craft_dept_pivot = craft_dept.pivot(index='LABOR_CRAFT', columns='DEPT_NAME', values='PLANNED_LABOR_HRS').fillna(0)
    
    fig3 = px.imshow(craft_dept_pivot,
                     labels=dict(x="Department", y="Craft", color="Planned Hours"),
                     title="Craft Utilization Heatmap - Hours by Department & Craft",
                     color_continuous_scale='Viridis',
                     aspect="auto",
                     height=500)
    
    fig3.update_xaxes(side="bottom", tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("---")
    
    # ASSET VS LOCATION SCOPE PREFERENCES
    st.subheader("🎯 Asset vs Location Scope Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Overall scope distribution
        scope_dist = forecast['PMSCOPETYPE'].value_counts().reset_index()
        scope_dist.columns = ['Scope Type', 'Count']
        
        fig4 = px.pie(scope_dist,
                      values='Count',
                      names='Scope Type',
                      title="Overall Scope Distribution",
                      color_discrete_sequence=['#FF6B6B', '#4ECDC4'])
        st.plotly_chart(fig4, use_container_width=True)
    
    with col2:
        # Scope by department
        scope_dept = forecast.groupby(['DEPT_NAME', 'PMSCOPETYPE']).size().reset_index(name='Count')
        scope_dept_pivot = scope_dept.pivot(index='DEPT_NAME', columns='PMSCOPETYPE', values='Count').fillna(0)
        
        # Calculate percentage
        scope_dept_pivot['Asset %'] = (scope_dept_pivot.get('ASSET', 0) / 
                                       (scope_dept_pivot.get('ASSET', 0) + scope_dept_pivot.get('LOCATION', 0)) * 100)
        scope_dept_pivot = scope_dept_pivot.sort_values('Asset %', ascending=False).reset_index()
        
        fig5 = px.bar(scope_dept_pivot,
                      x='DEPT_NAME',
                      y='Asset %',
                      title="Department Asset-Focus Ranking",
                      labels={'Asset %': 'Asset Focus %', 'DEPT_NAME': 'Department'},
                      color='Asset %',
                      color_continuous_scale='RdYlGn')
        
        fig5.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig5, use_container_width=True)
    
    st.markdown("---")
    
    # TASK COMPLEXITY TRENDS
    st.subheader("📈 Task Complexity Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Complexity by department
        complexity_dept = forecast.groupby('DEPT_NAME')['complexity_score'].mean().reset_index()
        complexity_dept.columns = ['Department', 'Avg Complexity Score']
        complexity_dept = complexity_dept.sort_values('Avg Complexity Score', ascending=False)
        
        fig6 = px.bar(complexity_dept,
                      x='Avg Complexity Score',
                      y='Department',
                      orientation='h',
                      title="Average Complexity by Department",
                      color='Avg Complexity Score',
                      color_continuous_scale='Reds')
        st.plotly_chart(fig6, use_container_width=True)
    
    with col2:
        # Complexity level distribution
        complexity_level_dist = forecast['complexity_level'].value_counts().reset_index()
        complexity_level_dist.columns = ['Complexity Level', 'Count']
        
        # Order properly
        complexity_order = ['Low', 'Medium', 'High', 'Very High']
        complexity_level_dist['Complexity Level'] = pd.Categorical(
            complexity_level_dist['Complexity Level'],
            categories=complexity_order,
            ordered=True
        )
        complexity_level_dist = complexity_level_dist.sort_values('Complexity Level')
        
        fig7 = px.bar(complexity_level_dist,
                      x='Complexity Level',
                      y='Count',
                      title="PM Distribution by Complexity Level",
                      color='Complexity Level',
                      color_discrete_map={'Low': '#90EE90', 'Medium': '#FFD700',
                                         'High': '#FFA500', 'Very High': '#FF6347'})
        st.plotly_chart(fig7, use_container_width=True)
    
    st.markdown("---")
    
    # JOB TYPE INSIGHTS
    st.subheader("🏗️ Job Type Distribution")
    
    job_type_summary = forecast.groupby('JOB_TYPE').agg({
        'PMNUM': 'nunique',
        'PLANNED_LABOR_HRS': 'sum',
        'complexity_score': 'mean'
    }).reset_index()
    
    job_type_summary.columns = ['Job Type', 'PM Count', 'Total Hours', 'Avg Complexity']
    job_type_summary = job_type_summary.sort_values('Total Hours', ascending=False).head(15)
    
    fig8 = px.scatter(job_type_summary,
                      x='PM Count',
                      y='Total Hours',
                      size='Avg Complexity',
                      color='Avg Complexity',
                      hover_name='Job Type',
                      title="Job Type Analysis - Count vs Hours (bubble size = complexity)",
                      labels={'PM Count': 'Number of PMs', 'Total Hours': 'Total Labor Hours'},
                      color_continuous_scale='Plasma',
                      height=500)
    
    st.plotly_chart(fig8, use_container_width=True)
    
    st.markdown("---")
    
    # KEY INSIGHTS TABLE
    st.subheader("📊 Summary Statistics by Job Type")
    
    job_type_table = job_type_summary.copy()
    job_type_table['Total Hours'] = job_type_table['Total Hours'].apply(lambda x: f"{x:,.0f}")
    job_type_table['Avg Complexity'] = job_type_table['Avg Complexity'].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(job_type_table, use_container_width=True, hide_index=True)
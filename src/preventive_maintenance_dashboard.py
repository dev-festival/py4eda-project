
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path

# Page config
st.set_page_config(page_title="PM Dashboard", layout="wide")

# Path to outputs 
OUTPUT_DIR = Path(__file__).parent.parent / 'outputs'

# Load data (cached so it only loads once)
@st.cache_data
def load_data():
    # Forecast/ planning datase 
    df = pd.read_pickle(OUTPUT_DIR / 'data_clean_forecast.pkl')
    df['MONTH'] = df['DUE_DATE'].dt.to_period('M').astype(str)
    df['MONTH_DATE'] = df['DUE_DATE'].dt.to_period('M').dt.to_timestamp()

    # merged dataset 
    path2 = pd.read_pickle(OUTPUT_DIR / 'Path2_analysis.pkl')
    
    # For better sorting
    return df, path2

forecast, path2 = load_data()

# Sidebar for page navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Dashboard", 
                        ["Executive Overview", "Department Deep Dive", "Workload Calendar", "Operational Insights", "Plan vs Execution"])

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
    
    # HELPER FUNCTION - Clean dataset for user output
    def get_clean_output(df):
        """Returns a clean dataframe for user download/viewing"""
        # Select columns (exclude internal calculations)
        output_columns = [col for col in df.columns if col not in [
            'complexity_score', 'task_norm', 'hours_norm', 'desc_norm', 
            'MONTH_DATE', 'total_labor_per_occ_capped'
        ]]
        
        clean_df = df[output_columns].copy()
        
        # Rename columns for clarity
        clean_df = clean_df.rename(columns={
            'task_density': 'tasks_per_hour'
        })

        clean_df = clean_df.set_index('PMNUM')
        
        return clean_df


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
        
        # Apply clean output function
        detail_data_clean = get_clean_output(detail_data)
        
        # Show preview
        st.markdown(f"**Showing {len(detail_data_clean)} records**")
        st.dataframe(detail_data_clean, use_container_width=True, height=400)

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
                             y='Total Labor Hrs',
                             title=f"Total Labor Hours by {location_type}",
                             color='Total Labor Hrs',
                             color_continuous_scale='Blues',
                             labels={'Total Labor Hrs': 'Hours'})
                fig1.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Zone Interval Mix
                zone_interval = zone_data.groupby([location_col, 'interval_category'])['total_labor_hrs'].sum().reset_index()
                
                # Filter out zeros
                zone_interval = zone_interval[zone_interval['total_labor_hrs'] > 0]
                
                if zone_interval.empty:
                    st.warning("No interval data available")
                else:
                    fig2 = px.bar(zone_interval,
                                 x=location_col,
                                 y='total_labor_hrs',
                                 color='interval_category',
                                 title=f"{location_type} Workload by Interval Type",
                                 labels={'total_labor_hrs': 'Total Labor Hours', 
                                        'interval_category': 'Interval'},
                                 barmode='stack',
                                 color_discrete_sequence=px.colors.qualitative.Set2)
                    
                    fig2.update_layout(
                        xaxis_tickangle=-45,
                        legend_title_text='Interval Type',
                        height=450
                    )
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
        
        # COLLAPSIBLE ZONE DETAIL DATA
        if st.checkbox("📋 View zone detailed data", key="zone_detail"):
            st.markdown("#### Zone/Line Detailed Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Zone/Line filter
                all_zones_option = ['All'] + sorted(zone_data[location_col].dropna().unique().tolist())
                selected_zone_filter = st.selectbox(f"Filter by {location_type}", all_zones_option, key="zone_filter")
            
            with col2:
                # Interval filter
                all_intervals_option = ['All Intervals'] + sorted(zone_data['interval_category'].dropna().unique().tolist())
                selected_interval_filter = st.selectbox("Filter by Interval", all_intervals_option, key="interval_filter")
            
            # Apply filters
            zone_detail_data = zone_data.copy()
            
            if selected_zone_filter != 'All':
                zone_detail_data = zone_detail_data[zone_detail_data[location_col] == selected_zone_filter]
            
            if selected_interval_filter != 'All Intervals':
                zone_detail_data = zone_detail_data[zone_detail_data['interval_category'] == selected_interval_filter]
            
            # Apply clean output function
            zone_detail_clean = get_clean_output(zone_detail_data)
            
            # Show preview
            st.markdown(f"**Showing {len(zone_detail_clean)} records**")
            st.dataframe(zone_detail_clean, use_container_width=True, height=400)

        st.markdown("---")
        
        # Summary table
        st.subheader(f"📊 Zone/Line Summary Table")
        
        zone_summary_display = zone_summary.copy()
        zone_summary_display['Planned Labor Hrs'] = zone_summary_display['Planned Labor Hrs'].apply(lambda x: f"{x:,.0f}")
        zone_summary_display['Total Labor Hrs'] = zone_summary_display['Total Labor Hrs'].apply(lambda x: f"{x:,.0f}")
        zone_summary_display = zone_summary_display.sort_values('Total Occurrences', ascending=False)
        
        st.dataframe(zone_summary_display, use_container_width=True, hide_index=True)

    st.markdown("---")
    
   
    # COMPLEXITY FACTOR DISTRIBUTION (KDE)
    st.subheader("📈 Complexity Factor Distributions")
    st.markdown("*Kernel Density Estimation of the three components that make up the complexity score*")

    # COMPLEXITY LEVEL FILTER
    complexity_options = ['All Levels'] + sorted(dept_data['complexity_level'].dropna().unique().tolist())
    selected_complexity_filter = st.selectbox("Filter by Complexity Level", complexity_options, key="complexity_filter")

    # Apply complexity filter
    if selected_complexity_filter == 'All Levels':
        complexity_filtered_data = filtered_dept_data.copy()
    else:
        complexity_filtered_data = filtered_dept_data[filtered_dept_data['complexity_level'] == selected_complexity_filter]
    
    # Create KDE line plots
    fig_kde = go.Figure()
    
    # Task norm KDE
    from scipy.stats import gaussian_kde
    
    # Task norm
    task_kde = gaussian_kde(complexity_filtered_data['task_norm'].dropna())
    task_x = np.linspace(0, 1, 200)
    task_y = task_kde(task_x)
    
    fig_kde.add_trace(go.Scatter(
        x=task_x,
        y=task_y,
        name='Task Count (normalized)',
        mode='lines',
        line=dict(color='#81f2e9', width=2),
        fill='tozeroy',
        fillcolor='rgba(129, 242, 233, 0.2)'
    ))
    
    # Hours norm
    hours_kde = gaussian_kde(complexity_filtered_data['hours_norm'].dropna())
    hours_x = np.linspace(0, 1, 200)
    hours_y = hours_kde(hours_x)
    
    fig_kde.add_trace(go.Scatter(
        x=hours_x,
        y=hours_y,
        name='Labor Hours (normalized)',
        mode='lines',
        line=dict(color='#fcd107', width=2),
        fill='tozeroy',
        fillcolor='rgba(252, 209, 7, 0.2)'
    ))
    
    # Description norm
    desc_kde = gaussian_kde(complexity_filtered_data['desc_norm'].dropna())
    desc_x = np.linspace(0, 1, 200)
    desc_y = desc_kde(desc_x)
    
    fig_kde.add_trace(go.Scatter(
        x=desc_x,
        y=desc_y,
        name='Description Length (normalized)',
        mode='lines',
        line=dict(color='#32f58a', width=2),
        fill='tozeroy',
        fillcolor='rgba(49, 246, 138, 0.2)'
    ))
    
    fig_kde.update_layout(
        title=f"{selected_dept} - Distribution of Normalized Complexity Components",
        xaxis_title="Normalized Value (0-1)",
        yaxis_title="Density",
        height=350,  # Shorter height
        #hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=1.02,  # Position above the chart
            xanchor="center",
            x=0.5
        )
    )
    
    st.plotly_chart(fig_kde, use_container_width=True)
    
    # ROW 2: JOB TYPE MIX & COMPLEXITY DISTRIBUTION
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Job Type Mix")
        job_type_dist = complexity_filtered_data['JOB_TYPE'].value_counts().reset_index()
        job_type_dist.columns = ['Job Type', 'Count']
        
        fig2 = px.pie(job_type_dist,
                      values='Count',
                      names='Job Type',
                      title=f"{selected_dept} - Job Types",
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        st.subheader("📊 Complexity Distribution")
        complexity_dist = complexity_filtered_data['complexity_level'].value_counts().reset_index()
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
    
    # COLLAPSIBLE COMPLEXITY DETAIL DATA
    if st.checkbox("📋 View complexity detailed data", key="complexity_detail"):
        st.markdown("#### Complexity Detailed Data")
        
        # Apply clean output function
        complexity_detail_clean = get_clean_output(complexity_filtered_data)
        
        # Show preview
        st.markdown(f"**Showing {len(complexity_detail_clean)} records** (filtered by: {selected_complexity_filter})")
        st.dataframe(complexity_detail_clean, use_container_width=True, height=400)

    st.markdown("---")
    
    # INTERVAL FREQUENCY ANALYSIS ===============================================================
    st.subheader("⏰ Maintenance Interval Deep Dive")
    
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
                             ["Total Labor Hours", "Labor Assignments"],
                             horizontal=True,
                             key="interval_metric")
    
    if metric_choice == "Total Labor Hours":
        metric_col = 'PLANNED_LABOR_HRS'
        y_label = 'Labor Assignments'
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
    monthly_totals.columns = ['Month', 'Total Hours', 'Labor Assignments', 'PM Count']
    monthly_totals = monthly_totals.sort_values('Total Hours', ascending=False)
    
    # Top 3 bottleneck months
    col1, col2, col3 = st.columns(3)
    
    for idx, (i, row) in enumerate(monthly_totals.head(3).iterrows()):
        with [col1, col2, col3][idx]:
            st.metric(
                label=f"#{idx+1}: {row['Month']}",
                value=f"{row['Total Hours']:,.0f} hrs",
                delta=f"{row['Labor Assignments']:.0f} assignments | {row['PM Count']} PMs"
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
                                'Total Hours', 'Labor Assignments', 'Avg Complexity', 'Avg Tasks']
    interval_summary['Hours per PM'] = interval_summary['Total Hours'] / interval_summary['Unique PMs']
    interval_summary = interval_summary.sort_values('Total Hours', ascending=False)
    
    # Format for display
    interval_summary_display = interval_summary.copy()
    interval_summary_display['Total Hours'] = interval_summary_display['Total Hours'].apply(lambda x: f"{x:,.0f}")
    interval_summary_display['Labor Assignments'] = interval_summary_display['Labor Assignments'].apply(lambda x: f"{x:,.0f}")
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

# ============================================================================
# PAGE 5: Plan vs Execution 
# ============================================================================
elif page == "Plan vs Execution":
    st.title("📊 Plan vs Execution")
    st.markdown("*How well do our PM plans match reality?*")

    st.info("""
    This dashboard compares **planned vs actual labor performance** across PMs, 
    departments, intervals, and job types. Use the filters below and in the sidebar 
    to explore planning accuracy patterns and execution discipline.
    """)

    # Filters 
    st.markdown("### Filters")

    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        dept_filter = st.multiselect(
            "Department", 
            options=sorted(path2['DEPT_NAME'].dropna().unique()), 
            default=[])

    with col_f2:
        interval_filter = st.multiselect(
            "Interval",
            options=sorted(path2['INTERVAL'].dropna().unique()),
            default=[])

    with col_f3:
        job_type_filter = st.multiselect(
            "Job Type", 
            options=sorted(path2['JOB_TYPE'].dropna().unique()),
            default=[])

    # Apply Filters
    path2_filtered = path2.copy()

    if dept_filter:
        path2_filtered = path2_filtered[path2_filtered['DEPT_NAME'].isin(dept_filter)]

    if interval_filter:
        path2_filtered = path2_filtered[path2_filtered['INTERVAL'].isin(interval_filter)]

    if job_type_filter: 
        path2_filtered =path2_filtered[path2_filtered['JOB_TYPE'].isin(job_type_filter)]

    if path2_filtered.empty:
        st.warning("No data for selected filters.")
        st.stop()

    # KPIs 
    st.markdown('### Overall Performance')

    fail_threshold = 0.75

    avg_completion = path2_filtered['completion_rate'].mean()
    avg_ontime = path2_filtered['on_time_rate'].mean()
    avg_bias_hrs = (path2_filtered['AVG_ACTUAL_HRS'] - path2_filtered['AVG_PLANNED_HRS']).mean()
    failing_pm_count = (path2_filtered['completion_rate'] < fail_threshold).sum()
    total_pm_count = path2_filtered['PMNUM'].nunique()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Avg Completion Rate", f"{avg_completion:.1%}")

    with col2: 
        st.metric("Avg On-Time Rate", f"{avg_ontime:.1%}")

    with col3:
        st.metric("Avg Hour Bias (Actual - Planned)", f"{avg_bias_hrs:.2f} hrs")

    with col4: 
        st.metric("Failing PMs (<75% complete)", f"{failing_pm_count} of {total_pm_count}")

    st.write(f"Showing **{total_pm_count:,}** unique PMs based on selected filters.")
    st.success("Execution looks **reasonably strong overall**, but specific departments and categories show opportunities to reduce bias.")

    # Highlight message depending on average completion (use success/warning dynamically)
    if avg_completion >= 0.80:
        st.success("Execution looks strong overall based on selected filters.")
    elif avg_completion >= 0.60:
        st.warning("Execution shows moderate variation; improvement opportunities exist.")
    else:
        st.error("Execution appears weak under current filters; many PMs are failing to meet expectations.")
    
    st.divider()

    # Failing threshold and worst PMs
    st.markdown("### 🚨 Problem PMs")

    fail_threshold = st.slider("Completion Rate Threshold for 'Failing' PMs",
                               min_value=0.0,
                               max_value=1.0,
                               value=0.75,
                               step=0.05)

    failing = path2_filtered[path2_filtered['completion_rate'] < fail_threshold].copy()

    if failing.empty:
        st.info("No PMs below the selected completion threshold.")
    else:
        # Rank by completion then by hour deviation
        failing['rank'] = failing['completion_rate'].rank(method='first')
        worst_pms = (failing
            .sort_values(['completion_rate', 'hour_deviation_pct'])
            [['PMNUM', 'DEPT_NAME', 'INTERVAL', 'JOB_TYPE','completion_rate', 'on_time_rate',
              'AVG_PLANNED_HRS', 'AVG_ACTUAL_HRS', 'hour_deviation_pct']]
            .head(25))

        # format %
        worst_pms['completion_rate'] = (worst_pms['completion_rate'] * 100).round(1).astype(str) + '%'
        worst_pms['on_time_rate'] = (worst_pms['on_time_rate'] * 100).round(1).astype(str) + '%'
        worst_pms['hour_deviation_pct'] = (worst_pms['hour_deviation_pct']).round(1)

        st.dataframe(worst_pms, use_container_width=True, hide_index=True)
        st.caption("Worst-performing PMs based on the selected completion threshold, sorted by completion rate and hour deviation.")

    st.divider()
    
    # Department execution
    st.subheader("🏭 Department Execution Discipline")

    dept_exec = (path2_filtered
                 .groupby('DEPT_NAME', observed=True)
                 .agg(avg_completion=('completion_rate', 'mean'),
                      avg_ontime=('on_time_rate', 'mean'),
                      n_pm=('PMNUM', 'nunique'))
                 .reset_index())

    # Sort by Completion rate
    dept_exec = dept_exec.sort_values('avg_completion')

    fig_dept = px.bar(dept_exec,
                      x='avg_completion',
                      y='DEPT_NAME', 
                      orientation='h',
                      color='avg_completion',
                      color_continuous_scale='RdYlGn', 
                      labels={'avg_completion': 'Avg Completion Rate', 'DEPT_NAME': 'Department'},
                      title='Completion Rate by Department')

    fig_dept.update_layout(xaxis_tickformat='.0%')
    st.plotly_chart(fig_dept, use_container_width=True)
    st.caption("Departments toward the top with higher completion and greener shading show stronger execution discipline.")


    with st.expander('Show department table'):
        tmp = dept_exec.copy()
        tmp['avg_completion'] = (tmp['avg_completion'] * 100).round(1).astype(str) + '%'
        tmp['avg_ontime'] = (tmp['avg_ontime'] * 100).round(1).astype(str) + '%'
        st.dataframe(tmp, use_container_width=True, hide_index=True)

    st.divider()

    # Accuracy by chosen category
    st.subheader("🎯 Accuracy by Category")

    category = st.selectbox("Group by:",
                            options=['INTERVAL', 'JOB_TYPE', 'LABOR_CRAFT'])

    cat_summary = (path2_filtered
        .groupby(category, observed=True)
        .agg(avg_completion=('completion_rate', 'mean'),
            avg_ontime=('on_time_rate', 'mean'),
            avg_hour_dev_pct=('hour_deviation_pct', 'mean'),
            n_pm=('PMNUM', 'nunique'))
        .reset_index()
        .sort_values('avg_completion'))

    fig_cat = px.bar(cat_summary,
                     x='avg_completion',
                     y=category,
                     orientation='h',
                     color='avg_hour_dev_pct',
                     color_continuous_scale='RdYlGn_r',
                     labels={'avg_completion': 'Avg Completion Rate',
                             'avg_hour_dev_pct': 'Avg Hour Deviation %',
                             category: category.replace('_', ' ').title()},
                     title=f"Completion & Bias by {category.replace('_', ' ').title()}")
    
    fig_cat.update_layout(xaxis_tickformat=".0%")
    st.plotly_chart(fig_cat, use_container_width=True)
    st.caption("Use this view to see which intervals, job types, or crafts have lower completion or higher planning bias.")

    with st.expander("Show category table"):
        cat_tmp = cat_summary.copy()
        cat_tmp['avg_completion'] = (cat_tmp['avg_completion'] * 100).round(1).astype(str) + '%'
        cat_tmp['avg_ontime'] = (cat_tmp['avg_ontime'] * 100).round(1).astype(str) + '%'
        cat_tmp['avg_hour_dev_pct'] = cat_tmp['avg_hour_dev_pct'].round(1)
        st.dataframe(cat_tmp, use_container_width=True, hide_index=True)

    st.divider()

    # Planning Bias
    st.subheader("📐 Planning Bias – Planned vs Actual Labor Hours")

    col_left, col_right = st.columns(2)

    with col_left:
        fig_hist = px.histogram(path2_filtered,
                                x='hour_deviation_pct',
                                nbins=40,
                                title="Distribution of Hour Deviation % (Actual vs Planned)",
                                labels={'hour_deviation_pct': 'Hour Deviation %'})
        
        fig_hist.add_vline(x=0, line_dash="dash")
        st.plotly_chart(fig_hist, use_container_width=True)
        st.caption("Bars to the right of 0 indicate overruns (actual > planned); bars to the left indicate underruns.")


    with col_right:
        fig_scatter = px.scatter(path2_filtered,
                                 x='AVG_PLANNED_HRS',
                                 y='AVG_ACTUAL_HRS',
                                 color='performance_tier',
                                 hover_data=['PMNUM', 'DEPT_NAME', 'INTERVAL'],
                                 title="Planned vs Actual Hours by PM",
                                 labels={'AVG_PLANNED_HRS': 'Planned Hours', 'AVG_ACTUAL_HRS': 'Actual Hours', 'performance_tier': 'Preformance Tier'})
        
        fig_scatter.add_shape(type="line",
                              x0=0, y0=0,
                              x1=path2_filtered['AVG_PLANNED_HRS'].max(),
                              y1=path2_filtered['AVG_PLANNED_HRS'].max(),
                              line=dict(dash="dash"))
        
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.caption("Points far from the dashed line highlight PMs with large planning bias (over- or under-estimated hours).")

    st.divider()

    # Failing vs Successful PM
    st.subheader("🧪 Failing vs Successful PM Characteristics")

    failing = path2_filtered[path2_filtered['completion_rate'] < fail_threshold]
    successful = path2_filtered[path2_filtered['completion_rate'] >= fail_threshold]

    comp_df = pd.DataFrame({'Group': ['Failing PMs', 'Successful PMs'],
                            'Avg Planned Hours': [failing['AVG_PLANNED_HRS'].mean(),
                                                  successful['AVG_PLANNED_HRS'].mean()],
                            'Avg Actual Hours': [failing['AVG_ACTUAL_HRS'].mean(),
                                                 successful['AVG_ACTUAL_HRS'].mean()],
                            'Avg Hour Deviation %': [failing['hour_deviation_pct'].mean(),
                                                     successful['hour_deviation_pct'].mean()],
                            'Avg Complexity Score': [failing['complexity_score'].mean(),
                                                     successful['complexity_score'].mean()],
                            'Count of PMs': [failing['PMNUM'].nunique(),
                                             successful['PMNUM'].nunique()]})

    st.dataframe(comp_df, use_container_width=True, hide_index=True)
    st.caption("Compare how complexity, planned vs actual hours, and deviation differ between failing and successful PMs.")

    st.divider()

    # Monthly trends in completion 
    st.subheader("🕒 Monthly Trends in Completion & On-Time Performance")

    monthly = (path2_filtered
        .groupby('due_month', observed=True)
        .agg(avg_completion=('completion_rate', 'mean'),
             avg_ontime=('on_time_rate', 'mean'),
             total_pm=('PMNUM', 'nunique'))
        .reset_index()
        .sort_values('due_month'))

    fig_trend = px.line(monthly,
                        x='due_month',
                        y=['avg_completion', 'avg_ontime'],
                        labels={'value': 'Rate', 'due_month': 'Month', 'variable': 'Metric'},
                        title="Monthly Completion vs On-Time Rate")

    fig_trend.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig_trend, use_container_width=True)
    st.caption("Use this view to spot seasonal patterns, ramp-up periods, or sustained improvements/declines in execution performance.")

    with st.expander("Show monthly table"):
        mtmp = monthly.copy()
        mtmp['avg_completion'] = (mtmp['avg_completion'] * 100).round(1).astype(str) + '%'
        mtmp['avg_ontime'] = (mtmp['avg_ontime'] * 100).round(1).astype(str) + '%'
        st.dataframe(mtmp, use_container_width=True, hide_index=True)

    st.divider()

    # Complexity vs completion 
    st.subheader("🧩 Complexity vs Completion Rate")

    fig_complex = px.scatter(path2_filtered,
                             x='complexity_score',
                             y='completion_rate',
                             color='performance_tier',
                             hover_data=['PMNUM', 'DEPT_NAME', 'INTERVAL', 'JOB_TYPE'],
                             labels={'complexity_score': 'Complexity Score',
                                     'completion_rate': 'Completion Rate',
                                     'performance_tier': 'Performance Tier'},
                             title="Completion vs Complexity")
    
    fig_complex.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig_complex, use_container_width=True)
    st.caption("Helps identify whether low-complexity PMs are failing (process issue) or failures are concentrated in high-complexity work (expected risk).")
    
    # Download filtered data
    csv_bytes = path2_filtered.to_csv(index=False).encode('utf-8')

    st.download_button(label="📥 Download filtered Path 2 data (CSV)",
                       data=csv_bytes,
                       file_name="path2_filtered.csv",
                       mime="text/csv")


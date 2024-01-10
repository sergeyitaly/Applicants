import warnings
import bar_chart_race as bcr
import pandas as pd
import tldextract

def create_chart_from_excel(input_file, output_file="position_chart_race.html"):
    # Suppress FutureWarning related to Series.fillna
    warnings.simplefilter(action='ignore', category=FutureWarning)

    # Suppress UserWarnings related to set_ticklabels
    warnings.simplefilter(action='ignore', category=UserWarning)

    # Read data from Excel file
    df = pd.read_excel(input_file)

    # Create a new column for extracted domain names
    df['Domain'] = df['Website'].apply(lambda x: f"{tldextract.extract(x).domain}.{tldextract.extract(x).suffix}")

    # Pivot the DataFrame for bar_chart_race
    df_pivot = df.pivot(index='Date', columns='Keyword', values='Amount')

    # Convert DataFrame values to numeric
    df_pivot = df_pivot.apply(pd.to_numeric, errors='coerce')

    # Create the bar chart race with color_bar set to None
    bcr.bar_chart_race(
        df=df_pivot,
        filename=output_file,
        title=f'Applicants per Position on {df["Domain"].iloc[0]} ({min(df["Date"])} - {max(df["Date"])})',
        orientation='h',
        sort='desc',  # Sorting order, set to 'desc' for descending order
        n_bars=5,    # Number of bars to show in the animation
        fixed_order=False,  # Allow bars to change order
        steps_per_period=20,  # Number of steps between each period
        fixed_max=False,
        bar_texttemplate="{x:,.2f}",
        tick_template="{x:,.2f}",
        shared_fontdict=None, 
        filter_column_colors=True,
        scale='linear', 
        fig=None, 
        writer='html', 
        period_summary_func= lambda v, r : {'x' :.89, 'y' : .03, 's' : f'Made by @SerhiiVoinolovych', 'ha' :'right', 'size' :6}
    )

    print(f"Chart saved to {output_file}")

input_file = 'EXPERIENCE.xlsx'
output_file = 'position_chart_race_experience.html'
create_chart_from_excel(input_file, output_file)

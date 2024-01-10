from collections import defaultdict
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import warnings, re, json
from tqdm import tqdm
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
import pandas as pd
from datetime import datetime, timedelta
import tldextract
# Suppress warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
total_quantity_all_positions = defaultdict(int)  # Declare the variable here

def get_archived_html(website_url, timestamp, max_retries=3):
    for attempt in range(max_retries):
        try:
            print(f"Retrieving data for {website_url} at {timestamp}...")
            wayback_url = f"http://web.archive.org/web/{timestamp}/{website_url}"
            response = requests.get(wayback_url, timeout=10)
            response.raise_for_status()
            print("Data retrieved successfully.")
            return response.text

        except HTTPError as errh:
            if response.status_code == 404:
                print(f"Error 404: {wayback_url} not found.")
            else:
                print(f"HTTP Error: {errh}")

        except ConnectionError as errc:
            warnings.warn(f"Error Connecting: {errc}", RuntimeWarning)

        except Timeout as errt:
            print(f"Timeout Error: {errt}")

        except RequestException as err:
            print(f"An error occurred: {err}")

        print(f"Retrying... (Attempt {attempt + 1}/{max_retries})")

    print(f"Max retries ({max_retries}) exceeded. Unable to retrieve data.")
    return None

def analyze_position_amount(website_url, keywords, start_date, end_date):

    # Mapping between Ukrainian and English keywords
    keyword_mapping = {
        "Менеджер": "Manager",
        "Розробник": "Developer",
        "Разработчик": "Developer",
        "Аналітик" : "Analyst",
        "Аналитик" : "Analyst",
        "Дизайнер" : "Designer",    
        "Тестувальник" : "QA",
        "Тестировщик" : "QA",
        "Tester" : "QA",
        "Рекрутер" : "Recruiter",
        "Молодший" : "Junior",
        "Младший" : "Junior",
        "Старший" :"Senior",
        "Головний" :"Chief",
        "Главный" :"Chief",
        "Керівник" :"Lead",
        "Руководитель" :"Lead",
        "Інженер" :"Engineer",
        "Инженер" :"Engineer",
        "Інтерн" :"Intern",
        "Интерн" :"Intern",
        
        # Add more mappings as needed
    }

    # Combine data for mapped keywords
    combined_keywords = set()
    for keyword_ua in keywords:
        combined_keywords.add(keyword_mapping.get(keyword_ua, keyword_ua))

    position_amount_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    total_positions_all_data = defaultdict(lambda: defaultdict(int))
    total_positions_all_keywords_data = defaultdict(lambda: defaultdict(int))
    total_quantity_all_positions = defaultdict(int)
    total_iterations = (end_date - start_date).days + 1
    current_date = start_date

    with tqdm(total=total_iterations, desc=f"Analyzing {website_url}", unit="day") as pbar:
        while current_date <= end_date:
            positions = []  # Initialize positions outside the try block
            total_applications_count = 0  # New variable for all applications
            total_positions_all = 0  # New variable for all positions
            positions_with_keyword = set()
            keyword_applications = {}
            amount_positions_keywords = {}
            for page in range(10):                
                current_url = f'{website_url}' if page == 0 else f'{website_url}?page={page+1}'
                timestamp = current_date.strftime("%Y%m%d")
                archived_html = get_archived_html(current_url, timestamp)
                if archived_html:
                    try:

                        timestamp = current_date.strftime("%Y%m%d")
                        soup = BeautifulSoup(archived_html, 'html.parser')
                        if 'work.ua' in website_url:
                                positions = soup.find_all('h2', class_='')

                        elif 'djinni.co' in current_url:
                            if current_date >= datetime(2023, 9, 1):
                                job_items = soup.find_all('li', class_='list-jobs__item job-list__item')
                                for job_item in job_items:
                                    title_container = job_item.find('a', class_='h3 job-list-item__link')
                                    position_title = title_container.get_text(strip=True).lower()
                                    positions.append(position_title)

                                       # Collect applications
                                    applications_span = job_item.find_all('span', class_='mr-2', title=re.compile(r'\d+\s+(applications?|views?)'))
                                    for span in applications_span:
                                        applications_text = span.get_text(strip=True)
                                        applications_match = re.search(r'(\d+)\s+applications?', span.get('title', ''))
                                        if applications_match:
                                            applications_count = int(applications_match.group(1))
                                            if applications_count > 0:
                                                total_applications_count += applications_count                                                      
                                            for keyword in keywords:
                                                if re.search(r'\b{}\b'.format(re.escape(keyword)), position_title, flags=re.IGNORECASE):
                                                    positions_with_keyword.update({position_title})
                                                    amount_positions_keywords[keyword] = amount_positions_keywords.get(keyword, 0) + 1  
                                                    if applications_count > 0:
                                                        keyword_applications[keyword] = keyword_applications.get(keyword, 0) + applications_count
                                                   
                            elif (current_date >= datetime(2023, 8, 17)) and (current_date < datetime(2023, 9, 1)):
                                job_items = soup.find_all('li', class_='list-jobs__item job-list__item')
                                for job_item in job_items:
                                    title_container = job_item.find('div', class_='job-list-item__title mb-1 position-relative d-lg-block d-flex')
                                    position_title = title_container.get_text(strip=True).lower()
                                    positions.append(position_title)
                                    # Collect applications
                                    applications_span = job_item.find_all('span', class_='mr-2', title=re.compile(r'\d+\s+(applications?|views?)'))
                                    for span in applications_span:
                                        applications_text = span.get_text(strip=True)
                                        applications_match = re.search(r'(\d+)\s+applications?', span.get('title', ''))
                                        if applications_match:
                                            applications_count = int(applications_match.group(1))
                                            if applications_count > 0:
                                                total_applications_count += applications_count                                                      
                                            for keyword in keywords:
                                                if re.search(r'\b{}\b'.format(re.escape(keyword)), position_title, flags=re.IGNORECASE):
                                                    positions_with_keyword.update({position_title})
                                                    amount_positions_keywords[keyword] = amount_positions_keywords.get(keyword, 0) + 1  
                                                    if applications_count > 0:
                                                        keyword_applications[keyword] = keyword_applications.get(keyword, 0) + applications_count

                            elif (current_date >= datetime(2023, 1, 13)) and (current_date < datetime(2023, 8, 17)):
                                job_items = soup.find_all('li', class_='list-jobs__item list__item')
                                for job_item in job_items:
                                    title_container = job_item.find('div', class_='list-jobs__title list__title order-1')
                                    position_title = title_container.get_text(strip=True).lower()
                                    positions.append(position_title)

                                        # Collect applications
                                    applications_span = job_item.find_all('span', class_='ml-2', title=re.compile(r'\d+\s+(applications?|views?)'))
                                    for span in applications_span:
                                        applications_text = span.get_text(strip=True)
                                        applications_match = re.search(r'(\d+)\s+applications?', span.get('title', ''))
                                        if applications_match:
                                            applications_count = int(applications_match.group(1))
                                            if applications_count > 0:
                                                total_applications_count += applications_count                                                      
                                            for keyword in keywords:
                                                if re.search(r'\b{}\b'.format(re.escape(keyword)), position_title, flags=re.IGNORECASE):
                                                    positions_with_keyword.update({position_title})
                                                    amount_positions_keywords[keyword] = amount_positions_keywords.get(keyword, 0) + 1  
                                                    if applications_count > 0:
                                                        keyword_applications[keyword] = keyword_applications.get(keyword, 0) + applications_count

                            elif (current_date < datetime(2023, 1, 13)):
                                job_items = soup.find_all('li', class_='list-jobs__item list__item')                                
                                for job_item in job_items:
                                    title_container = job_item.find('div', class_='list-jobs__title list__title order-1')
                                    position_title = title_container.find('span').get_text(strip=True).lower()
                                    positions.append(position_title)
                                        # Collect applications
                                    applications_span = job_item.find('div', class_='d-flex align-items-md-center flex-column flex-sm-row').find_all('span', class_='job-card--meta-info-item')
                                    for span in applications_span:
                                        applications_text = span.get_text(strip=True)
                                        applications_match = re.search(r'people_alt\D*(\d+)', applications_text)
                                        if applications_match:
                                            applications_count = int(applications_match.group(1))
                                            if applications_count > 0:
                                                total_applications_count += applications_count                                                      
                                            for keyword in keywords:
                                                if re.search(r'\b{}\b'.format(re.escape(keyword)), position_title, flags=re.IGNORECASE):
                                                    positions_with_keyword.update({position_title})
                                                    amount_positions_keywords[keyword] = amount_positions_keywords.get(keyword, 0) + 1  
                                                    if applications_count > 0:
                                                        keyword_applications[keyword] = keyword_applications.get(keyword, 0) + applications_count

                            elif 'linkedin.com' in website_url:
                                job_listings = soup.find_all("div", class_="base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card")
                                for job in job_listings:
                                    title_container = job.find("h3", class_="base-search-card__title")
                                    if title_container:
                                        job_title = title_container.text.strip()
                                        if job_title:
                                            positions.append(job_title)
                            else:
                                raise ValueError(f"Unsupported website: {current_url}")

                            total_positions_all_keywords = len(positions_with_keyword)
                            total_positions_all = len(positions)
                            total_quantity_all_positions[(current_date.year, current_date.month, timestamp)] = total_positions_all

                            for keyword in combined_keywords:
                                # Check if the keyword has entries in the dictionaries
                                if keyword in amount_positions_keywords and keyword in keyword_applications:
                                    # Calculate amount for the keyword and all positions
                                    amount = keyword_applications[keyword] / amount_positions_keywords[keyword] if amount_positions_keywords[keyword] > 0 else 0
                                else:
                                    amount = 0  # Set a default value if the keyword is not present in the dictionaries

                                amount_all_positions = total_applications_count / total_positions_all if total_positions_all > 0 else 0
                                position_amount_data[website_url][keyword][(current_date.year, current_date.month, timestamp)] = {
                                    'amount': amount,
                                    'amount_all_positions': amount_all_positions,
                                    'quantity': keyword_applications.get(keyword, 0),  # Use get() to handle missing keys
                                    'total_positions_all_keywords': total_positions_all_keywords,
                                    'total_quantity_all_positions': total_quantity_all_positions[(current_date.year, current_date.month, timestamp)],
                                }
                            
                    except Exception as e:
                        print(f"Error processing {current_url} at {timestamp}: {str(e)}")
                
            current_date += timedelta(days=1)
            pbar.update(1)

        position_amount_data['total_positions_all'] = total_positions_all_data
        position_amount_data['total_positions_all_keywords'] = total_positions_all_keywords_data

    return position_amount_data


def create_chart(position_amount_data, start_date, end_date, output_file="position_chart.html"):
    fig = go.Figure()
    max_percentage = 0
    total_days = 0
    all_dates_set = {date[2] for website_data in position_amount_data.values() for keyword_data in website_data.values() for date, values in keyword_data.items() if isinstance(values, dict) and values.get('quantity', 0) > 0}
    all_dates = sorted(list(all_dates_set))
    legend_entries = set()

    # Create a dictionary to store aggregated data for each keyword on each date
    aggregated_data = defaultdict(lambda: defaultdict(float))
    all_amounts = []
    total_amount_all_positions = defaultdict(float)  # New variable for total amount across all positions

    for website_url, website_data in position_amount_data.items():
        total_positions_all_keywords = 0
        total_quantity_all_positions = defaultdict(int)

        for keyword, data in website_data.items():
            total_positions_all = total_quantity = total_amount = keyword_days = 0
            date_data_dict = defaultdict(
                lambda: {'quantity': 0, 'amount': 0, 'total_positions_all_keywords': 0,
                         'total_quantity_all_positions': 0, 'total_positions_all': 0})

            for key, values in data.items():
                if isinstance(values, int) and values > 0:
                    total_quantity += values
                    total_positions_all += values
                elif isinstance(values, dict) and values.get('quantity', 0) > 0:
                    total_quantity += values.get('quantity', 0)
                    total_positions_all += values.get('total_positions_all', 0)

                    if isinstance(values, dict):
                        total_positions_all_keywords = max(total_positions_all_keywords,
                                                            values.get('total_positions_all_keywords', 0))
                        total_quantity_all_positions[key[2]] = values.get('total_quantity_all_positions', 0) + (values.get('total_positions_all_keywords', 0) - values.get('quantity', 0))
                        total_days += 1
                        if values['amount'] > 0:
                            keyword_days += 1
                            total_amount += values['amount']
                            total_amount_all_positions[key[2]] += values['amount']  # Accumulate total amount for each date

                        all_amounts.append(values['amount'])

                        date_data_dict[key[2]] = {
                            'current': values.get('quantity', 0),
                            'total_quantity': total_quantity,
                            'amount': values['amount'],
                            'total_positions_all_keywords': values.get('total_positions_all_keywords', 0),
                            'total_quantity_all_positions': values.get('total_quantity_all_positions', 0),
                            'total_positions_all': values.get('total_positions_all', 0)
                        }
            max_amount = max(all_amounts, default=0)

            average_amount = total_amount / keyword_days if keyword_days > 0 else 0
            sorted_data = sorted(date_data_dict.items(), key=lambda item: item[0])

            if sorted_data:
                for date, values in sorted_data:
                    aggregated_data[keyword][date] += values['amount']
                # Create x and y values for the trace
                x_values_dates, y_values_amount = zip(*[(date, aggregated_data[keyword][date]) for date, _ in sorted_data])
                hover_text = [
                    f'  Date: {date}<br>'
                    f'  Current Quantity:{values["current"]}<br>'
                    f'  Current Amount: {values["amount"]:.2f}<br>'
                    f'  Total Quantity: {values["total_quantity"]}<br>'
                    f'  Total Keywords: {values["total_positions_all_keywords"]}<br>'
                    f'  All Positions: {values["total_quantity_all_positions"]}<br>'
                    for date, values in sorted_data
                ]

                extracted_info = tldextract.extract(website_url)
                domain_name = f"{extracted_info.domain}.{extracted_info.suffix}"
                legend_entry = (f"{keyword}-{average_amount:.2f}%<br>{domain_name}", average_amount)
                if legend_entry not in legend_entries:
                    trace_amount = go.Scatter(
                        x=x_values_dates,
                        y=y_values_amount,
                        stackgroup='one',
                        name=f"{keyword}-{average_amount:.2f}<br>{domain_name}",
                        hovertemplate=hover_text,
                        text=x_values_dates,
                        connectgaps=False,
                        mode='markers+lines',  # Set mode to 'markers+lines' to show markers
                        marker=dict(size=3),  # Adjust the marker size here (e.g., size=5)
                    )

                    fig.add_trace(trace_amount)
                    legend_entries.add(legend_entry)

    all_dates = sorted(all_dates)

    if all_dates:
        x_values_all_positions, y_values_amount_all_positions = zip(*[(date, total_amount_all_positions.get(date, 0)) for date in all_dates])
    else:
        # Provide default values or handle the case when there are no dates
        x_values_all_positions, y_values_amount_all_positions = [], []

    hover_text_all_positions = [
        f'  Date: {date}<br>'
        f'  Total Amount All Positions: {total_amount_all_positions[date]:.2f}<br>'
        for date in x_values_all_positions
    ]
    
    extracted_info = tldextract.extract(website_url)
    domain_name = f"{extracted_info.domain}.{extracted_info.suffix}"

    trace_amount_all_positions = go.Scatter(
        x=x_values_all_positions,
        y=y_values_amount_all_positions,
        stackgroup='one',
        name=f"All Positions<br>{domain_name}",
        hovertemplate=hover_text_all_positions,
        text=x_values_all_positions,
        connectgaps=False,
        mode='markers+lines',  # Set mode to 'markers+lines' to show markers
        marker=dict(size=3),  # Adjust the marker size here (e.g., size=5)
    )

    fig.add_trace(trace_amount_all_positions)  # Add the new trace for amount_all_positions

    fig.update_layout(
        legend=dict(
            title='Key Words',
            traceorder='reversed',
            itemsizing='constant',
            tracegroupgap=0,
            borderwidth=0,
        ),
        title=f'Applicants per Position ({start_date.strftime("%b %d, %Y")} - {end_date.strftime("%b %d, %Y")})',
        yaxis_title='',
        template='plotly_dark',
        xaxis=dict(type='category', categoryorder='array', categoryarray=sorted(all_dates)),
        yaxis_range=[0, max_amount+2],
    )

    fig.write_html(output_file)
    print(f"Chart saved to {output_file}")

def export_to_excel(position_percentage_data, output_file="position_data.xlsx"):
    result_data = defaultdict(list)

    for website_url, keyword_data in position_percentage_data.items():
        for keyword, data in keyword_data.items():
            for key, values in data.items():
                if isinstance(values, dict):
                    timestamp = key[2]
                    timestamp_str = str(timestamp)
                    date_info = datetime.strptime(timestamp_str, "%Y%m%d")  # Correct the timestamp format
                    result_data['Website'].append(website_url)
                    result_data['Keyword'].append(keyword)
                    result_data['Quantity'].append(values.get('quantity', 0))
                    result_data['Amount'].append(values.get('amount', 0))
                    result_data['All_Applicants'].append(values.get('amount_all_positions', 0))
                    result_data['Total_Positions_All_Keywords'].append(values.get('total_positions_all_keywords', 0))
                    result_data['Total_Quantity_All_Positions'].append(values.get('total_quantity_all_positions', 0))
                    result_data['Date'].append(date_info.strftime('%Y-%m-%d'))  # Adding the formatted date

    df = pd.DataFrame(result_data)
    df.to_excel(output_file, index=False)
    print(f"Data exported to {output_file}")

def main():
    keywordsua=["Analyst", "Developer", "DevOps", "Manager", "Cloud", "QA", "Lead", "HR","Recruiter", "Рекрутер",
                "Talent", "Designer", "Дизайнер", "Аналітик","Аналитик", "Розробник","Разработчик", 
                "Менеджер", "Тестувальник", "Тестировщик", "Tester", "Керівник", "Руководитель", "Engineer", "Інженер","Инженер",
                "Chief","Senior", "Middle", "Junior", "Intern", "Internship", "Головний", "Главный","Молодший",
                "Младший","Старший","Інтерн", "Интерн"]

    websites = {
       # 'https://work.ua/jobs-it/': keywordsua,
        'https://djinni.co/jobs/': keywordsua
       #'https://www.linkedin.com/jobs/search/?keywords={job_title}&location={Ukraine}': keywordsua
    }
    #before 22,10,15 djjini.co did not put down amount of applications 
    start_date = datetime(2023, 9, 2)
    end_date = datetime(2024, 1, 9)

    position_amount_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for website_url, keywords in websites.items():
        print(f"\nAnalyzing {website_url}...")
        position_amount_data.update(analyze_position_amount(website_url, keywords, start_date, end_date))

    create_chart(position_amount_data, start_date, end_date, output_file="combined_position_chart.html")
    export_to_excel(position_amount_data, output_file="combined_position_data.xlsx")

if __name__ == "__main__":
    main()

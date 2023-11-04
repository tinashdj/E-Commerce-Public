import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Helper functions needed to prepare various dataframes

def create_total_order(ecommerce):
    total_order = (ecommerce['order_id'].count())

    return total_order

def create_total_sales(ecommerce):
    total_sales = round(ecommerce['price'].sum(), 2)
    
    return total_sales


def create_mean_sales(ecommerce):
    mean_sales = round(ecommerce['price'].mean(), 2)   # Rounds to 2 decimal places
    
    return mean_sales

def create_by_product(ecommerce):
    ecommerce_product = ecommerce.groupby(by='product_category_name').order_id.nunique().sort_values(ascending=False).reset_index().head(10)

    return ecommerce_product


def create_by_city(ecommerce):
    ecommerce_city = ecommerce.groupby(by='customer_city').order_id.nunique().sort_values(ascending=False).reset_index().head(10)

    return ecommerce_city

def create_order_month(ecommerce):
    order_by_month = ecommerce.groupby(by='purchase_month_year').order_id.nunique().reset_index()
    order_by_month = order_by_month.sort_values('purchase_month_year')

    return order_by_month

def create_revenue_month(ecommerce):
    revenue_by_month = ecommerce.groupby('purchase_month_year').price.sum().reset_index()
    revenue_by_month = revenue_by_month.sort_values('purchase_month_year')

    return revenue_by_month
    
def create_rfm(ecommerce):
    rfm = ecommerce.groupby(by='customer_id', as_index=False).agg({
    'order_purchase_timestamp': 'max', #calculates the maximum (most recent) purchase
    'order_id': 'count', #calculates the count of orders
    'price': 'sum' #calculates the sum of prices
    })

    rfm.columns = ['customer_id', 'max_order_timestamp', 'frequency', 'monetary']
 
    rfm['max_order_timestamp'] = rfm['max_order_timestamp'].dt.date
    recent_date = ecommerce['order_purchase_timestamp'].dt.date.max()
    rfm['recency'] = rfm['max_order_timestamp'].apply(lambda x: (recent_date - x).days)
    rfm.drop(columns='max_order_timestamp', inplace=True)
    
    return rfm


# Load cleaned data

df = pd.read_csv('https://raw.githubusercontent.com/tinashdj/E-Commerce-Public/main/dashboard/ecommerce.csv')

datetime_columns = ['order_purchase_timestamp', 'purchase_month_year']
df.sort_values(by='order_purchase_timestamp', inplace=True)
df.reset_index(inplace=True)

for column in datetime_columns:
    df[column] = pd.to_datetime(df[column])

    
st.set_page_config(page_title="E-Commerce Public Dashboard",
                   page_icon="bar_chart:",
                   layout="wide")
    
# Filter data

min_date = df['order_purchase_timestamp'].min()
max_date = df['order_purchase_timestamp'].max()

with st.sidebar:
    
    # Retrieves start_date & end_date from date_input
    start_date, end_date = st.date_input(
        label='Order Time',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = df[(df['order_purchase_timestamp'] >= str(start_date)) & 
             (df['order_purchase_timestamp'] <= str(end_date))]
    

# Preparing dataframe
total_order = create_total_order(main_df)
total_sales = create_total_sales(main_df)
mean_sales = create_mean_sales(main_df)
ecommerce_product = create_by_product(main_df)
ecommerce_city = create_by_city(main_df)
order_by_month = create_order_month(main_df)
revenue_by_month = create_revenue_month(main_df)
rfm = create_rfm(main_df)

# Main page

st.header('E-Commerce Public Dashboard :bar_chart:')

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('### Total Order:')
    st.subheader(total_order)
    
with col2:
     st.markdown('### Total Sales:')
     total_sales_currency = format_currency(total_sales, 'BRL', locale='pt_BR')
     st.subheader(total_sales_currency)
    
with col3:
     st.markdown('### Average Sales:')
     mean_sales_currency = format_currency(mean_sales, 'BRL', locale='pt_BR')
     st.subheader( mean_sales_currency)
    
st.markdown("---")


# Most Order by Product and City

col1, col2 = st.columns(2)

with col1:
    st.markdown('### Top 10 Products With the Most Orders')
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.barh(ecommerce_product['product_category_name'], ecommerce_product['order_id'])
    plt.xlabel('Total Order')
    plt.ylabel('Product Category')
    plt.title('Top 10 Products That Have The Most Orders')
    plt.gca().invert_yaxis()
    st.pyplot(fig)
    
with col2:
    st.markdown('### Top 10 Cities With the Most Orders')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    plt.barh(ecommerce_city['customer_city'], ecommerce_city['order_id'])
    plt.xlabel('Total Order')
    plt.ylabel('City Name')
    plt.title('10 Cities With The Most Orders')
    plt.gca().invert_yaxis()
    st.pyplot(fig)
    

# Total Order and Sales by Month

col1, col2 = st.columns(2)

with col1:
    st.markdown('### Total Order per Month')
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    plt.plot(order_by_month['purchase_month_year'], order_by_month['order_id'], marker='o')
    plt.xlabel('Order Date')
    plt.ylabel('Total Order')
    plt.title('Total Order per Month (2017-2018)')
    plt.xticks(rotation=45)
    st.pyplot(fig1)
    
with col2:
    st.markdown('### Total Revenue per Month')
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    plt.plot(revenue_by_month['purchase_month_year'], revenue_by_month['price'], marker='o')
    plt.xlabel('Order Date')
    plt.ylabel('Total Revenue')
    plt.title('Total Revenue per Month (2017-2018)')
    plt.xticks(rotation=45)
    st.pyplot(fig2)
    
    
# Best Customer Based on RFM Parameters
st.subheader('Best Customer Based on RFM Parameters')

f, axes = plt.subplots(3, 1, figsize=(15, 12))

# Plotting histograms
sns.histplot(rfm['recency'], bins=50, kde=True, ax=axes[0])
sns.histplot(rfm['frequency'], bins=50, kde=True, ax=axes[1])
sns.histplot(rfm['monetary'], bins=50, kde=True, ax=axes[2])

# Set titles
axes[0].set_title('Recency Distribution')
axes[1].set_title('Frequency Distribution')
axes[2].set_title('Monetary Distribution')

# Adjust space between subplots
plt.subplots_adjust(hspace=0.4)

st.pyplot(f)

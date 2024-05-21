ETL and Data Analysis with Python and SQL

This project shed more light on the importance of loading data with APIS and python

Data is loaded with Kaggle API, cleaned, and preprocessed with Python. The clean data is loaded into a database for storage and further analysis with SQL

![alt text](<data analysis.jpg>)

The first part of this project (analysis.py) is sub-divided into:
- Loading of Data with Kaggle API with Python
- Clean the data by:
  - Replacing missing values
  - Convert the columns into lowercase and replace whitespaces with underscores
  - Perform feature engineering by adding more features and dropping insignificant features
  - Change data types of some of the features
- Load the cleaned data into MS SQL Server

- Query the database and answer the following questions:
   - Question 1: Find the top 10 highest revenue-generating products
   - Question 2: find the top 5 highest-selling products per region.
   - Question 3: Find month-over-month growth comparison  for 2022 and 2023 sales. For example, Jan 2022 vs Jan 2023. Compute the difference
   - Question 4: For each category, which month had the highest sales.
   - Question 5: Which sub-category had the highest growth by profit in 2023 compared to 2022

create database  retail;

use retail;

create table orders( order_id int primary key,
					 order_date date,
					 ship_mode varchar(255),
					 segment varchar(255),
					 country varchar(255),
					 city varchar(255),
					 state varchar(255),
					 postal_code int,
					 region varchar(255),
					 category varchar(255),
					 sub_category varchar(255),
					 product_id varchar(255),
					 quantity int,
					 discount float,
					 sales_price float,
					 profit float);

select * from orders;
---Question 1: Find the top 10 higest revenue generating products

select TOP 10 product_id, category,SUM(sales_price) total_sales
from orders
group by product_id, category
order by  total_sales desc;



--- Question 2: find top 5 higest selling products per region


with top_product as (select product_id, region, SUM(sales_price) total_sales,
DENSE_RANK() OVER(PARTITION BY region order by SUM(sales_price) desc) ranked
from orders
group by product_id, region)
select * from top_product
where ranked<=5 ;


--- Question 3: Find month over month growth comparison  for 2022 and 2023 sales. For example, Jan 2022 vs Jan 2023. Compute the difference

select * from orders;

with cte as 
(select YEAR(order_date) order_year, month(order_date) order_month,
		round(SUM(sales_price),2) as total_sales	
from orders
group by YEAR(order_date), month(order_date))

select order_month,
SUM(case when order_year = 2022 then total_sales else 0 end) as sale_2022,
SUM(case when order_year = 2023 then total_sales else 0 end) as sales_2023,
round((SUM(case when order_year = 2023 then total_sales else 0 end)-SUM(case when order_year = 2022 then total_sales else 0 end)),2) as growth_or_loss
from cte
group by order_month
order by order_month;

--- Question 4" For each category, which month had the highest sales
with ranked_cat as (select format(order_date,'yyyyMM') order_year_month, category, SUM(sales_price) total_sales,
RANK() OVER(PARTITION BY category ORDER BY SUM(sales_price) desc) as ranked_category
from orders
group by format(order_date,'yyyyMM'), category)

select order_year_month, category, ROUND(total_sales,2) total_sales, ranked_category from ranked_cat
where ranked_category<=1
order by total_sales desc

---Question 5: Which sub-category had highest growth by profit in 2023 compared to 2022



with cte as 
(select YEAR(order_date) order_year,sub_category,
		round(SUM(sales_price),2) as total_sales,
		round(SUM(profit),2) as total_profit
from orders
group by sub_category, YEAR(order_date)),

cte2 as(

select sub_category,
SUM(case when order_year = 2022 then total_profit else 0 end) as profit_2022,
SUM(case when order_year = 2023 then total_profit else 0 end) as profit_2023
from cte
group by sub_category)

select *, round((profit_2023-profit_2022)*100/profit_2022,2) growth_percent
from cte2
order by (profit_2023-profit_2022)*100/profit_2022 desc

---Question 5: Which sub-category had highest growth by sales in 2023 compared to 2022



with cte as 
(select YEAR(order_date) order_year,sub_category,
		round(SUM(sales_price),2) as total_sales
from orders
group by YEAR(order_date),sub_category)

select sub_category,
SUM(case when order_year = 2022 then total_sales else 0 end) as sales_2022,
SUM(case when order_year = 2023 then total_sales else 0 end) as sales_2023,
round((SUM(case when order_year = 2023 then total_sales else 0 end)-SUM(case when order_year = 2022 then total_sales else 0 end)),2) as growth_or_loss

from cte
group by sub_category
order by growth_or_loss desc
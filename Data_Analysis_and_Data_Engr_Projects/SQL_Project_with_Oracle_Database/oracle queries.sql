QUERYING ORACLE DATABASE TO EXTRACT INSIGHTS FROM DATA




--Question 1: compute avg_sales for each month
SELECT trunc(SALES_DATE,'MM') sales_month, ROUND(AVG(SALES_AMOUNT)) avg_sales  
from sales
group by trunc(SALES_DATE,'MM');


--Question 2: compute total_sales for each month by each salesperson and determine top salesperson for each month
with cte as (SELECT TRUNC(s.SALES_DATE,'MM') sales_month, sp.first_name salesperson,
        SUM(s.SALES_AMOUNT) as total_sales,
        RANK() OVER (PARTITION BY TRUNC(s.SALES_DATE,'MM') order by SUM(s.SALES_AMOUNT)) as rank_number
from SALES s
JOIN SALESPERSON sp
ON s.salesperson_id = sp.salesperson_id
group by TRUNC(s.SALES_DATE,'MM'),sp.first_name)
select * from cte 
where rank_number = 1;


--Add salary column to Salesperson table and and update salary amount for each salesperson

ALTER TABLE SALESPERSON
ADD salary NUMBER(10,2);

UPDATE SALESPERSON
SET salary = 80000
WHERE  first_name = 'Greg';

select * from SALESPERSON;

--Obtain the data of supervisors who are earning more than managers.
-- This is a bit tricky. You join the table on itself. This is called a self join.
-- You join the table on the job_title column. You also add a condition to check if the supervisor's salary is greater than the manager's salary.

SELECT supervisor.salesperson_id, supervisor.first_name supervisor_name, supervisor.salary AS supervisor_salary, manager.first_name manager_name,manager.salary AS manager_salary   
FROM 
    SALESPERSON supervisor
JOIN 
    SALESPERSON manager ON supervisor.job_title = 'Supervisor' 
                        AND manager.job_title = 'Manager'
WHERE 
    supervisor.salary > manager.salary;


select * from SALESPERSON supervisor;

-- Find out salesperon and manager Hierarchy
--Here we use a pseudo column called LEVEL to find out the hierarchy.

select first_name, job_title, manager, level
from salesperson;
connect by prior first_name=manager --first_name and manager are the child and parent relationship, where manager is the parent
start with manager is null
order by 4;

--To create the hierarchy tree
CONCAT (LPAD (' ',level*3-3),first_name) as first_name
from salesperson
connect by prior first_name=manager
start with manager is null
order siblings by salesperson.first_name desc; --in this case, we use order siblings by to order the siblings in descending order.

-- To obtain the total sales for each salesperson under Raj (the salespersons under Raj are Bob and Greb with Bob having Sara and 
-- Rehman reporting to him and Anil reports to Greg

-- First we see the hierarchy for people under Raj

SELECT CONCAT (LPAD (' ',level*3-3),first_name) as first_name
from salesperson
connect by prior first_name=manager
start with manager = 'Raj'
order siblings by salesperson.first_name desc;

--Then we compute the total sales for all the salesperson under Raj

with cte as (select salesperson_id,first_name, job_title, manager, level, connect_by_root first_name top_boss
from salesperson 
connect by prior first_name = manager
start with manager = 'Raj')
select c.top_boss,SUM(s.sales_amount) total_sales
from cte c
join sales s
on
s.salesperson_id = c.salesperson_id
GROUP BY c.top_boss;

--To show the hierarchy on a column level, we use sys_connect_by_path
select first_name, manager, level, sys_connect_by_path(first_name,'/') as heir1
from salesperson
connect by prior first_name=manager
start with manager='Jeff';

--To have the sum of sales display for each sales month
select trunc(s.sales_date,'mon') sales_month,p.product_name,
sum(sales_amount) total_sales
from sales s
join product p
on p.product_id = s.product_id
Group by rollup(trunc(s.sales_date,'mon'), p.product_name) --"here we use group by rollup instead of group by alone to add the data fro each month ans display the total.
order by 1;

-- monthly sales over time (LAG: Previous month, LEAD : Next month
select trunc(sales_date,'MM') sales_month, 
        SUM(sales_amount),
        LAG(SUM(sales_amount),1) OVER(ORDER BY trunc(sales_date,'MM')) previous_month_sales 
        from sales
        group by trunc(sales_date,'MM');
    
--Next month

select trunc(sales_date,'MM') sales_month, 
        SUM(sales_amount),
        LEAD(SUM(sales_amount),1) OVER(ORDER BY trunc(sales_date,'MM')) previous_month_sales 
        from sales
        group by trunc(sales_date,'MM');

--MOM % growth
-- To compute the MOM growth, we use the LAG function to get the previous month sales and then compute the percentage growth.

with cte as (
select trunc(sales_date,'MM') sales_month, 
        SUM(sales_amount) total_sales,
        LAG(SUM(sales_amount),1) OVER(ORDER BY trunc(sales_date,'MM')) previous_month_sales
        FROM sales
        group by trunc(sales_date,'MM'))
        select total_sales, previous_month_sales, 
       ROUND(((total_sales-previous_month_sales)/previous_month_sales),2) as percent_monthly_sales_growth
from cte;

-- YOY growth
-- To compute the YOY growth, you replace 1 with 12 in the LAG function to get the sales for the same month in the previous year.

-- To determine the sumtotal of product sold per month, we use rollup
select trunc(s.sales_date,'MM') sales_month,
        p.product_name,
        SUM(s.sales_amount) total_sales
FROM sales s
JOIN Product p
ON s.product_id = p.product_id
group by rollup (trunc(s.sales_date,"MM"),p.product_name)

--To compute the sum total of product sold per month ans the sum total of each product sold, we use cube instead of rollup
select trunc(s.sales_date,'MM') sales_month,
        p.product_name,
        SUM(s.sales_amount) total_sales
FROM sales s
JOIN Product p
ON s.product_id = p.product_id
group by cube (trunc(s.sales_date,"MM"),p.product_name)

--To determine total amount of each product bought per month and the percentage growth of each product bought per month

with cte as (
select trunc(sales_date,'MM') sales_month, 
        p.product_name,
        SUM(sales_amount) total_sales,
        LAG(SUM(sales_amount),1) OVER(PARTITION BY p.product_name ORDER BY trunc(sales_date,'MM')) previous_year_sales
        from sales s
        join product p
        on s.product_id = p.product_id
        group by trunc(sales_date,'MM'), p.product_name)
        select sales_month, product_name, total_sales, previous_year_sales,
        ROUND(((total_sales-previous_year_sales)/previous_year_sales),2) as percent_yearly_sales_growth
        from cte;

--Determine the top 3 salesperson for each month
--To determine the top 3 salesperson for each month, we use the RANKor DENSE_RANK function to rank the salesperson based on the total sales for each month.
--Determine the top 3 salesperson per month
with cte as (
select trunc(s.sales_date,'MM')sales_month, sp.first_name salesperson,SUM(s.sales_amount) total_sales,
DENSE_RANK() OVER(PARTITION BY trunc(s.sales_date,'MM') ORDER BY SUM(s.sales_amount) desc) rank_number
from sales s
join salesperson sp
on sp.salesperson_id = s.salesperson_id
group by trunc(s.sales_date,'MM'), sp.first_name
order by sales_month,rank_number)

select * from cte 
WHERE rank_number <= 3;

--USE window functions to perform advanced analytical tasks, such as calculating moving averages or detecting outliers.
--To compute the moving average of sales for each month, we use the AVG function with the OVER clause to compute the average of the sales for the last three months.
-- in the query below, we compute the total sales and the moving average of 1 preceding row and the current row for each month.
select trunc(sales_date,'MM') sales_month, 
        SUM(sales_amount) total_sales,
        ROUND(AVG(SUM(sales_amount)) OVER(ORDER BY trunc(sales_date,'MM') ROWS BETWEEN 1 PRECEDING AND CURRENT ROW),2) moving_avg_sales
        from sales
        group by trunc(sales_date,'MM');


--To compute the percentage ratio of monthly sales over total sales
select trunc(sales_date,'MM') as month,
sum(sales_amount) as total_sales, round(ratio_to_report(sum(sales_amount)) over () *100,2) as ratio_perc
from sales
group by trunc(sales_date,'MM');

-- Group the salespersons into 3 groups based on their total sales
select sp.first_name, 
       SUM(s.sales_amount) as total_sales,
       NTILE (3) OVER( ORDER BY sum(s.sales_amount) DESC) as bucket_list
from sales s
join salesperson sp
on s.salesperson_id=sp.salesperson_id
GROUP BY sp.first_name;
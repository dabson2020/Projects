SELECT
    races.race_id race_id, 
    races.race_year race_year,
    constructors.team_name team_name, 
    SUM(results.points) total_points,
    RANK() OVER (PARTITION BY races.race_year ORDER BY SUM(results.points) DESC) rank
   
    
FROM
    results
JOIN
    races 
ON
    results.race_id = races.race_id
JOIN
    constructors
ON
    results.constructor_id = constructors.constructor_id
group by races.race_id, races.race_year, constructors.team_name
order by SUM(results.points) desc
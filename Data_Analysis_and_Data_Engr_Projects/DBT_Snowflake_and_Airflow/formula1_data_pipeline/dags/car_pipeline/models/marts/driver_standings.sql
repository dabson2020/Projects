with race_result as 
                (SELECT r.race_id race_id, r.race_year race_year, r.race_name race_name,
                SUBSTRING( d.driver_name,
                CHARINDEX('"forename":"', d.driver_name) + LEN('"forename":"'),
                CHARINDEX('"', d.driver_name, CHARINDEX('"forename":"', d.driver_name) + LEN('"forename":"')) -                               (CHARINDEX('"forename":"', d.driver_name) + LEN('"forename":"'))) AS forename,
                SUBSTRING( d.driver_name,
                CHARINDEX('"surname":"', d.driver_name) + LEN('"surname":"'),
                CHARINDEX('"', d.driver_name, CHARINDEX('"surname":"', d.driver_name) + LEN('"surname":"')) -       
                (CHARINDEX('"surname":"', d.driver_name) + LEN('"surname":"'))) AS surname,
                d.nationality driver_nationality ,c.team_name team_name,
                re.points points,
                re.position position,
                FROM results re
                JOIN races r
                ON re.race_id = r.race_id
                JOIN drivers d
                ON re.driver_id = d.driver_id
                JOIN constructors c
                ON c.constructor_id = re.constructor_id)
                
select race_id, race_year, race_name, forename,surname, driver_nationality,team_name,
                SUM(points) total_points, 
                COUNT (CASE WHEN position = 1 THEN 1 else 0 end ) wins
                
from race_result
group by race_id, race_year, race_name, forename, surname, driver_nationality,team_name
ORDER BY total_points desc
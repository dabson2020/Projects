SELECT  
    races.race_year,
    races.race_id,
    races.race_name,
    races.race_date,
    circuits.location,
    drivers.driver_name,
    drivers.driver_number,
    drivers.nationality,
    constructors.team_name,
    results.grid,
    results.fastest_lap,
    results.time,
    results.points
FROM
    {{ref('results')}} results
JOIN
    {{ref('races')}} races
ON 
    results.race_id = races.race_id
JOIN
    {{ref('drivers')}} drivers
ON
    results.driver_id = drivers.driver_id
JOIN
    {{ref('constructors')}} constructors
ON
    results.constructor_id = constructors.constructor_id    
JOIN
    {{ref('circuits')}} circuits
ON
    races.circuit_id = circuits.circuit_id
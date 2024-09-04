SELECT
    race_id,
    driver_id,
    lap,
    position,
    time as lap_time,
    milliseconds
FROM
    {{source('formula1','laptimes')}}

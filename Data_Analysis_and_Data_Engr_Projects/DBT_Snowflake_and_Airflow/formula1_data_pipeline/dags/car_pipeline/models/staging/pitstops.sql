SELECT
    race_id,
    driver_id,
    stop,
    lap,
    time as lap_time,
    duration,
    milliseconds
FROM
    {{source('formula1','pitstops')}}
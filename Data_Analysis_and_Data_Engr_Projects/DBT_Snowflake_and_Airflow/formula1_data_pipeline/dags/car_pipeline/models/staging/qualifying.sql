SELECT 
    qualify_id,
    race_id,
    driver_id,
    constructor_id,
    number,
    position,
    q1,
    q2,
    q3
FROM
    {{source('formula1','qualifying')}}
SELECT 
    circuit_id,
    circuit_ref,
    circuit_name,
    location,
    country,
    latitude,
    longitude,
    altitude
FROM
    {{source('formula1', 'circuits')}}
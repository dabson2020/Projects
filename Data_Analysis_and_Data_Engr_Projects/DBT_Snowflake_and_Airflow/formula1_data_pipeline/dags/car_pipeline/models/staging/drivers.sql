SELECT
    driver_id,
    driver_ref,
    driver_number,
    code,
    driver_name,
    dob,
    nationality
FROM
    {{source('formula1', 'drivers')}}
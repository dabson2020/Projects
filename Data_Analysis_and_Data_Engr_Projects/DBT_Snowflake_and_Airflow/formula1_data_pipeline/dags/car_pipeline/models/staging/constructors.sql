SELECT  
    constructor_id,
    constructor_ref,
    team_name,
    nationality
FROM
    {{source('formula1', 'constructors')}}
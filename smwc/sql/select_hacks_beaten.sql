SELECT id, title, exit_count, exits_cleared, 
    CASE WHEN exit_count = exits_cleared 
    THEN 0 ELSE 1 END AS is_beaten 
FROM hacks
WHERE is_beaten = 0
	AND exits_cleared <> 0;
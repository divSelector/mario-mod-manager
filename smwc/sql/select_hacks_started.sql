SELECT id, title, exit_count, exits_cleared
FROM hacks
WHERE exits_cleared > 0
    AND exit_count <> exits_cleared;
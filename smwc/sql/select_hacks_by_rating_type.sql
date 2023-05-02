SELECT hacks.id, hacks.title, hack_paths.path, hacks.rating FROM hacks
JOIN hack_paths ON hacks.id = hack_paths.hack_id
JOIN hack_types ON hacks.id = hack_types.hack_id
WHERE hack_types.type LIKE ?
AND hacks.rating > ?;
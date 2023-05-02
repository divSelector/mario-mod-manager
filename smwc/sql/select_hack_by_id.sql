SELECT hacks.*, hack_types.type, hack_paths.path, hack_authors.author FROM hacks 
JOIN hack_paths ON hacks.id = hack_paths.hack_id
JOIN hack_types ON hacks.id = hack_types.hack_id
JOIN hack_authors ON hacks.id = hack_authors.hack_id
WHERE id = ?;
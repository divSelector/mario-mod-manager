SELECT h.*, 
    GROUP_CONCAT(DISTINCT ht.type) as types,
    GROUP_CONCAT(DISTINCT ha.author) as authors,
    GROUP_CONCAT(DISTINCT hp.path) as paths
FROM hacks h
LEFT JOIN hack_types ht ON ht.hack_id = h.id
LEFT JOIN hack_authors ha ON ha.hack_id = h.id
LEFT JOIN hack_paths hp ON hp.hack_id = h.id
WHERE h.id = ?
GROUP BY h.id;
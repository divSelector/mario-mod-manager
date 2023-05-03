SELECT h.*,
    GROUP_CONCAT(DISTINCT ht.type) as types,
    GROUP_CONCAT(DISTINCT ha.author) as authors,
    GROUP_CONCAT(DISTINCT hp.path) as paths
FROM hacks h
LEFT JOIN hack_types ht ON ht.hack_id = h.id
LEFT JOIN hack_authors ha ON ha.hack_id = h.id
LEFT JOIN hack_paths hp ON hp.hack_id = h.id
WHERE h.title LIKE ?
    AND ht.type LIKE ?
    AND ha.author LIKE ?
	AND h.rating > ?
    AND h.rating < ?
    AND h.exit_count > ?
    AND h.exit_count < ?
    AND h.downloaded_count > ?
    AND h.downloaded_count < ?
    AND h.created_on > date(?)
    AND h.created_on < date(?)
    AND h.is_featured LIKE ?
    AND h.is_demo LIKE ?
GROUP BY h.id;
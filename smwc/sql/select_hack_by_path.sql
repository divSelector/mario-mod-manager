SELECT h.id, h.title, h.created_on, h.page_url, 
    h.is_demo, h.is_featured, h.exit_count, 
    h.rating, h.size, h.size_units,
    h.download_url, h.downloaded_count,
    GROUP_CONCAT(DISTINCT ht.type) as types,
    GROUP_CONCAT(DISTINCT ha.author) as authors,
    GROUP_CONCAT(DISTINCT hp.path) as paths,
    h.exits_cleared
FROM hacks h
LEFT JOIN hack_types ht ON ht.hack_id = h.id
LEFT JOIN hack_authors ha ON ha.hack_id = h.id
LEFT JOIN hack_paths hp ON hp.hack_id = h.id
WHERE hp.path = ?
GROUP BY h.id;
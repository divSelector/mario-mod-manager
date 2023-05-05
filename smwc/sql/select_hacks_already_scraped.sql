SELECT 
    id, page_url,
    CASE 
        WHEN page_url LIKE '%&id=%' THEN SUBSTR(page_url, INSTR(page_url, '&id=') + 4)
        ELSE NULL 
    END AS url_id
FROM hacks;
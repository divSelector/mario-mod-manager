DELETE FROM hacks 
WHERE id IN (
  SELECT h.id
  FROM hacks h
  LEFT JOIN hack_paths hp ON hp.hack_id = h.id
  WHERE hp.path IS NULL
);
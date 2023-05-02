CREATE TABLE hacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    page_url TEXT NOT NULL UNIQUE,
    is_demo TEXT NOT NULL,
    is_featured TEXT NOT NULL,
    exit_count INTEGER NOT NULL,
    rating REAL NOT NULL,
    size REAL NOT NULL,
    size_units TEXT NOT NULL,
    download_url TEXT NOT NULL,
    downloaded_count INTEGER NOT NULL
);

CREATE TABLE hack_types (
    hack_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    FOREIGN KEY (hack_id) REFERENCES hacks(id) ON DELETE CASCADE
);

CREATE TABLE hack_authors (
    hack_id INTEGER NOT NULL,
    author TEXT NOT NULL,
    FOREIGN KEY (hack_id) REFERENCES hacks(id) ON DELETE CASCADE
);

CREATE TABLE hack_paths (
    hack_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    FOREIGN KEY (hack_id) REFERENCES hacks(id) ON DELETE CASCADE
);
"""Database tables, kept inside Python (no .sql files).

SQLITE_SCHEMA is used for the optional SQLite mode and the tests.
MYSQL_SCHEMA is used with XAMPP's MySQL (the default). Both are safe to run repeatedly
(CREATE TABLE IF NOT EXISTS), so db.py applies them automatically on first use.
"""

SQLITE_SCHEMA = r"""
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS user_account (
    user_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,          
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ingredient (
    ingredient_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT NOT NULL UNIQUE,
    unit            TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pantry_item (
    pantry_item_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES user_account(user_id) ON DELETE CASCADE,
    ingredient_id   INTEGER NOT NULL REFERENCES ingredient(ingredient_id),
    quantity_on_hand REAL NOT NULL DEFAULT 0,
    expiry_date     TEXT,                   
    UNIQUE (user_id, ingredient_id)          
);

CREATE TABLE IF NOT EXISTS recipe (
    recipe_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES user_account(user_id) ON DELETE CASCADE,
    recipe_name     TEXT NOT NULL,
    servings        INTEGER NOT NULL CHECK (servings >= 1),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS recipe_ingredient (
    recipe_ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id       INTEGER NOT NULL REFERENCES recipe(recipe_id) ON DELETE CASCADE,
    ingredient_id   INTEGER NOT NULL REFERENCES ingredient(ingredient_id),
    quantity_needed REAL NOT NULL CHECK (quantity_needed > 0)
);
CREATE TABLE IF NOT EXISTS recipe_group (
    group_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES user_account(user_id) ON DELETE CASCADE,
    group_name      TEXT NOT NULL COLLATE NOCASE,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (user_id, group_name)             
);

CREATE TABLE IF NOT EXISTS recipe_group_item (
    group_item_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id        INTEGER NOT NULL REFERENCES recipe_group(group_id) ON DELETE CASCADE,
    recipe_id       INTEGER NOT NULL REFERENCES recipe(recipe_id) ON DELETE CASCADE,
    servings        INTEGER NOT NULL CHECK (servings >= 1),
    UNIQUE (group_id, recipe_id)
);

CREATE INDEX IF NOT EXISTS idx_pantry_user ON pantry_item(user_id);
CREATE INDEX IF NOT EXISTS idx_recipe_user ON recipe(user_id);
CREATE INDEX IF NOT EXISTS idx_recipe_ingredient_recipe ON recipe_ingredient(recipe_id);
CREATE INDEX IF NOT EXISTS idx_group_user ON recipe_group(user_id);
CREATE INDEX IF NOT EXISTS idx_group_item_group ON recipe_group_item(group_id);
"""

MYSQL_SCHEMA = r"""
CREATE TABLE IF NOT EXISTS user_account (
    user_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(190) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ingredient (
    ingredient_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    ingredient_name VARCHAR(190) NOT NULL,
    unit VARCHAR(80) NOT NULL DEFAULT '',
    PRIMARY KEY (ingredient_id),
    UNIQUE KEY uq_ingredient_name (ingredient_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pantry_item (
    pantry_item_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    ingredient_id INT UNSIGNED NOT NULL,
    quantity_on_hand DECIMAL(12,3) NOT NULL DEFAULT 0,
    expiry_date DATE NULL,
    PRIMARY KEY (pantry_item_id),
    UNIQUE KEY uq_pantry_user_ingredient (user_id, ingredient_id),
    KEY idx_pantry_user (user_id),
    CONSTRAINT fk_pantry_user FOREIGN KEY (user_id)
        REFERENCES user_account(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_pantry_ingredient FOREIGN KEY (ingredient_id)
        REFERENCES ingredient(ingredient_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS recipe (
    recipe_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    recipe_name VARCHAR(190) NOT NULL,
    servings INT UNSIGNED NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (recipe_id),
    KEY idx_recipe_user (user_id),
    CONSTRAINT chk_recipe_servings CHECK (servings >= 1),
    CONSTRAINT fk_recipe_user FOREIGN KEY (user_id)
        REFERENCES user_account(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS recipe_ingredient (
    recipe_ingredient_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    recipe_id INT UNSIGNED NOT NULL,
    ingredient_id INT UNSIGNED NOT NULL,
    quantity_needed DECIMAL(12,3) NOT NULL,
    PRIMARY KEY (recipe_ingredient_id),
    KEY idx_recipe_ingredient_recipe (recipe_id),
    CONSTRAINT chk_recipe_ingredient_quantity CHECK (quantity_needed > 0),
    CONSTRAINT fk_recipe_ingredient_recipe FOREIGN KEY (recipe_id)
        REFERENCES recipe(recipe_id) ON DELETE CASCADE,
    CONSTRAINT fk_recipe_ingredient_ingredient FOREIGN KEY (ingredient_id)
        REFERENCES ingredient(ingredient_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS recipe_group (
    group_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    group_name VARCHAR(60) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (group_id),
    UNIQUE KEY uq_recipe_group_user_name (user_id, group_name),
    KEY idx_group_user (user_id),
    CONSTRAINT fk_recipe_group_user FOREIGN KEY (user_id)
        REFERENCES user_account(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS recipe_group_item (
    group_item_id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    group_id INT UNSIGNED NOT NULL,
    recipe_id INT UNSIGNED NOT NULL,
    servings INT UNSIGNED NOT NULL,
    PRIMARY KEY (group_item_id),
    UNIQUE KEY uq_group_recipe (group_id, recipe_id),
    KEY idx_group_item_group (group_id),
    CONSTRAINT chk_group_item_servings CHECK (servings >= 1),
    CONSTRAINT fk_group_item_group FOREIGN KEY (group_id)
        REFERENCES recipe_group(group_id) ON DELETE CASCADE,
    CONSTRAINT fk_group_item_recipe FOREIGN KEY (recipe_id)
        REFERENCES recipe(recipe_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

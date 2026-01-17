\d authentication_menumodule

-- Add missing columns if they don't exist
ALTER TABLE authentication_menumodule ADD COLUMN IF NOT EXISTS category_id INTEGER;
ALTER TABLE authentication_menumodule ADD COLUMN IF NOT EXISTS "order" INTEGER DEFAULT 0;
ALTER TABLE authentication_menumodule ADD COLUMN IF NOT EXISTS path VARCHAR(200);
ALTER TABLE authentication_menumodule ADD COLUMN IF NOT EXISTS requires_permission BOOLEAN DEFAULT TRUE;

-- Update existing columns
ALTER TABLE authentication_menumodule ALTER COLUMN key TYPE VARCHAR(50);
ALTER TABLE authentication_menumodule ALTER COLUMN icon TYPE VARCHAR(50);

-- Add foreign key constraint if it doesn't exist
ALTER TABLE authentication_menumodule ADD CONSTRAINT fk_menumodule_category 
FOREIGN KEY (category_id) REFERENCES authentication_menucategory(id) ON DELETE CASCADE;

\q
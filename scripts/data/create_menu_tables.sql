-- Create menu tables manually
CREATE TABLE IF NOT EXISTS authentication_menucategory (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    key VARCHAR(50) UNIQUE NOT NULL,
    icon VARCHAR(50) NOT NULL,
    "order" INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS authentication_menumodule (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES authentication_menucategory(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    key VARCHAR(50) UNIQUE NOT NULL,
    icon VARCHAR(50) NOT NULL,
    path VARCHAR(200) NOT NULL,
    "order" INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    requires_permission BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS authentication_companymenuaccess (
    id SERIAL PRIMARY KEY,
    athens_tenant_id UUID NOT NULL,
    module_id INTEGER REFERENCES authentication_menumodule(id) ON DELETE CASCADE,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(athens_tenant_id, module_id)
);

CREATE TABLE IF NOT EXISTS authentication_usermenupermission (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES authentication_customuser(id) ON DELETE CASCADE,
    module_id INTEGER REFERENCES authentication_menumodule(id) ON DELETE CASCADE,
    can_access BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, module_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_menucategory_order ON authentication_menucategory("order");
CREATE INDEX IF NOT EXISTS idx_menumodule_category ON authentication_menumodule(category_id);
CREATE INDEX IF NOT EXISTS idx_menumodule_order ON authentication_menumodule("order");
CREATE INDEX IF NOT EXISTS idx_companymenuaccess_tenant ON authentication_companymenuaccess(athens_tenant_id);
CREATE INDEX IF NOT EXISTS idx_usermenupermission_user ON authentication_usermenupermission(user_id);
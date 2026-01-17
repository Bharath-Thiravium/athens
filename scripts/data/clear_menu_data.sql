-- Clear menu data with proper foreign key handling
DELETE FROM authentication_usermenupermission;
DELETE FROM authentication_companymenuaccess;
DELETE FROM authentication_projectmenuaccess;
DELETE FROM authentication_menumodule;
DELETE FROM authentication_menucategory;

-- Reset sequences
ALTER SEQUENCE authentication_menucategory_id_seq RESTART WITH 1;
ALTER SEQUENCE authentication_menumodule_id_seq RESTART WITH 1;
-- Fix Script: Remove Events Module and Clean Broken Attachments
-- Run this with: psql -U luminous_imteaj -d odoo_test_db -f fix_events_and_attachments.sql

-- Step 1: Delete ALL broken file attachments
-- (Since filestore was missing, ALL file references are broken)
DELETE FROM ir_attachment WHERE store_fname IS NOT NULL;

-- Step 2: Find and mark Events modules for uninstallation
UPDATE ir_module_module 
SET state = 'to remove' 
WHERE name LIKE '%event%' 
  AND state = 'installed';

-- Step 3: Show what will be uninstalled
SELECT id, name, state, latest_version 
FROM ir_module_module 
WHERE name LIKE '%event%' 
ORDER BY name;

-- Step 4: Show attachment cleanup results
SELECT 
    'Cleanup Complete' as status,
    COUNT(*) as total_attachments,
    COUNT(CASE WHEN store_fname IS NOT NULL THEN 1 END) as file_attachments,
    COUNT(CASE WHEN db_datas IS NOT NULL THEN 1 END) as db_attachments
FROM ir_attachment;


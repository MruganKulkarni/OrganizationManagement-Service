// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

db = db.getSiblingDB('org_master_db');

// Create collections with indexes for better performance
db.createCollection('organizations');
db.createCollection('admin_users');
db.createCollection('audit_logs');

// Create indexes for organizations collection
db.organizations.createIndex({ "organization_name": 1 }, { unique: true });
db.organizations.createIndex({ "created_at": 1 });
db.organizations.createIndex({ "status": 1 });

// Create indexes for admin_users collection
db.admin_users.createIndex({ "email": 1 }, { unique: true });
db.admin_users.createIndex({ "organization_id": 1 });
db.admin_users.createIndex({ "is_active": 1 });

// Create indexes for audit_logs collection
db.audit_logs.createIndex({ "timestamp": 1 });
db.audit_logs.createIndex({ "action": 1 });
db.audit_logs.createIndex({ "organization_name": 1 });
db.audit_logs.createIndex({ "admin_email": 1 });

print('Database initialization completed successfully!');
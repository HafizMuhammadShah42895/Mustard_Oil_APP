# Production Readiness Checklist

## Critical Security Fixes Required

### 1. Fix Admin Password Authentication
- Replace plain text password comparison with hashed password verification
- Update admin_routes.py line 39-40

### 2. Remove Hardcoded Credentials
- Move all email addresses to environment variables
- Remove hardcoded database credentials from __init__.py

### 3. Disable Debug Mode
- Set debug=False in run.py for production
- Use environment variable to control debug mode

### 4. Add File Upload Security
- Validate file extensions for image uploads
- Add file size limits
- Check MIME types

### 5. Add Input Validation
- Validate all form inputs
- Add CSRF protection
- Sanitize user inputs

## Files to Remove

1. `create_reviews_table.py` - No longer needed
2. `app/static/2.png` - Unused image file
3. `app/static/hero.jpg` - Not used in current design

## Environment Variables Needed

```
SECRET_KEY=your-production-secret-key
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=your-db-host
DB_NAME=your-db-name
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
ADMIN_EMAIL=admin@yourdomain.com
FLASK_DEBUG=False
```

## Additional Recommendations

1. Add proper logging instead of print statements
2. Implement rate limiting for forms
3. Add database connection pooling
4. Set up proper error pages (404, 500)
5. Add SSL/HTTPS configuration
6. Implement backup strategy
7. Add monitoring and health checks
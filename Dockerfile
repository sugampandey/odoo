FROM python:3.11.6-slim

# ----------------------------------------------------
# 1. Install system dependencies (rarely change)
# ----------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    git wget curl python3-dev build-essential \
    libxml2-dev libxslt1-dev zlib1g-dev libsasl2-dev libldap2-dev \
    libssl-dev libjpeg-dev libpq-dev postgresql-client \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# ----------------------------------------------------
# 2. Create non-root user for Odoo
# ----------------------------------------------------
RUN useradd -m -d /var/lib/odoo -U -r -s /bin/bash odoo

# ----------------------------------------------------
# 3. Set working directory
# ----------------------------------------------------
ENV ODOO_HOME=/opt/odoo
WORKDIR $ODOO_HOME

# ----------------------------------------------------
# 4. Copy requirements.txt first & install Python deps
# ----------------------------------------------------
COPY requirements.txt .
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# ----------------------------------------------------
# 5. Copy Odoo core (changes less frequently)
# ----------------------------------------------------
COPY odoo/ ./odoo/

# ----------------------------------------------------
# 6. Copy custom addons (changes frequently)
# ----------------------------------------------------
COPY addons/ ./addons/

# ----------------------------------------------------
# 7. Copy config + wait-for script
# ----------------------------------------------------
COPY debian/odoo.conf ./debian/odoo.conf
COPY wait-for-rds.sh /usr/local/bin/wait-for-rds.sh
RUN chmod +x /usr/local/bin/wait-for-rds.sh

# ----------------------------------------------------
# 8. Copy any other project files (scripts, etc.)
# ----------------------------------------------------
COPY . $ODOO_HOME

# ----------------------------------------------------
# 9. Fix permissions
# ----------------------------------------------------
RUN chown -R odoo:odoo $ODOO_HOME
USER odoo

# ----------------------------------------------------
# 10. Entrypoint & CMD
# ----------------------------------------------------
ENTRYPOINT ["wait-for-rds.sh"]
CMD ["python", "/opt/odoo/odoo-bin", "-c", "/opt/odoo/debian/odoo.conf"]

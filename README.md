# Retail Inventory and Sales Management System (RISMS)

## Set up the database and launch the app

The application connects to a local MySQL server and uses the database
`sales_management_db`. Install MySQL Server, then create the schema and sample
records from a terminal in the repository root:

```sh
mysql -u root -p < sales_management/database/schema.sql
mysql -u root -p < sales_management/database/seed_data.sql
```

The first command creates the database, tables, triggers, and reports' views.
The second loads the sample data and demo accounts. These seed records are for
an empty database; do not rerun the seed command after data has already been
loaded.

Install the Python dependencies and start the Streamlit app from its project directory:

```sh
cd sales_management
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

You can also launch it with `python main.py`. The sidebar contains
**Overview**, **Tables**, **Queries**, **Form designs**,
**Reports**, **Data dictionary**, and **ERD**. Operational views such as sales,
purchases, inventory, customers, expenses, products, and users are grouped
inside **Tables**, alongside the browser for all 14 database tables. Queries
includes the proposal queries and management reports from `database/queries.sql`,
plus the full SQL script. Sales
and purchase forms support multiple items per transaction; inventory and
line-item records are maintained by database triggers. Reports includes the
existing text summaries and chart reports. The app opens directly in local
mode without an application login.

The connection defaults to MySQL on `localhost:3306`, username `root`, an
empty password, and database `sales_management_db`. For a MySQL installation
with a different password or username, set these variables before starting
the app (use your own MySQL credentials):

```sh
export RISMS_DB_HOST=localhost
export RISMS_DB_PORT=3306
export RISMS_DB_USER=root
export RISMS_DB_PASSWORD='your MySQL password'
export RISMS_DB_NAME=sales_management_db
```

The Users page lists the seeded accounts, which can also be used if database
authentication is enabled again later:

| Username | Password | Role |
| --- | --- | --- |
| `admin_user` | `admin123` | Administrator |
| `manager_john` | `manager123` | Manager |
| `cashier_grace` | `cashier123` | Sales Employee |
| `cashier_brian` | `brian123` | Sales Employee |
| `store_peter` | `store123` | Inventory Employee |

The sample `cashier_diana` account is intentionally inactive. Local mode skips
the app's role-based login screen; restrict access to the computer and MySQL
account accordingly.



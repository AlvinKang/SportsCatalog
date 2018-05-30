# Linux Server Configuration
This project involves configuring an Amazon AWS Lightsail Linux Ubuntu server to deploy the Catalog App on the web (via Apache).

**You can check out the app live [here](http://catalog.app.alvinkang.com).**

**You can learn more about the app [here](https://github.com/AlvinKang/CatalogApp).**

## Configuration Summary
When the server was first created on AWS Lightsail, Linux Ubuntu (Xenial 16.04) was all that was installed on the machine. In order to successfully deploy the Catalog App, I had to configure and install many things. App-specific Python packages are listed in `requirements.txt`.

#### SSH port configuration
In the server, I configured the `sshd_config` file to access through port 2200 instead of the default 22.
#### Key-based SSH authentication
In order to SSH into the server from my local machine, I had to set up key-based SSH authentication. I downloaded the default private key from AWS and changed its permissions to read-only for the owner. Since AWS had already installed the corresponding public key, I was able to SSH without a hitch.
#### Firewall configuration
By default the firewall was turned off, and for security measures, I had to configure and enable it (`ufw`) to only accept certain protocols. With the firewall turned off, I started off by blocking all incoming connections. Then, I allowed each port and corresponding protocol one-by-one: SSH (2200), HTTP (80), NTP (123). I enabled the firewall afterwards.
#### Grader access
To allow the Udacity reviewer to access the server, I first created a new account with username `grader`. As required by the project, I gave it superuser (`sudo`) privileges. Then, I generated a key pair using `key-gen` (4096-bit, RSA algorithm). I switched into the `grader` account and installed the public key in the user's `authorized_keys` file located in `~/.ssh/`. With that, I was able to SSH into the server as `grader` using the generated private key.
#### Local timezone configuration
I configured the timezone to UTC by executing `$ dpkg-reconfigure tzdata`, which renders a GUI menu to select the timezone.
#### Apache installation and configuration
The app is deployed through an Apache web server. I installed `apache2` and `mod_wsgi`, which enables Python to communicate with Apache. Then I created a `CatalogApp/` directory inside `/var/www/` just to test that everything was working. I created a new site config file for the app in the `/.../apache2/sites-available/` directory and configured it to work with `mod_wsgi`. I also enabled Apache's `dump_io` mod to log Python errors into the `errors.log` file.
#### Python installation and configuration
This server already had Python installed. So I just needed to download the relevant packages for the app. First, I installed `python-pip` and `virtualenv`. Then, I activated the virtual environment for the project and proceeded to install `Flask`, `psycopg2`, `SQLAlchemy`, `requests`, and `oauth2client` (other Python dependencies are listed in `requirements.txt`).
#### PostgreSQL installation and configuration
I used Postgres as my back-end database for the application. I installed `postgresql`, `postgresql-contrib`, and `libpq-dev`. I created a new Postgres role called `catalog` and set privileges to only allow control of databases created by `catalog`. I logged in to the `catalog` role in Postgres and created the `catalog_app` database.
#### Git installation
I installed `git` and cloned the Catalog App that I built previously.
#### CatalogApp modifications
Since the previous version of Catalog App used `sqlite` and was deployed locally, I had to modify several things. First, I changed the database to connect to my newly set-up Postgres database. Next, I changed the **'Authorized Javascript Origins'** and **'Authorized redirect URIs'** on this app's Google OAuth2.0 credentials to allow access to this API. Since OAuth cannot access IP addresses, I purchased and registered a domain name. I also had to modify the path to the locally stored OAuth credentials to be absolute (e.g., `"/.../CatalogApp/CatalogApp/client_secrets.json"`) instead of relative (e.g., `"/client_secrets.json"`). I also fixed some minor bugs in the code.

## References
In order to complete the project, I referred to the following websites (in no particular order):
* [http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/](http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/)
* [http://xip.io/](http://xip.io/)
* [https://aws.amazon.com/premiumsupport/knowledge-center/new-user-accounts-linux-instance/](https://aws.amazon.com/premiumsupport/knowledge-center/new-user-accounts-linux-instance/)
* [https://blog.bigbinary.com/2016/01/23/configure-postgresql-to-allow-remote-connection.html](https://blog.bigbinary.com/2016/01/23/configure-postgresql-to-allow-remote-connection.html)
* [https://blog.theodo.fr/2017/03/developping-a-flask-web-app-with-a-postresql-database-making-all-the-possible-errors/](https://blog.theodo.fr/2017/03/developping-a-flask-web-app-with-a-postresql-database-making-all-the-possible-errors/)
* [https://developers.google.com/identity/protocols/OAuth2WebServer](https://developers.google.com/identity/protocols/OAuth2WebServer)
* [https://help.ubuntu.com/community/UFW](https://help.ubuntu.com/community/UFW)
* [https://launchschool.com/blog/how-to-install-postgres-for-linux](https://launchschool.com/blog/how-to-install-postgres-for-linux)
* [https://marcyes.com/2016/0922-messing-with-postgresql-users-and-permissions/](https://marcyes.com/2016/0922-messing-with-postgresql-users-and-permissions/)
* [https://modwsgi.readthedocs.io/en/develop/user-guides/quick-configuration-guide.html](https://modwsgi.readthedocs.io/en/develop/user-guides/quick-configuration-guide.html)
* [https://support.rackspace.com/how-to/set-up-apache-virtual-hosts-on-ubuntu/](https://support.rackspace.com/how-to/set-up-apache-virtual-hosts-on-ubuntu/)
* [https://www.codementor.io/engineerapart/getting-started-with-postgresql-on-mac-osx-are8jcopb](https://www.codementor.io/engineerapart/getting-started-with-postgresql-on-mac-osx-are8jcopb)
* [https://www.cyberciti.biz/faq/apache-mod_dumpio-log-post-data/](https://www.cyberciti.biz/faq/apache-mod_dumpio-log-post-data/)
* [https://www.digitalocean.com/community/tutorials/how-to-create-temporary-and-permanent-redirects-with-apache](https://www.digitalocean.com/community/tutorials/how-to-create-temporary-and-permanent-redirects-with-apache)
* [https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)
* [https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04)
* [https://www.digitalocean.com/community/tutorials/how-to-use-roles-and-manage-grant-permissions-in-postgresql-on-a-vps--2](https://www.digitalocean.com/community/tutorials/how-to-use-roles-and-manage-grant-permissions-in-postgresql-on-a-vps--2)
* [http://xmodulo.com/how-to-force-ssh-login-via-public-key-authentication.html](http://xmodulo.com/how-to-force-ssh-login-via-public-key-authentication.html)

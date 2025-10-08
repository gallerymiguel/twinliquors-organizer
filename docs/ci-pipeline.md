# DevOps CI Pipeline Explanation

My pipeline was created so I can test push and pull requests through GitHub to make sure I always have clean and tested code. I used `ubuntu-latest` so GitHub gives me an isolated environment every time the pipeline runs through a disposable Linux server in the cloud.

I test my database by spawning a temporary MariaDB 11 container before tests run. It sets the environment variables for credentials and database setup and checks if the container is healthy before proceeding. I did this because it mimics my production database in a test environment. Now every developer or pull request gets their own fresh DB container with no risk of corrupting shared data. The health check ensures that tests don’t run until the database is actually ready.

In the next step, I have my script tell GitHub to download my repository into a virtual machine so it can run my code. Without this, GitHub has no idea what code to test.

The next step in the script tells GitHub to install Python 3.11 in the VM. This helps prevent “works on my machine” issues by ensuring everyone uses the same version.

After that, GitHub installs my dependencies by upgrading pip and installing everything from `requirements.txt`. This recreates my app’s runtime environment exactly like in production, and every dependency version is controlled and tested.

Next, GitHub installs the MariaDB client so it can connect to the database, which is needed for the following step.

In this step, GitHub tests my database connection by connecting to my IP address with the username, password, and database name. This ensures the tests don’t start before the database is online and stable; otherwise, I’d get random connection errors.

Finally, at the end of the script, GitHub runs all of the tests that I’ve written for the program. These would usually include component tests, end-to-end tests, or any other in-program tests. This helps GitHub warn me if anything might break before merging into the main branch.

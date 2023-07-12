### Running the tests

You use `poetry` and `pytest` to run the tests:

`poetry run pytest -s`

You can also run specific files

`poetry run pytest tests/<test_folder>/<test_file.py>`

and even use filtering with `-k`

`poetry run pytest -k "Manager"`

You can use the flags `-vx` where `v` prints the test & `x` makes the test stop if any
tests fails (Verbose, X-fail)

You can get the coverage report like this:

`poetry run pytest -s --cov --cov-report term-missing -vvx`

### Using the app

First make sure that OS2mo is up and running.

You can then boot the app like this:

```
poetry lock
poetry install
docker-compose up
```

### inspecting emails using smtp4dev

In the development environment we use a mailserver called `mailcatcher`. To use it,
go to [localhost:1080](http://localhost:1080/) to inspect mails which would be sent out
by the application if this was a production environment.


### Adding agents

To add an email agent, write a function in `agents.py`. The function should be able to:
- Receive an AMQP message
- Process the message
- Send an email

Then activate the agent by adding the function name to the `active_agents` config list
variable
# Petit Mail Engine

This project is made to easely send emails from an application

## Why ?

It is a part of the petite stack, a stack made to build petite apps.

Here we make developped this part in order to be used in the petit_erp project, which aims to make building ERP easier and faster

Reloads all the template of the server without restarting the server.


### How to write a template

This lib uses the Jinja2 template engine, so you can refer to the Jinja2 documentation for the syntax.

There is however, one diffence, in an effort to be concise the subject and the body of each template are in the same file.

So you have to put the **subject** of the email between this two balises: '<subject>' and '</subject>'

The body of the email should then be between this two balises: '<mail_content>' and '</mail_content>'

Example :

```jinja
<subject>
    Docker | Backup Failed
</subject>


<mail_content>

    <body>
        {% from "common/centered_button.html" import centered_button %} {% from "common/card.html" import card %} {% call card("La sauvegarde a échouée") %}

        <div style="white-space: pre-wrap">
            The backup failed at {{data.operation_date}}, if the problem persists, contact an administrator
        </div>
        <br /> {{ centered_button("Example Incorporation", "https://example.com") }}

        <br> Sysadmins {% endcall %}

    </body>

</mail_content>
```

### How to reuse components

In order to make a component reusable, you have to place it into the common directory, and you don't have to use the special <subject> and <mail_content> balises.


## Configuration

Most of the configuration is held in the `conf.yaml` file.

There are 2 things to configure, the template_provider and the emails senders:

The infos for the template provider are located under the `templates` key.

Two providers are provided with the library, an S3 provider and a local provider.

They can be used by using the string values 's3' or 'local'. You can see below an example of settings for both types.

exemple :

```yaml
templates:
  # minio doesn't support the last options
  s3:
    host: documents.staging.example.com
    pass_key: password
    access_key: key
    bucket_name: mail-templates

  local: 
    folder: templates
```

exemple :

```yaml
creds:
  example:
    type: gmail
    email: example@example.com
    refresh_token: <>
    client_id: <>
    client_secret: <>
  info:
    type: gmail
    email: info@example.com
    refresh_token: <>
    client_id: <>
    client_secret: <>
  
  # note that here with smtp support it's not the same keys
  info2:
    type: smtp
    email: info@example.com
    password: <>
    server: <>
    server_port: <>
```

### How to get your tokens ?

- Activate your Gmail API keys in the Gmail console
- Get the `credentials.json` from the Gmail console
- use the `make_token.py` script from the `google_token_utils` folder

## How to add a custom TemplateDB provider ?

Inherit the `TemplateDB` class and overide the `init` function and the `get_creds_form`function

Then before calling `make_server` you can use the `add_template_db_engine` and add the class under the name you like, it will then be bound automatically

## How to add a custom EmailSender ?

Inherit the `EmailSender` class and overide `get_creds_form` function and the `send_html_mail` ,`send_raw_mail` functions.

Then before calling `make_server` you can use the `add_sender_engine` and add the class under the name you like, it will then be bound automatically


## TODO

- add monitoring
- add support to make templates with grapeJS

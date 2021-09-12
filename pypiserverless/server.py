from .aws import get_file_url, packages_list


def html(title, content):
    return f"<html><head><title>{title}</title></head><body><h1>{title}</h1>{content}</body></html>"


def home():
    messages = [
        "To use this server with <b>pip</b>, run the following command:",
        "<code>pip install --index-url http://current_host/ PACKAGE [PACKAGE2...]</code>",
        "The complete list of all packages can be found",
        '<a href="packages/">here</a> or via the <a href="simple/">simple</a> index.',
        "This instance is running the pypiserverless package.",
    ]
    content = "<p>" + "</p><p>".join(messages) + "</p>"
    return html("Welcome to pypiserverless!", content)


def simple():
    pkgs = (pkg["name"] for pkg in packages_list())
    content = "".join(f'<a href="../{pkg}/">{pkg}</a><br>' for pkg in set(pkgs))
    return html("Simple Index", content)


def simple_package(package_name):
    content = "".join(
        '<a href="../packages/{filename}">{filename}</a><br>'.format(**pkg) for pkg in packages_list(package_name)
    )
    if content:
        return html(f"Links for {package_name}", content)
    return None


def packages():
    pkgs = (pkg["filename"] for pkg in packages_list())
    content = "".join(f'<a href="{pkg}">{pkg}</a><br>' for pkg in pkgs)
    return html("Index of packages", content)


def handler(event):
    url = event["path"].strip("/")
    response = None
    resp_fn = {"": home, "simple": simple, "packages": packages}.get(url, None)

    if resp_fn:
        response = resp_fn()
    elif "/" not in url:
        response = simple_package(url)
    elif url.startswith("packages/") and len(url.split("/")) == 2:
        package_filename = url[9:]
        return {
            "statusCode": 302,
            "headers": {
                "Location": get_file_url(package_filename),
            },
        }

    if response:
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/html",
            },
            "body": response,
        }

    return {
        "statusCode": 404,
        "body": "Not Found",
    }

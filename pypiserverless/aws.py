from os import getenv, path

import boto3

from .core import guess_pkgname_and_version


def _s3():
    return boto3.client("s3")


def get_file_url(filename):

    url = _s3().generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": getenv("PACKAGES_BUCKET"),
            "Key": path.join(getenv("PACKAGES_PATH"), filename),
        },
        ExpiresIn=600,
    )
    return url


def packages_list(pkg_name=None):

    prefix = pkg_name or ""
    prefix = path.join(getenv("PACKAGES_PATH"), prefix)

    all_files = _s3().list_objects_v2(
        Bucket=getenv("PACKAGES_BUCKET"),
        Prefix=prefix,
    )["Contents"]

    for f in all_files:

        pkg = {}
        pkg["uri"] = f["Key"]
        pkg["filename"] = path.basename(pkg["uri"])

        res = guess_pkgname_and_version(pkg["uri"])

        if res is None:
            continue

        pkg["name"], pkg["version"] = res
        if pkg_name is not None and pkg_name != pkg["name"]:
            continue

        yield pkg

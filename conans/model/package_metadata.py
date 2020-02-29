import json
from collections import defaultdict
from datetime import datetime, timezone

from conans import DEFAULT_REVISION_V1

# Replacement for fromisoformat for older python 3.x, saved times are UTC
time_fmt_str =  r"%Y-%m-%dT%H:%M:%S.%f" 

class _RecipeMetadata(object):

    def __init__(self):
        self._revision = None
        self.properties = {}
        self.checksums = {}
        self.remote = None
        self._last_used = None

    @property
    def revision(self):
        return self._revision

    @revision.setter
    def revision(self, r):
        self._revision = r

    @property
    def last_used(self):
        return self._last_used

    @last_used.setter
    def last_used(self, lu):
        self._last_used = lu

    def to_dict(self):
        ret = {"revision": self.revision,
               "remote": self.remote,
               "properties": self.properties,
               "checksums": self.checksums,
               "last_used_utc": self.last_used}
        return ret

    @staticmethod
    def loads(data):
        ret = _RecipeMetadata()
        ret.revision = data["revision"]
        ret.remote = data.get("remote")
        ret.properties = data["properties"]
        ret.checksums = data.get("checksums", {})
        ret.time = data.get("time")
        try:
            ret.last_used = datetime.strptime(data.get("last_used_utc"), time_fmt_str).replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            ret.last_used = None
        return ret


class _BinaryPackageMetadata(object):

    def __init__(self):
        self._revision = None
        self._recipe_revision = None
        self.properties = {}
        self.checksums = {}
        self.remote = None
        self._last_used = None

    @property
    def revision(self):
        return self._revision

    @revision.setter
    def revision(self, r):
        self._revision = DEFAULT_REVISION_V1 if r is None else r

    @property
    def recipe_revision(self):
        return self._recipe_revision

    @recipe_revision.setter
    def recipe_revision(self, r):
        self._recipe_revision = DEFAULT_REVISION_V1 if r is None else r

    @property
    def last_used(self):
        return self._last_used

    @last_used.setter
    def last_used(self, lu):
        self._last_used = lu

    def to_dict(self):
        ret = {"revision": self.revision,
               "recipe_revision": self.recipe_revision,
               "remote": self.remote,
               "properties": self.properties,
               "checksums": self.checksums,
               "last_used_utc": self.last_used}
        return ret

    @staticmethod
    def loads(data):
        ret = _BinaryPackageMetadata()
        ret.revision = data.get("revision")
        ret.recipe_revision = data.get("recipe_revision")
        ret.properties = data.get("properties")
        ret.checksums = data.get("checksums", {})
        ret.remote = data.get("remote")
        try:
            ret.last_used = datetime.strptime(data.get("last_used_utc"), time_fmt_str).replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            ret.last_used = None
        return ret


class PackageMetadata(object):

    def __init__(self):
        self.recipe = None
        self.packages = None
        self.clear()

    @staticmethod
    def loads(content):
        ret = PackageMetadata()
        data = json.loads(content)
        ret.recipe = _RecipeMetadata.loads(data.get("recipe"))
        for pid, v in data.get("packages").items():
            ret.packages[pid] = _BinaryPackageMetadata.loads(v)
        return ret

    @property
    def last_used(self):
        try:
            return max([self.recipe.last_used] + [p.last_used for p in self.packages.values()])
        except TypeError:
            return None

    def dumps(self, for_comparison=False):
        tmp = {"recipe": self.recipe.to_dict(),
               "packages": {k: v.to_dict() for k, v in self.packages.items()}}
        if for_comparison:
            del tmp["recipe"]["last_used_utc"]
            for package_id in tmp["packages"].keys():
                del tmp["packages"][package_id]["last_used_utc"]

        def default(o):
            if isinstance(o, datetime):
                return o.strftime(time_fmt_str)
        return json.dumps(tmp, default=default)

    def __str__(self):
        return self.dumps()

    def __eq__(self, other):
        return self.dumps(for_comparison=True) == other.dumps(for_comparison=True)

    def clear(self):
        self.recipe = _RecipeMetadata()
        self.packages = defaultdict(_BinaryPackageMetadata)

    def clear_package(self, package_id):
        if package_id in self.packages:
            del self.packages[package_id]

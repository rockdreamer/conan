import unittest
from datetime import datetime, timezone, timedelta
from conans.model.package_metadata import PackageMetadata


class PackageMetadataTest(unittest.TestCase):

    def test_load_unload(self):
        last_used1 = datetime(2000, 1, 1, 0, 10, 23, 283000, tzinfo=timezone.utc)
        last_used2 = datetime(2020, 1, 1, 0, 10, 23, 283000, tzinfo=timezone.utc)

        a = PackageMetadata()
        a.recipe.revision = "rev"
        a.recipe.checksums["somefile1"] = {"md5": "50b2137a5d63567b7e88b743a3b594cf",
                                           "sha1": "0b7e8ed59ff4eacb95fd3cc8e17a8034584a96c2"}
        a.recipe.last_used = last_used1
        a.packages["ID"].recipe_revision = "rec_rev"
        a.packages["ID"].revision = "revp"
        a.packages["ID"].properties["Someprop"] = "23"
        a.packages["ID"].checksums["somefile2"] = {"md5": "efb7597b146344532fe8da2b79860aaa",
                                                   "sha1": "cc3e6eae41eca26538630f4cd5b0bf4fb52e2d"}
        a.packages["ID"].last_used = last_used2

        tmp = a.dumps()

        b = PackageMetadata.loads(tmp)

        self.assertEqual(b, a)
        self.assertEqual(b.packages["ID"].properties["Someprop"], "23")
        self.assertEqual(b.recipe.checksums["somefile1"]["md5"],
                         "50b2137a5d63567b7e88b743a3b594cf")
        self.assertEqual(b.packages["ID"].checksums["somefile2"]["sha1"],
                         "cc3e6eae41eca26538630f4cd5b0bf4fb52e2d")
        self.assertEqual(a.last_used, b.last_used)
        self.assertEqual(a.recipe.last_used, b.recipe.last_used)
        self.assertEqual(a.packages["ID"].last_used, b.packages["ID"].last_used)

    def test_other_types_than_str(self):
        a = PackageMetadata()
        a.recipe.revision = "rev"
        a.packages["ID"].recipe_revision = 34
        a.packages["ID"].revision = {"23": 45}
        a.packages["ID"].properties["Someprop"] = [23, 2444]

        tmp = a.dumps()

        b = PackageMetadata.loads(tmp)

        self.assertEqual(b, a)
        self.assertEqual(b.packages["ID"].revision, {"23": 45})
        self.assertEqual(b.packages["ID"].properties["Someprop"], [23, 2444])

    def test_package_last_used_returns_max_last_used(self):
        last_used1 = datetime(2000, 1, 1, 0, 10, 23, 283000, tzinfo=timezone.utc)
        last_used2 = datetime(2020, 1, 1, 0, 10, 23, 283000, tzinfo=timezone.utc)

        a = PackageMetadata()
        a.recipe.last_used = last_used1
        a.packages["ID"].last_used = last_used2

        tmp = a.dumps()

        b = PackageMetadata.loads(tmp)

        self.assertEqual(b.last_used, last_used2)

    def test_load_with_no_dates(self):
        a = PackageMetadata()
        a.recipe.revision = "rev"
        a.recipe.checksums["somefile1"] = {"md5": "50b2137a5d63567b7e88b743a3b594cf",
                                           "sha1": "0b7e8ed59ff4eacb95fd3cc8e17a8034584a96c2"}
        a.packages["ID"].recipe_revision = "rec_rev"
        a.packages["ID"].revision = "revp"
        a.packages["ID"].properties["Someprop"] = "23"
        a.packages["ID"].checksums["somefile2"] = {"md5": "efb7597b146344532fe8da2b79860aaa",
                                                   "sha1": "cc3e6eae41eca26538630f4cd5b0bf4fb52e2d"}

        tmp = a.dumps()

        b = PackageMetadata.loads(tmp)
        
        # Packages with no last_used data return None
        self.assertIsNone(b.last_used)
        self.assertIsNone(b.recipe.last_used)
        self.assertIsNone(b.packages["ID"].last_used)

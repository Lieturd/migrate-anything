import csv
import types
from collections import namedtuple
from io import open

from migrate_anything.log import logger

try:
    from itertools import imap
except ImportError:
    imap = map

_CSVRow = namedtuple("Row", "name,code")


def _fix_docs(cls):
    """
    Used to copy function docstring from Storage baseclass to subclasses
    """
    for name, func in vars(cls).items():
        if isinstance(func, types.FunctionType) and not func.__doc__:
            for parent in cls.__bases__:
                parfunc = getattr(parent, name, None)
                if parfunc and getattr(parfunc, "__doc__", None):
                    func.__doc__ = parfunc.__doc__
                    break
    return cls


class Storage(object):
    def save_migration(self, name, code):
        """
        Save a migration
        :param str name: The name of the migration
        :param str code: The source code (encoded)
        """
        raise NotImplementedError("Storage class does not implement save_migration")

    def list_migrations(self):
        """
        List applied migrations
        :return List[Tuple[str, str]]:
        """
        raise NotImplementedError("Storage class does not implement list_migrations")

    def remove_migration(self, name):
        """
        Remove migration after it's been undone
        :param str name:
        """
        raise NotImplementedError("Storage class does not implement remove_migration")


@_fix_docs
class CSVStorage(Storage):
    def __init__(self, file):
        self.file = file
        logger.warn(
            "Using CSV storage - hopefully you're just testing or know what you're doing as this data can be easily lost."
        )

    def save_migration(self, name, code):
        with open(self.file, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([name, code])

    def list_migrations(self):
        migrations = []

        try:
            with open(self.file, encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if not row:
                        continue
                    migrations.append(_CSVRow(*row))
        except FileNotFoundError:
            pass

        return migrations

    def remove_migration(self, name):
        migrations = [
            migration for migration in self.list_migrations() if migration.name != name
        ]

        with open(self.file, "w", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            for row in migrations:
                writer.writerow(row)


__all__ = ["CSVStorage"]
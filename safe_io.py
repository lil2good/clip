"""Bounded, nofollow I/O for private state and installer destinations."""
from contextlib import contextmanager
import errno
import os
from pathlib import Path
import secrets
import stat


@contextmanager
def parent_fd(path, create=False):
    """Walk each component without following links; pin the destination directory."""
    path = Path(os.path.abspath(path))
    fd = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for component in path.parent.parts[1:]:
            if create:
                try:
                    os.mkdir(component, mode=0o700, dir_fd=fd)
                except FileExistsError:
                    pass
            try:
                child = os.open(component, os.O_RDONLY | os.O_DIRECTORY |
                                os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
            except OSError as error:
                if error.errno in (errno.ELOOP, errno.ENOTDIR):
                    raise ValueError("Unsafe parent directory") from error
                raise
            os.close(fd)
            fd = child
        if os.fstat(fd).st_uid != os.getuid():
            raise ValueError("Parent directory is not owned by current user")
        yield fd, path.name
    finally:
        os.close(fd)


def validate_file(info, max_bytes=None):
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
        raise ValueError("File must be regular and owned by current user")
    if max_bytes is not None and info.st_size > max_bytes:
        raise ValueError("File exceeds byte limit")


def read_bytes(path, max_bytes):
    with parent_fd(path) as (directory, name):
        validate_file(os.stat(name, dir_fd=directory, follow_symlinks=False), max_bytes)
        try:
            # NONBLOCK prevents a pre-positioned FIFO from hanging before fstat.
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC |
                         os.O_NONBLOCK, dir_fd=directory)
        except OSError as error:
            if error.errno in (errno.ELOOP, errno.ENXIO, errno.ENODEV):
                raise ValueError("Unsafe file refused") from error
            raise
        try:
            validate_file(os.fstat(fd), max_bytes)
            chunks = []
            total = 0
            while True:
                chunk = os.read(fd, min(65536, max_bytes + 1 - total))
                if not chunk:
                    return b"".join(chunks)
                chunks.append(chunk)
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError("File exceeds byte limit")
        finally:
            os.close(fd)


def atomic_write(path, data, mode=0o600, max_bytes=None):
    if max_bytes is not None and len(data) > max_bytes:
        raise ValueError("Output exceeds byte limit")
    with parent_fd(path, create=True) as (directory, name):
        def check_destination():
            try:
                info = os.stat(name, dir_fd=directory, follow_symlinks=False)
            except FileNotFoundError:
                return
            validate_file(info, max_bytes)

        check_destination()
        temporary = ".clip-" + secrets.token_hex(16)
        fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY |
                     os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=directory)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fchmod(stream.fileno(), mode)
                os.fsync(stream.fileno())
            check_destination()
            os.replace(temporary, name, src_dir_fd=directory, dst_dir_fd=directory)
            os.fsync(directory)
        finally:
            try:
                os.unlink(temporary, dir_fd=directory)
            except FileNotFoundError:
                pass


def ensure_directory(path):
    with parent_fd(Path(path) / ".directory-check", create=True):
        pass

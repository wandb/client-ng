import logging
import os
import six
import time

from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler
from wandb import util
import glob


logger = logging.getLogger(__file__)


class FileEventHandler(object):
    def __init__(self, file_path, save_name, api, file_pusher, *args, **kwargs):
        self.file_path = file_path
        # Convert windows paths to unix paths
        save_name = util.to_forward_slash_path(save_name)
        self.save_name = save_name
        self._api = api

    def on_created(self):
        pass

    def on_modified(self):
        pass

    def on_renamed(self, new_path, new_name):
        self.file_path = new_path
        self.save_name = new_name
        self.on_created()

    def finish(self):
        pass


class PolicyNow(FileEventHandler):
    """This policy only uploads files now"""
    def on_created(self):
        self._file_pusher.file_changed(self.save_name, self.file_path)


class PolicyEnd(FileEventHandler):
    """This policy only updates at the end of the run"""

    # TODO: make sure we call this
    def finish(self):
        # We use copy=False to avoid possibly expensive copies, and because
        # user files shouldn't still be changing at the end of the run.
        self._file_pusher.file_changed(self.save_name, self.file_path, copy=False)


class PolicyLive(FileEventHandler):
    """This policy will upload files every RATE_LIMIT_SECONDS as it 
        changes throttling as the size increases"""
    TEN_MB = 10000000
    HUNDRED_MB = 100000000
    ONE_GB = 1000000000
    RATE_LIMIT_SECONDS = 15
    # Wait to upload until size has increased 20% from last upload
    RATE_LIMIT_SIZE_INCREASE = 1.2

    def __init__(self, file_path, save_name, api, file_pusher, *args, **kwargs):
        super(PolicyLive, self).__init__(file_path, save_name, api, file_pusher,
                                         *args, **kwargs)
        self._last_uploaded_time = None
        self._last_uploaded_size = 0

    def on_created(self):
        self.on_modified()

    @property
    def current_size(self):
        return os.path.getsize(self.file_path)

    def min_wait_for_size(self, size):
        if self.current_size < self.TEN_MB:
            return 60
        elif self.current_size < self.HUNDRED_MB:
            return 5 * 60
        elif self.current_size < self.ONE_GB:
            return 10 * 60
        else:
            return 20 * 60

    def last_uploaded(self):
        if self._last_uploaded_time:
            # Check rate limit by time elapsed
            time_elapsed = time.time() - self._last_uploaded_time
            if time_elapsed < self.RATE_LIMIT_SECONDS:
                return time_elapsed
            # Check rate limit by size increase
            size_increase = self.current_size / float(self._last_uploaded_size)
            if size_increase < self.RATE_LIMIT_SIZE_INCREASE:
                return time_elapsed
        return 0

    def on_modified(self):
        if self.current_size == 0:
            return 0

        time_elapsed = self.last_uploaded()
        if time_elapsed == 0 or time_elapsed > self.min_wait_for_size(
            self.current_size
        ):
            self.save_file()

    def finish(self):
        self._file_pusher.file_changed(self.save_name, self.file_path)

    def save_file(self):
        self._last_uploaded_time = time.time()
        self._last_uploaded_size = self.current_size
        self._file_pusher.file_changed(self.save_name, self.file_path)


class DirWatcher(object):
    def __init__(self, root_dir, api):
        self._api = api
        self._file_count = 0
        self._dir = root_dir
        self._user_file_policies = {
            "end": [],
            "live": [],
            "now": []
        }
        self.file_event_handlers = {}
        self._file_observer = PollingObserver()
        self._file_observer.schedule(
            self._per_file_event_handler(), root_dir, recursive=True
        )

    @property
    def emitter(self):
        try:
            return next(iter(self._file_observer.emitters))
        except StopIteration:
            return None

    def _per_file_event_handler(self):
        """Create a Watchdog file event handler that does different things for every file
        """
        file_event_handler = PatternMatchingEventHandler()
        file_event_handler.on_created = self._on_file_created
        file_event_handler.on_modified = self._on_file_modified
        file_event_handler.on_moved = self._on_file_moved
        file_event_handler._patterns = [os.path.join(self._dir, os.path.normpath("*"))]
        # Ignore hidden files/folders
        #  TODO: what other files should we skip?
        file_event_handler._ignore_patterns = [
            "*.tmp",
            os.path.join(self._dir, ".*"),
            os.path.join(self._dir, "*/.*"),
        ]
        # TODO: pipe in settings
        for glb in self._api.settings("ignore_globs"):
            file_event_handler._ignore_patterns.append(os.path.join(self._dir, glb))

        return file_event_handler

    def _on_file_created(self, event):
        logger.info("file/dir created: %s", event.src_path)
        if os.path.isdir(event.src_path):
            return None
        self._file_count += 1
        # We do the directory scan less often as it grows
        if self._file_count % 100 == 0:
            self.emitter._timeout = int(self._file_count / 100) + 1
        save_name = os.path.relpath(event.src_path, self._dir)
        self._get_file_event_handler(event.src_path, save_name).on_created()

    def _on_file_modified(self, event):
        logger.info("file/dir modified: %s", event.src_path)
        if os.path.isdir(event.src_path):
            return None
        save_name = os.path.relpath(event.src_path, self._dir)
        self._get_file_event_handler(event.src_path, save_name).on_modified()

    def _on_file_moved(self, event):
        # TODO: test me...
        logger.info("file/dir moved: %s -> %s", event.src_path, event.dest_path)
        if os.path.isdir(event.dest_path):
            return None
        old_save_name = os.path.relpath(event.src_path, self._dir)
        new_save_name = os.path.relpath(event.dest_path, self._dir)

        # We have to move the existing file handler to the new name
        handler = self._get_file_event_handler(event.src_path, old_save_name)
        self._file_event_handlers[new_save_name] = handler
        del self._file_event_handlers[old_save_name]

        handler.on_renamed(event.dest_path, new_save_name)

    def _get_file_event_handler(self, file_path, save_name):
        """Get or create an event handler for a particular file.

        file_path: the file's actual path
        save_name: its path relative to the run directory (aka the watch directory)
        """
        if save_name not in self._file_event_handlers:
            if 'tfevents' in save_name or 'graph.pbtxt' in save_name:
                # TODO: we want this fanciness?
                pass
            else:
                Handler = PolicyEnd
                for policy, globs in six.iteritems(self._user_file_policies):
                    if policy == "end":
                        continue
                    for g in globs:
                        paths = glob.glob(os.path.join(self._dir, g))
                        if any(save_name in p for p in paths):
                            if policy == "live":
                                Handler = PolicyLive
                            elif policy == "now":
                                Handler = PolicyNow
                self._file_event_handlers[save_name] = Handler(
                    file_path, save_name, self._api, self._file_pusher)
        return self._file_event_handlers[save_name]

    def finish(self):
        self._file_observer._timeout = 0
        self._file_observer._stopped_event.set()
        self._file_observer.join()
        for handler in list(self._file_event_handlers.values()):
            handler.finish()

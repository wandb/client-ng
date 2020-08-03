"""
tensor b watcher.
"""

import os
import threading
import time

import six


class TBWatcher(object):
    def __init__(self, settings, sender=None):
        self._logdirs = {}
        self._settings = settings
        self._sender = sender

    def _calculate_namespace(self, logdir):
        dirs = list(self._logdirs) + [logdir]
        rootdir = os.path.dirname(os.path.commonprefix(dirs))
        if os.path.isfile(logdir):
            filename = os.path.basename(logdir)
        else:
            filename = ""
        # Tensorboard loads all tfevents files in a directory and prepends
        # their values with the path.  Passing namespace to log allows us
        # to nest the values in wandb
        namespace = logdir.replace(filename, "").replace(rootdir, "").strip(os.sep)
        # TODO: revisit this heuristic, it exists because we don't know the
        # root log directory until more than one tfevents file is written to
        if len(dirs) == 1 and namespace not in ["train", "validation"]:
            namespace = None
        return namespace

    def add(self, logdir, save):
        if logdir in self._logdirs:
            return
        namespace = self._calculate_namespace(logdir)

        tbdir_watcher = TBDirWatcher(self, logdir, save, namespace)
        self._logdirs[logdir] = tbdir_watcher
        tbdir_watcher.start()

    def finish(self):
        for tbdirwatcher in six.itervalues(self._logdirs):
            tbdirwatcher.finish()


class TBDirWatcher(object):
    from tensorboard.backend.event_processing import directory_watcher  # type: ignore
    from tensorboard.backend.event_processing import event_file_loader  # type: ignore
    from tensorboard.compat import tf as tf_compat  # type: ignore

    def __init__(self, tbwatcher, logdir, save, namespace):
        self._tbwatcher = tbwatcher
        self._generator = self.directory_watcher.DirectoryWatcher(
            logdir, self._loader(save, namespace), self._is_new_tensorflow_events_file
        )
        self._thread = threading.Thread(target=self._thread_body)
        self._first_event_timestamp = None
        self._shutdown = None

    def start(self):
        self._thread.start()

    def _is_new_tensorflow_events_file(self, path):
        """Checks if a path has been modified since launch and contains tfevents"""
        if not path:
            raise ValueError("Path must be a nonempty string")
        path = self.tf_compat.compat.as_str_any(path)
        is_mod_after_start = (
            os.stat(path).st_mtime >= self._tbwatcher._settings._start_time
        )
        return "tfevents" in os.path.basename(path) and is_mod_after_start

    def _loader(self, save=True, namespace=None):
        """Incredibly hacky class generator to optionally save / prefix tfevent files"""
        _loader_sender = self._tbwatcher._sender

        class EventFileLoader(self.event_file_loader.EventFileLoader):
            def __init__(self, file_path):
                super(EventFileLoader, self).__init__(file_path)
                if save:
                    # TODO: save plugins?
                    logdir = os.path.dirname(file_path)
                    parts = list(os.path.split(logdir))
                    if namespace and parts[-1] == namespace:
                        parts.pop()
                        logdir = os.path.join(*parts)
                    # wandb.save(file_path, base_path=logdir)
                    # TODO(jhr): deal with symlink file since out of files dir
                    # TODO(jhr): need to figure out policy
                    _loader_sender._save_file(file_path)

        return EventFileLoader

    def _thread_body(self):
        """Check for new events every second"""
        while True:
            try:
                for event in self._generator.Load():
                    self.process_event(event)
            except self.directory_watcher.DirectoryDeletedError:
                break
            if self._shutdown:
                break
            else:
                time.sleep(1)

    def process_event(self, event):
        if self._first_event_timestamp is None:
            self._first_event_timestamp = event.wall_time

        if event.HasField("file_version"):
            self.file_version = event.file_version

        if event.HasField("summary"):
            # self.queue.put(Event(event, self.namespace))
            pass

    def finish(self):
        self._shutdown = True
        self._thread.join()

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import logging
import time

from cache import DataMasterCache, DatasetStates


cache = DataMasterCache()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class UpdateCacheEventHandler(LoggingEventHandler):
    def on_moved(self, event):
        super(UpdateCacheEventHandler, self).on_moved(event)
        # update the paths to watch new location. If it's outside of our root path then warn.
        what = 'directory' if event.is_directory else 'file'

    def on_created(self, event):
        super(UpdateCacheEventHandler, self).on_created(event)
        # warn about untracked entry.
        what = 'directory' if event.is_directory else 'file'

    def on_deleted(self, event):
        super(UpdateCacheEventHandler, self).on_deleted(event)
        # deactivate the entry
        what = 'directory' if event.is_directory else 'file'

    def on_modified(self, event):
        super(UpdateCacheEventHandler, self).on_modified(event)
        # set timer. when timer is done, if no more recent entry exists then set file to done.
        what = 'directory' if event.is_directory else 'file'
        if what == 'file':
            new_facts = {'state': DatasetStates.LocalSaved}
            cache.set_facts_for_dataset_from_path(event.src_path, new_facts)


def _main(file_root):
    """ Watch files in our temporary path. """
    
    event_handler = UpdateCacheEventHandler()
    observer = Observer()
    observer.schedule(event_handler, file_root, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':

    default_fileroot = "C:/tmp/play/"  # todo settings

    _main(default_fileroot)
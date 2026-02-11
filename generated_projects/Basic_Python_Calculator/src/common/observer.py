from abc import ABC, abstractmethod

class Observer(ABC):
    """
    Abstract base class for Observer objects.
    Observers register with a Subject and get notified of changes.
    """
    @abstractmethod
    def update(self, subject_data: any):
        """
        Receive update from subject.
        :param subject_data: Data passed by the subject during notification.
        """
        pass

class Subject(ABC):
    """
    Abstract base class for Subject (Observable) objects.
    Subjects maintain a list of observers and notify them of state changes.
    """
    def __init__(self):
        self._observers = []

    def add_observer(self, observer: Observer):
        """
        Attach an observer to the subject.
        :param observer: The Observer object to attach.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        """
        Detach an observer from the subject.
        :param observer: The Observer object to detach.
        """
        self._observers.remove(observer)

    def notify_observers(self, data: any = None):
        """
        Notify all attached observers about an event or state change.
        :param data: Optional data to pass to the observers.
        """
        for observer in self._observers:
            observer.update(data)

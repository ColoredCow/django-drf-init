from abc import ABC, abstractmethod


class StorageService(ABC):
    @abstractmethod
    def upload(self, file_obj, document_id) -> str:
        pass

    @abstractmethod
    def delete(self, document_id) -> None:
        pass

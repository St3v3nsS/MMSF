class Fingerprint:
    _description: str
    _name: str

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    def __init__(self) -> None:
        self._description = "Bypass Fingerprint authentication on both iOS/Android"
        self._name = "fingerprint"
    
    def execute(self, mssf):
        pass
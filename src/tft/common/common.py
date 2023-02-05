from __future__ import annotations


class CaseBlankInsentiveDict(dict):
    @classmethod
    def _k(cls, key):
        return key.lower().strip() if isinstance(key, str) else key

    def __init__(self, *args, **kwargs):
        super(CaseBlankInsentiveDict, self).__init__(*args, **kwargs)
        self._convert_keys()

    def __getitem__(self, key):
        return super(CaseBlankInsentiveDict, self).__getitem__(self.__class__._k(key))

    def __setitem__(self, key, value):
        super(CaseBlankInsentiveDict, self).__setitem__(self.__class__._k(key), value)

    def __delitem__(self, key):
        return super(CaseBlankInsentiveDict, self).__delitem__(self.__class__._k(key))

    def __contains__(self, key):
        return super(CaseBlankInsentiveDict, self).__contains__(self.__class__._k(key))

    def pop(self, key, *args, **kwargs):
        return super(CaseBlankInsentiveDict, self).pop(self.__class__._k(key), *args, **kwargs)

    def get(self, key, *args, **kwargs):
        return super(CaseBlankInsentiveDict, self).get(self.__class__._k(key), *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        return super(CaseBlankInsentiveDict, self).setdefault(self.__class__._k(key), *args, **kwargs)

    def update(self, E={}, **F):
        super(CaseBlankInsentiveDict, self).update(self.__class__(E))
        super(CaseBlankInsentiveDict, self).update(self.__class__(**F))

    def _convert_keys(self):
        for k in list(self.keys()):
            v = super(CaseBlankInsentiveDict, self).pop(k)
            self.__setitem__(k, v)

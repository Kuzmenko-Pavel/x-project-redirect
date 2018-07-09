from collections import defaultdict
from .base import BaseProcessing
from .rg import RgProcessing
from .fb import FbProcessing


class Processing():
    processing_types = defaultdict(lambda: BaseProcessing)
    processing_types['rg'] = RgProcessing
    processing_types['fb'] = FbProcessing

    def __new__(cls, request, *args, **kwargs):
        source = request.match_info.get('source')
        obj = cls.processing_types[source](request, *args, **kwargs)
        return obj

from flask_appbuilder import Model
from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Index, BIGINT, String, Text, Boolean


class TFTAPIItems(Model):
    __tablename__ = 'api_documents_items'
    api_name = Column(String, primary_key=True)
    description = Column(Text)
    effects = Column(Text)
    from_coord = Column(Text)
    icon = Column(Text)
    id = Column(BIGINT)
    name = Column(String)
    unique = Column(Boolean)

class TFTMatchHistories(Model):
    pass



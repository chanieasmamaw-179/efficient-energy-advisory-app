from model import Base
target_metadata = Base.metadata

class model(Base):
    class Config:
        from_attributes = False


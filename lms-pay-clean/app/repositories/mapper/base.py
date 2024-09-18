class BaseOrmMapper:
    @staticmethod
    def to_domain(data):
        if not data:
            return None
        
    @staticmethod
    def to_orm(data):
        if not data:
            return None
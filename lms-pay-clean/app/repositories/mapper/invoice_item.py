from app.model.invoice import InvoiceItemModel, InvoiceReportModel
from app.repositories.orm.invoiceitem import InvoiceItem


class InvoiceItemOrmMapper:
    """
    This class is responsible for mapping the ORM data to the model data and vice versa of table *invoice_item*.
    """
    @staticmethod
    def to_domain(item: InvoiceItem) -> InvoiceItemModel:
        return InvoiceItemModel(
            invoice_id=item.invoice_id,
            course_id=item.course_id,
            author_id=item.author_id,
            amount=item.amount,
            course_name=item.course_name
        )
    
    @staticmethod
    def to_orm(item: InvoiceItemModel) -> InvoiceItem:
        return InvoiceItem(
            invoice_id=item.invoice_id,
            course_id=item.course_id,
            author_id=item.author_id,
            amount=item.amount,
            course_name=item.course_name
        )
    
    @staticmethod
    def to_report_domain(data) -> InvoiceReportModel:
        item = data[0]
        return InvoiceReportModel(
            invoice_id=item.invoice_id,
            course_id=item.course_id,
            author_id=item.author_id,
            amount=item.amount,
            course_name=item.course_name,
            updated_at=data[1]
        )
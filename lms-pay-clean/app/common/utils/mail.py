from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os

from app.model.invoice import InvoiceDetailModel, TransactionModel
from app.setting.setting import settings
from app.setting.template import invoice_template


conf = ConnectionConfig(
    MAIL_USERNAME = settings.mail["username"],
    MAIL_PASSWORD = settings.mail["password"],
    MAIL_FROM = settings.mail["from"],
    MAIL_PORT = 587,
    MAIL_SERVER = settings.mail["server"],
    MAIL_SSL_TLS = False,
    MAIL_STARTTLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    MAIL_FROM_NAME = settings.mail["from_name"]
)

mail = FastMail(conf)

async def send_invoice_mail(invoice: InvoiceDetailModel):
    template = invoice_template
    print(invoice)
    html = template.render(invoice=invoice)
    message = MessageSchema(
        subject=f"Invoice from {settings.mail['from_name']} for #{invoice.invoice_id}",
        recipients=[invoice.client_email],
        body=html,
        subtype="html"
    )

    await mail.send_message(message)

async def main():
    from app.model.invoice import InvoiceDetailModel, CreateInvoiceItemModel, CreateInvoiceModel, CreatePaymentModel
    
    invoice = {
        "invoice_id": "F17442512",
        "client_email": "ngocuoc30102000@gmail.com",
        "raise_date": "2022-01-01",
        "updated_at": "2022-01-01",
        "summary": "Invoice for Python Programming and Web Development",
        "client_id": 1,
        "items": [
            CreateInvoiceItemModel(
                course_id=int(item["id"]),
                course_name=item["course_name"],
                amount=float(item["price"].split("$")[1]),
                author_id=0,
            )
            for item in [
                {
                    "id": "1",
                    "course_name": "Python Programming",
                    "price": "$19.99"
                },
                {
                    "id": "2",
                    "course_name": "Web Development",
                    "price": "$29.99"
                }
            ]
        ],
        "total": float(49.98),
        "payment_method": "Credit Card",
        "payment_info": CreatePaymentModel(
            card_holder="John Doe",
            cvv="123",
            card_number="1234567890123456",
            exp_date="01/25",
            billing_address="123 Main St, New York, NY 10001"
        )
    }
    
    invoice_detail = InvoiceDetailModel(
        **invoice
    )
    await send_invoice_mail(invoice_detail)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

